#!/usr/bin/env python3
"""Add 8 new tactical systems to the football tactics database"""
import json

with open('data/tactics_database.json', 'r') as f:
    d = json.load(f)

existing_ids = {t['id'] for t in d['tactical_systems']}

new_tactics = [
    {
        "id": "brazilian_joga",
        "name": "巴西桑巴足球",
        "name_en": "Brazilian Samba Football",
        "era": "1958-1970",
        "origin": "巴西",
        "formation": "4-2-4 / 4-3-3",
        "philosophy": "个人天赋+即兴创造+快乐足球",
        "key_innovation": "将足球从战术纪律解放为艺术表达",
        "desc_short": "桑巴节奏下的个人天赋秀",
        "desc_full": "巴西足球黄金时代，以个人天赋和即兴创造为核心。加林查的变向过人、贝利的身体欺骗、迪迪的落叶球。1970年巴西队被认为是史上最伟大的球队。",
        "tags": ["个人天赋", "即兴创造", "快乐足球", "1v1突破"],
        "stats": {"possession": 6, "defense": 3, "pressing": 3, "creativity": 10, "speed": 7, "organization": 4},
        "players_per_side": 11,
        "field_type": "标准场",
        "goal_type": "标准球门",
        "players": [
            {"x": 0, "z": -45, "color": "#ffcc00", "label": "GK", "role": "门将"},
            {"x": -20, "z": -28, "color": "#22aa44", "label": "LB", "role": "左后卫"},
            {"x": -7, "z": -30, "color": "#22aa44", "label": "CB1", "role": "中卫"},
            {"x": 7, "z": -30, "color": "#22aa44", "label": "CB2", "role": "中卫"},
            {"x": 20, "z": -28, "color": "#22aa44", "label": "RB", "role": "右后卫"},
            {"x": -10, "z": -12, "color": "#ff8c00", "label": "DM", "role": "后腰"},
            {"x": 10, "z": -12, "color": "#ff8c00", "label": "CM", "role": "中场"},
            {"x": -25, "z": 8, "color": "#ffdd00", "label": "RW", "role": "右边锋"},
            {"x": -5, "z": 15, "color": "#ffdd00", "label": "CF", "role": "中锋"},
            {"x": 10, "z": 12, "color": "#ffdd00", "label": "SS", "role": "影锋"},
            {"x": 25, "z": 8, "color": "#ffdd00", "label": "LW", "role": "左边锋"}
        ],
        "passing_triangles": [[5,7],[5,9],[6,10],[7,8],[8,9],[9,10]],
        "movement_paths": [[7,8],[9,10],[8,9]]
    },
    {
        "id": "soviet_press",
        "name": "苏联高压足球",
        "name_en": "Soviet Pressing Football",
        "era": "1970s-1980s",
        "origin": "苏联/东欧",
        "formation": "4-4-2 (高位)",
        "philosophy": "体能碾压+集体压迫+快速转换",
