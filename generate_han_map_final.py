#!/usr/bin/env python3
"""2.png — 历史记载汉族最大控制区域并集"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely.ops import unary_union
import os, sys

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

GEO = r'C:\Users\Administrator\.geodata'
OUTPUT = r'C:\Users\Administrator\Desktop\2.png'

# ── 字体 ──────────────────────────────────────────────
cn_f = cn_t = cn_s = cn_l = None
for fp in [r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simhei.ttf']:
    if os.path.exists(fp):
        cn_f = FontProperties(fname=fp, size=10)
        cn_t = FontProperties(fname=fp, size=18)
        cn_s = FontProperties(fname=fp, size=5.5)
        cn_l = FontProperties(fname=fp, size=10)
        break

world = gpd.read_file(os.path.join(GEO, 'ne_110m_admin_0_countries.shp'))
world = world[world['CONTINENT'] != 'Antarctica'].copy()

# 湖泊和河流 (真实形状)
lakes = gpd.read_file(os.path.join(GEO, 'ne_110m_lakes.shp'))
rivers = gpd.read_file(os.path.join(GEO, 'ne_110m_rivers_lake_centerlines.shp'))
# 筛选主要河流 (NE 110m 仅有 Chang/Yangtze/Mekong/Brahmaputra)
major_rivers = rivers[rivers['name'].isin(['Chang', 'Yangtze', 'Mekong', 'Brahmaputra'])]

# 黄河不在110m数据中, 手动添加近似线
yellow_river = gpd.GeoDataFrame({
    'geometry': [LineString([
        (96,35),(100,36),(104,37),(108,38),(111,39),(114,37),(117,35),(119,34)
    ])],
    'name': ['Yellow River']
}, crs='EPSG:4326')

# ═══════════════════════════════════════════════════════
# 历史记载汉族最大控制区域并集多边形
# 西汉: 西域都护府 + 乐浪四郡(平壤) + 交趾九真日南(顺化)
# 唐:   安西/北庭(楚河-费尔干纳-巴尔喀什东) + 安北(贝加尔以南)
# 明:   奴儿干都司(黑龙江-库页岛海岸)
# ═══════════════════════════════════════════════════════
h = [
    # ── 日南郡 (汉最南, 今越南顺化 ~17N) ──
    (108.0, 16.5), (107.0, 17.5), (106.5, 20.0),
    # ── 交趾/九真 → 云南 → 缅甸北部 (明三宣六慰) ──
    (105.0, 22.0), (100.0, 21.5), (98.0, 24.0), (97.0, 27.0),
    # ── 吐蕃东部边缘 (唐羁縻) ──
    (96.0, 30.0), (92.0, 32.0), (88.0, 33.5),
    # ── 西域都护府/安西都护府 西界 ──
    (74.0, 37.5),  # 葱岭/帕米尔东麓
    (73.0, 39.5),  # 碎叶/楚河流域
    (75.0, 41.5), (77.0, 43.0),  # 费尔干纳盆地东缘
    (79.0, 44.5), (80.5, 46.0),  # 巴尔喀什湖以东
    # ── 阿尔泰山 → 杭爱山 (唐北庭/安北) ──
    (83.0, 47.0), (85.0, 48.5),
    (88.0, 49.5), (92.0, 50.0),
    # ── 贝加尔湖以南 (唐安北都护府最大范围 ~52N) ──
    (98.0, 51.0), (104.0, 52.0), (108.0, 51.5),
    # ── 肯特山东 → 鄂嫩河 → 黑龙江上游 (北界降至~50N) ──
    (112.0, 50.0), (116.0, 49.0),
    (120.0, 48.5), (125.0, 48.0),
    # ── 黑龙江中下游 (明奴儿干都司) ──
    (130.0, 49.0), (134.0, 48.5),
    # ── 库页岛海岸 (明奴儿干都司 囊哈儿卫) ──
    (140.0, 50.0), (143.0, 51.0), (144.0, 49.0), (142.0, 47.0),
    # ── 滨海边疆区 → 朝鲜半岛 ──
    (140.0, 44.0), (137.0, 42.5),
    (131.0, 42.0), (130.0, 38.5), (129.0, 36.0), (128.0, 34.5),
    # ── 东海 → 台湾 → 南海 ──
    (127.0, 33.0), (122.0, 31.0), (121.5, 25.0), (120.0, 22.0),
    (118.0, 18.0), (115.0, 12.0), (110.0, 16.0), (108.0, 16.5),
]
han_poly = Polygon(h)

# ── 国别分类 (交集>2% → 汉控) ────────────────────────
world['category'] = 'other'
for idx, row in world.iterrows():
    if row.geometry.intersects(han_poly):
        if row.geometry.intersection(han_poly).area / row.geometry.area > 0.02:
            world.at[idx, 'category'] = 'han'

# 俄罗斯/哈萨克斯坦: 整国不标红, 但历史控制的小块区域单独添加
# 从国别分类中移除俄/哈 (太大了)
world.loc[world['SOVEREIGNT'].isin(['Russia','Kazakhstan']), 'category'] = 'other'

# 俄远东省份 + 哈东南部 (裁剪到历史多边形内)
from shapely.geometry import box as sbox_poly
admin1 = gpd.read_file(os.path.join(GEO, '50m_admin1', 'ne_50m_admin_1_states_provinces.shp'))
rfe = admin1[(admin1['admin']=='Russia') & (admin1['name'].isin(['Primor\'ye','Khabarovsk','Sakhalin','Amur','Yevrey']))].copy()
rfe['geometry'] = rfe.geometry.intersection(han_poly)
rfe = rfe[~rfe.geometry.is_empty]
extra_red = list(rfe.geometry)  # 俄远东省份裁剪到历史边界

# 哈萨克斯坦东南部 (巴尔喀什湖以东, 唐北庭都护府)
kz_se = Polygon([(76,44),(79,47),(82,46),(80,44),(78,43),(76,43),(76,44)])
kz_clip = kz_se.intersection(han_poly).intersection(world[world['SOVEREIGNT']=='Kazakhstan'].geometry.unary_union)
if not kz_clip.is_empty:
    extra_red.append(kz_clip)

han_land = unary_union(list(world[world['category']=='han'].geometry) + extra_red)
maritime_base = han_poly.buffer(2.0).difference(han_land.buffer(0.05))  # 缩小buffer, 不过度延伸

# 裁剪领海: 鄂霍次克海/白令海/东太平洋非汉控海域
maritime_clip = sbox(-180,-58, 146, 53)  # 东146°E以东、北53°N以北不显示
maritime_base = maritime_base.intersection(maritime_clip)

# 补充: 南海完整范围 (含南沙/西沙/中沙 + 马六甲海峡)
scs = Polygon([
    (105,22),(112,22),(118,20),(120,17),(120,12),(119,9),(118,7),
    (116,5),(114,4),(112,4),(109,5),(107,7),(105,12),(105,18),(105,22)
])
# 郑和下西洋领海 (孟加拉湾+阿拉伯海+东非沿岸)
zhenghe_sea = Polygon([
    (78,22),(98,22),(98,0),(108,4),(115,3),(115,-12),(98,-8),(75,-5),
    (48,-2),(38,3),(38,22),(48,28),(78,22)
])
# 东南亚领海 (马六甲海峡+爪哇海+暹罗湾+苏禄海)
se_asia_sea = Polygon([
    (96,0),(106,-2),(110,-5),(115,-6),(120,-3),(120,2),(115,5),
    (110,10),(108,12),(105,12),(102,8),(98,5),(96,0)
])
maritime = unary_union([maritime_base, scs, zhenghe_sea, se_asia_sea])
# 移除所有陆地 (全球陆地mask), 仅保留海洋部分
land_all_mask = unary_union(world.geometry)
maritime = maritime.difference(land_all_mask.buffer(0.1))
# 裁剪到有效范围 (东146°, 北53°)
maritime = maritime.intersection(sbox(-175,-58,146,53))

# ── 东南亚12领地 (自然形状多边形, 非方块) ──────────────
sea_t = [
    # 吞武里王朝 — 湄南河三角洲不规则区域
    (Polygon([(100.2,13.7),(100.5,13.5),(100.7,13.6),(100.6,13.9),(100.4,14.0),(100.1,13.9)]), '吞武里王朝(曼谷)'),
    # 吴氏宋卡 — 宋卡湖周边
    (Polygon([(100.2,7.1),(100.5,6.9),(100.8,7.1),(100.8,7.4),(100.5,7.6),(100.3,7.4)]), '吴氏宋卡'),
    # 旧港宣慰司 — 穆西河三角洲 (苏门答腊东南)
    (Polygon([(104.5,-3.2),(105.0,-3.5),(105.5,-3.2),(105.3,-2.6),(104.8,-2.5),(104.3,-2.8)]), '旧港宣慰司(巨港)'),
    # 兰芳共和国 — 西加里曼丹坤甸 (卡普阿斯河流域)
    (Polygon([(109.0,-0.3),(109.8,-0.8),(110.8,-0.3),(110.5,0.5),(109.8,1.0),(109.0,0.5)]), '兰芳共和国(坤甸)'),
    # 戴燕王国 — 西加里曼丹内陆
    (Polygon([(111.2,0.3),(111.8,0.1),(112.5,0.5),(112.2,1.0),(111.5,1.3),(111.0,0.8)]), '戴燕王国'),
    # 和顺公司 — 西加里曼丹矿区
    (Polygon([(109.2,0.3),(109.7,0.1),(110.0,0.5),(109.7,1.0),(109.3,1.0),(109.0,0.7)]), '和顺公司'),
    # 黄森屏政权 — 文莱/北婆罗洲沿岸
    (Polygon([(114.2,4.5),(115.0,4.3),(115.5,4.7),(115.3,5.3),(114.5,5.5),(114.0,5.0)]), '黄森屏政权(文莱)'),
    # 顺塔国 — 西爪哇万丹/雅加达
    (Polygon([(105.5,-7.2),(106.3,-7.5),(107.2,-7.0),(107.0,-6.2),(106.2,-6.0),(105.5,-6.5)]), '顺塔国(爪哇)'),
    # 飞龙国 — 柔佛/新加坡
    (Polygon([(103.5,1.2),(104.0,1.1),(104.5,1.3),(104.3,1.8),(103.8,2.0),(103.4,1.6)]), '飞龙国(柔佛)'),
    # 纳吐纳张氏 — 纳吐纳群岛
    (Polygon([(108.0,3.5),(108.8,3.3),(109.5,3.6),(109.3,4.2),(108.5,4.5),(108.0,4.0)]), '纳吐纳张氏'),
    # 河仙镇 — 湄公河三角洲西端
    (Polygon([(104.3,10.2),(104.7,10.1),(105.0,10.3),(104.9,10.7),(104.5,10.7),(104.2,10.5)]), '河仙镇'),
    # 吉隆坡甲必丹 — 巴生河谷
    (Polygon([(101.5,3.0),(101.8,2.9),(102.0,3.1),(101.9,3.4),(101.6,3.4),(101.4,3.2)]), '吉隆坡甲必丹'),
]

# ═══════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(36,18), dpi=120)
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

ax.add_patch(plt.matplotlib.patches.Polygon(
    [(-175,-58),(180,-58),(180,82),(-175,82)],
    facecolor='#1a3a5c', edgecolor='none', zorder=0))

# 灰色: 非汉控国家
world[world['category']=='other'].plot(ax=ax, color='#909090', edgecolor='#666666', linewidth=0.2, zorder=1)

# 红色: 汉控国家整国标红
world[world['category']=='han'].plot(ax=ax, color='#CC2222', edgecolor='none', linewidth=0, zorder=2)

# 俄远东 + 哈东南 (裁剪到历史边界, 仅小块)
for geom in extra_red:
    gpd.GeoDataFrame({'geometry':[geom]}, crs='EPSG:4326').plot(
        ax=ax, color='#CC2222', edgecolor='none', linewidth=0, zorder=2)

# 领海
gpd.GeoDataFrame({'geometry':[maritime]}, crs='EPSG:4326').plot(
    ax=ax, color='#E87070', alpha=0.22, edgecolor='none', linewidth=0, zorder=0.5)

# 郑和下西洋领海标注
fig.text(0.62, 0.48, '郑和下西洋领海', fontproperties=cn_f, color='#ffaaaa', fontsize=9, rotation=-20)
fig.text(0.62, 0.44, '（印度洋—东非沿岸）', fontproperties=cn_s, color='#ffaaaa', fontsize=7, rotation=-20)

# 真实湖泊 (Natural Earth)
lakes.plot(ax=ax, color='#3377bb', edgecolor='#5599cc', linewidth=0.1, zorder=3, alpha=0.85)

# 真实河流 (长江/湄公河/雅鲁藏布江)
major_rivers.plot(ax=ax, color='#5599cc', linewidth=0.5, zorder=3, alpha=0.7)

# 黄河 (手动, 不在110m数据中)
yellow_river.plot(ax=ax, color='#5599cc', linewidth=0.5, zorder=3, alpha=0.7)

# 河流标注
river_labels = [
    (105,35,'黄河'), (112,31,'长江'), (106,15,'湄公河'),
    (90,28,'雅鲁藏布江'),
]
for rx, ry, rn in river_labels:
    ax.annotate(rn, (rx, ry), fontproperties=cn_s, color='#88bbdd', fontsize=5.5,
                ha='center', va='center', rotation=15, zorder=6)

# 南海诸岛标记 (仅星标, 无文字)
for sx, sy in [(116.7,20.7),(112.3,16.5),(115.5,15.5),(114.5,8.5),(117.8,15.1)]:
    ax.plot(sx, sy, marker='*', color='#ff3333', markersize=8, zorder=5)

# 东南亚12领地 (仅圆点, 无文字)
for sx, sy in [(100.4,13.7),(100.6,7.2),(105.2,-3.0),(110.0,0.2),(111.8,0.8),
               (109.5,0.6),(115.0,5.0),(106.5,-7.0),(103.8,1.4),(108.5,3.8),
               (104.5,10.4),(101.7,3.15)]:
    ax.plot(sx, sy, marker='o', color='#ff4444', markersize=4, zorder=5)

ax.set_xlim(-175,180); ax.set_ylim(-58,82); ax.axis('off')

# ── 精美小地图 (左下, 美洲上空, 专业制图风格) ────────
# 白色底卡 + 阴影 + 双线框
from matplotlib.patches import FancyBboxPatch, Rectangle
shadow = fig.add_axes([0.077, 0.047, 0.32, 0.48])
shadow.set_facecolor('#0a0a15'); shadow.axis('off')

panel = fig.add_axes([0.075, 0.045, 0.32, 0.48])
panel.set_facecolor('#f0f0e8'); panel.set_xlim(0,1); panel.set_ylim(0,1); panel.axis('off')
for sp in panel.spines.values():
    sp.set_color('#888888'); sp.set_linewidth(0.5); sp.set_visible(True)

# 地图本体
ax_se = fig.add_axes([0.085, 0.055, 0.30, 0.46])
ax_se.set_facecolor('#d8e8f0')  # 浅蓝海
ax_se.set_xlim(95,120); ax_se.set_ylim(-10,15)

# 陆地浅灰
world.plot(ax=ax_se, color='#c8c8c0', edgecolor='#999999', linewidth=0.15, zorder=1)

# 南海诸岛标记 (在 inset 也可见范围内)
scs_islands = [(112.5,9.0),(114.5,11.0),(116.5,12.5)]  # 南沙/中沙/黄岩岛大致位置
for sx, sy in scs_islands:
    ax_se.scatter(sx, sy, s=4, color='#e83030', zorder=4)

land_all = unary_union(world.geometry)

for poly, name in sea_t:
    try:
        lp = poly.intersection(land_all)
        target = lp if not lp.is_empty else poly
    except:
        target = poly
    gpd.GeoDataFrame({'geometry':[target]}, crs='EPSG:4326').plot(
        ax=ax_se, color='#d42020', edgecolor='#881111', linewidth=0.3, zorder=3, alpha=0.82)
    c = poly.centroid
    ax_se.annotate(name, (c.x, c.y), fontproperties=cn_s, color='#333333', fontsize=4.5,
                   ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.85,
                             edgecolor='#cc4444', linewidth=0.4), zorder=6)

# 内边框
for sp in ax_se.spines.values():
    sp.set_color('#444444'); sp.set_linewidth(1.0); sp.set_visible(True)

# 小地图标题
fig.text(0.235, 0.515, '海外政权（东南亚）',
         fontproperties=cn_f, color='white', ha='center', fontsize=9)

# ── 标题 ──────────────────────────────────────────────
fig.text(0.5,0.955, '汉族最高统治者历史控制区域叠加示意图',
         fontproperties=cn_t, color='white', ha='center', fontsize=18)

leg = ax.legend(handles=[
    mpatches.Patch(facecolor='#CC2222', label='历史控制区域'),
    mpatches.Patch(facecolor='#E87070', alpha=0.25, label='历史领海'),
    mpatches.Patch(facecolor='#909090', label='其他地区'),
], loc='lower left', fontsize=9, facecolor='#2a2a3e', edgecolor='#444466',
   framealpha=0.9, borderpad=0.6, prop=cn_l)
leg.get_frame().set_linewidth(0.5)
for txt in leg.get_texts(): txt.set_color('white')

fig.text(0.5,0.008,
         '注：汉族最高统治者历史控制区域叠加 + 16个海外政权（左下小地图）。边界为近似示意，仅供历史参考。',
         fontproperties=cn_f, ha='center', fontsize=7, color='#888888')

fig.savefig(OUTPUT, dpi=120, bbox_inches='tight', facecolor='#1a1a2e', pad_inches=0.3)
plt.close(fig)
print('OK')
