#!/usr/bin/env python3
"""
升级版3D战术示意图 - 14种战术体系完整版
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json

BG_COLOR = '#0a0e1a'
PITCH_COLOR = '#1a5c2a'
PITCH_LINE = '#3da35d'
TEXT_COLOR = '#ffffff'

# Load database
with open('/root/.coze/agents/7646924251471020315/workspace/football-tactics-3d/data/tactics_database.json') as f:
    db = json.load(f)

systems = db['tactical_systems']

# Create a 5x3 grid of 3D pitch diagrams
fig = plt.figure(figsize=(30, 22), facecolor=BG_COLOR)
fig.suptitle('⚽ 足球踢法3D战术全景 — 14种体系完整版\nFootball Tactical Systems 3D Panorama', 
             color=TEXT_COLOR, fontsize=22, fontweight='bold', y=0.98)

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def draw_pitch_3d(ax, title, subtitle=''):
    ax.set_facecolor(BG_COLOR)
    pitch_x = [0, 100, 100, 0, 0]
    pitch_y = [0, 0, 70, 70, 0]
    ax.plot(pitch_x, pitch_y, [0]*5, color=PITCH_LINE, linewidth=1, alpha=0.6)
    verts = [list(zip([0,100,100,0], [0,0,70,70], [0,0,0,0]))]
    pitch_poly = Poly3DCollection(verts, alpha=0.5, facecolor=PITCH_COLOR, edgecolor=PITCH_LINE)
    ax.add_collection3d(pitch_poly)
    ax.plot([50, 50], [0, 70], [0, 0], color=PITCH_LINE, linewidth=0.5, alpha=0.3)
    theta = np.linspace(0, 2*np.pi, 30)
    ax.plot(50 + 7*np.cos(theta), 35 + 5*np.sin(theta), [0]*30, color=PITCH_LINE, linewidth=0.5, alpha=0.3)
    ax.set_title(title, color=TEXT_COLOR, fontsize=9, fontweight='bold', pad=2)
    if subtitle:
        ax.text2D(0.5, 0.01, subtitle, transform=ax.transAxes, color='#8899aa', fontsize=6, ha='center')
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 75)
    ax.set_zlim(-3, 18)
    ax.view_init(elev=28, azim=-55)
    ax.axis('off')

for idx, sys in enumerate(systems):
    row = idx // 5
    col = idx % 5
    ax = fig.add_subplot(3, 5, row*5+col+1, projection='3d')
    
    title = f'{sys["name"]}\n{sys["name_en"]}'
    subtitle = f'{sys["era"]} · {sys["formation"]} · {sys["origin"]}'
    draw_pitch_3d(ax, title, subtitle)
    
    # Draw players
    color_map = {
        '#ffcc00': '#ffcc00', '#44cc88': '#44cc88', '#ff8c00': '#ff8c00',
        '#ff4444': '#ff4444', '#00ddff': '#00ddff', '#00aaff': '#00aaff',
        '#ddaa00': '#ddaa00', '#cc44ff': '#cc44ff', '#dd44ff': '#dd44ff'
    }
    
    for p in sys['players']:
        color = p.get('color', '#ffffff')
        x = p['x'] + 50  # Center on pitch
        z = p['z'] + 35
        ax.scatter([x], [z], [0.5], c=color, s=60, edgecolors='white', linewidth=0.3, depthshade=False, alpha=0.9)
        ax.text(x, z, 2.5, p['label'], color='white', fontsize=4, ha='center', va='bottom', fontweight='bold')
    
    # Draw passing triangles
    for tri in sys.get('passing_triangles', []):
        pts = [sys['players'][i] for i in tri]
        tri_x = [p['x']+50 for p in pts] + [pts[0]['x']+50]
        tri_z = [p['z']+35 for p in pts] + [pts[0]['z']+35]
        ax.plot(tri_x, tri_z, [0.3]*4, color='#00ddff', linewidth=0.5, alpha=0.3)
    
    # Draw movement paths
    for path in sys.get('movement_paths', []):
        p1, p2 = sys['players'][path[0]], sys['players'][path[1]]
        ax.plot([p1['x']+50, p2['x']+50], [p1['z']+35, p2['z']+35], [0.5, 0.5], 
                color='#cc44ff', linewidth=0.8, alpha=0.5, linestyle='--')
    
    # Stats bar at bottom
    stats = sys['stats']
    stat_text = '  '.join([f'{k[0].upper()}{v}' for k, v in stats.items()])
    ax.text2D(0.5, -0.02, stat_text, transform=ax.transAxes, color='#667788', fontsize=5, ha='center')

# Bottom legend
fig.text(0.5, 0.01, 
         '🟡门将  🟢后卫  🟠中场  🔴前锋  🔵清道夫/翼卫  🟣组织核心  △传球三角  --跑位路线\n'
         'P=控球 D=防守 Pr=压迫 C=创造 S=速度 O=组织',
         ha='center', color='#556677', fontsize=10)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('/root/.coze/agents/7646924251471020315/workspace/football-tactics-3d/assets/images/14体系3D全景.png', 
            dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
print("✅ 14体系3D全景图已生成")
