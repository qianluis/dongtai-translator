#!/usr/bin/env python3
"""Update tactics database with World Cup 2026 Day 2 results."""
import json

DB_PATH = "data/tactics_database.json"

with open(DB_PATH) as f:
    db = json.load(f)

# New Day 2 matches (June 15, 2026)
new_matches = [
    {
        "date": "2026-06-15",
        "home": "Spain",
        "away": "Cape Verde",
        "score": "0-0",
        "group": "H",
        "venue": "Mercedes-Benz Stadium, Atlanta",
        "attendance": 67640,
        "tactical_summary": "西班牙控球主导但无法突破佛得角密集防守。40岁门将Vozinha表现神勇多次扑救。佛得角采用5-4-1低位防守阵型展现小国足球的防守纪律性。这是世界杯历史上最大冷门之一人口不足50万的岛国逼平夺冠热门西班牙。",
        "tactical_en": "Spain dominated possession but couldn't break Cape Verde low block. 40-year-old GK Vozinha outstanding. Cape Verde used disciplined 5-4-1 defensive shape. One of biggest shocks in WC history - nation of 500k people held tournament favourites Spain.",
        "key_tactics": ["5-4-1低