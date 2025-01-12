import os 
import json 
import urllib.request
import boto3
from datetime import datetime, timezone, timedelta

def format_game_data (game):
  status = game.get ("Status", "Unknown")
  away_team = game.get ("AwayTeam", "Unknown")
  home_team = game.get ("HomeTeam", "Unknown")
  final_score = f"{game.get ('AwayTeamScore', 'N/A')}-{game.get ('HomeTeamScore', 'N/A' )}"
  start_time = game.get ("DateTime", "Unknown")
  channel = game.get ("Channel", "Unknown" )
  # Format quarters
  quarters = game.get("Quarters", [])
  quarter_scores = ','.join ( [f"Qfa|'Number'|): {q.get ('AwayScore', "N/A")}-{q.get ('HomeScore', 'N/A')}" for q in quarters])
  # Create the game string
  if status == "Final":
    return(
      f"Game Status: {status}\n" 
      f"(away_team) vs {home_team}\n" 
      f"Final Score: {final_score}\n" 
      f"Start Time: {start_time}\n" 
      f"Channel: {channel}\n"
      f"Quarter Scores: {quarter_scores}\n"
  )
  elif status == "InProgress":
    last_play = game.get ("LastPlay", "N/A")
    return(
    f"Game Status: {status}\n"
    f"{away_team} vs {home_team}\n" 
    f"Current Score: {final_score}\n"
    f"Last Play: {last_play}\n" 
    f"Channel: {channel}\n"
    )
  else:
    return(
      f"Game Status: {status}\n"
      f"{away_team} vs {home_team}\n"
      f"Details are unavailable at the moment.\n"
      )

def lambda_handler(event, context):
  #get environment variables
  api_key = os.environ.get("API_KEY")
  sns_topic = os.environ.get("SNS_TOPIC_ARN")
  sns_client = boto3.client("sns")
  
  #get the current date
  utc_now = datetime.now(timezone.utc)
  central_time = utc_now - timedelta(hours=6)
  today_date = central_time.strftime ("%Y-%m-%d")
  
  print(f"Today's date: {today_date}")
  
  #get the game data
  api_url = f"https://api.sportsdata.io/v3/nba/scores/json/GamesByDate/{today_date}?key={api_key}"
  try:
    with urllib.request.urlopen(api_url) as response:
      game_data = json.loads(response.read().decode())
  except Exception as e:
    print(f"An error occurred: {e}")
    return {
      "statusCode": 500,
      "body": json.dumps("An error occurred while fetching the game data.")
    }
  
  #format the game data
  formatted_games = [format_game_data(game) for game in game_data]
  final_message = "\n\n".join(formatted_games)
  
  #publish the message to the SNS topic
  try:
      sns_client.publish(
      TopicArn=sns_topic, 
      Message=final_message,
      Subject="Today's NBA Games"
      )
      print("Message published successfully.")
      
  except Exception as e:
    print(f"An error occurred: {e}")
    return {
      "statusCode": 500,
      "body": json.dumps("An error occurred while publishing the message.")
    }
    
  return {
    "statusCode": 200,
    "body": json.dumps("Message published successfully.")
    }
  