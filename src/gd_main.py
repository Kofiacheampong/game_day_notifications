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
      f"Quarter Scores: {quarter_score