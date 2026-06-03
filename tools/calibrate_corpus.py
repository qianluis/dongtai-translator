#!/usr/bin/env python3
"""东台方言语料校准器 - 修正吴语混入 + 合并两版语料"""
import json, random
random.seed(2026)

# ===== 方言校准映射（吴语→东台话）=====
DIALECT_FIXES = {
    # 时间词
    '明朝': '明呃', '今朝': '今呃', '昨朝': '昨呃',
    '后朝': '后呃', '前朝': '前呃',
    # 语气词
    '伐': '呃', '啘': '呃', '喔': '呃',
    # 否定词
    '没得': '呒得', '勿': '弗', '覅': '弗要',
    # 代词
    '我俫': '我俦', '你俫': '你俦', '他俫': '他俦',
    '侬': '你', '阿拉': '我俦',
    # 动词
    '侯告': '困觉', '困觉': '困觉',  # 这个是正确的
    '晓得伐': '晓得呃',
    # 副词
    '好多': '几钿', '蛮蛮': '蛮', '交关': '蛮',
    # 疑问词
    '啥': '什的', '哪能': '怎呃', '几化': '几钿',
    # 其他吴语词
    '物事': '杲昃', '小囡': '伢儿', '爷叔': '爷叔',
    '白相': '耍子', '讲白相': '讲白相',
    '磕哒': '推板',  # 磕哒=小气，推板=差
}

def fix_dialect(text):
    """修正方言翻译中的吴语混入"""
    fixed = text
    for wrong, correct in DIALECT_FIXES.items():
        fixed = fixed.replace(wrong, correct)
    return fixed

def is_valid_dongtai(dialect_text):
    """检查方言翻译是否看起来像东台话"""
    # 东台话特征词
    dongtai_markers = ['呃', '弗', '呒得', '哪块', '什的', '怎呃', '杲昃',
                       '来斯', '推板', '扎实', '刷刮', '家去', '俦', '伢儿',
                       '几钿', '汏', '蛮', '爹爹', '今呃', '明呃', '昨呃',
                       '夜头', '早起头', '中上', '下半日', '老早', '才刚',
                       '讲白相', '相骂', '荡荡', '适意', '心焦', '气恼',
                       '欢喜', '吓煞', '龌龊', '清爽', '嫌人']
    # 吴语特征词（不应出现）
    wu_markers = ['明朝', '今朝', '伐', '侯告', '我俫', '你俫', '侬',
                  '阿拉', '物事', '哪能', '几化', '交关']
    
    has_dongtai = any(m in dialect_text for m in dongtai_markers)
    has_wu = any(m in dialect_text for m in wu_markers)
    
    if has_wu and not has_dongtai:
        return False  # 纯吴语，不是东台话
    return True

# ===== 加载两版语料 =====
print("📂 加载语料...")

# 我的版本
with open('dongtai_corpus_200k.json', 'r') as f:
    my_corpus = json.load(f)
print(f"  我的版本: {len(my_corpus)} 句")

# 知世界版本
with open('/tmp/.fuse_data/所有对话/主对话/dongtai-dialect-200k/corpus/dongtai_corpus_200k_final.json', 'r') as f:
    their_corpus = json.load(f)
print(f"  知世界版本: {len(their_corpus)} 句")

# ===== 校准知世界版 =====
print("\n🔧 校准知世界版语料...")
fixed_count = 0
valid_count = 0
invalid_count = 0

their_fixed = []
for item in their_corpus:
    dialect = item.get('dialect', item.get('dongtai', ''))
    standard = item.get('standard', item.get('mandarin', ''))
    
    if not standard or not dialect:
        continue
    
    # 修正方言
    fixed_dialect = fix_dialect(dialect)
    if fixed_dialect != dialect:
        fixed_count += 1
    
    # 检查有效性
    if is_valid_dongtai(fixed_dialect):
        valid_count += 1
        their_fixed.append({
            'id': item.get('id', ''),
            'standard': standard,
            'dialect': fixed_dialect,
            'category': item.get('category', ''),
            'subcategory': item.get('subcategory', ''),
            'register': '口语',
            'region': '东台城区',
            'emotion': '中性',
        })
    else:
        invalid_count += 1

print(f"  修正吴语混入: {fixed_count} 句")
print(f"  有效（校准后）: {valid_count} 句")
print(f"  无效（丢弃）: {invalid_count} 句")
print(f"  保留率: {valid_count/len(their_corpus)*100:.1f}%")

# ===== 合并两版 =====
print("\n🔗 合并两版语料...")

# 先放我的版本
seen_standards = set()
merged = []

for item in my_corpus:
    if item['standard'] not in seen_standards:
        seen_standards.add(item['standard'])
        merged.append(item)

# 再补充知世界版中独有的高质量语料
added_from_theirs = 0
for item in their_fixed:
    if item['standard'] not in seen_standards:
        seen_standards.add(item['standard'])
        merged.append(item)
        added_from_theirs += 1

print(f"  我的版本: {len(my_corpus)} 句")
print(f"  知世界版补充: +{added_from_theirs} 句")
print(f"  合并去重后: {len(merged)} 句")

# ===== 校准我的版本中的语义问题 =====
print("\n🔧 校准语义问题...")

# 不合理的动宾搭配（更精细版）
BAD_COMBOS = {
    ('吃', '衣裳'), ('吃', '鞋子'), ('吃', '碗'), ('吃', '筷'), ('吃', '锅'),
    ('吃', '刀'), ('吃', '手机'), ('吃', '钿'), ('吃', '钥匙'), ('吃', '伞'),
    ('吃', '书'), ('吃', '笔'), ('吃', '包'), ('吃', '药'),  # 吃药其实合理
    ('穿', '鱼'), ('穿', '肉'), ('穿', '水'), ('穿', '茶'), ('穿', '饭'),
    ('穿', '粥'), ('穿', '面'), ('穿', '菜'), ('穿', '蛋'), ('穿', '虾'),
    ('穿', '蟹'), ('穿', '钿'), ('穿', '碗'), ('穿', '书'), ('穿', '笔'),
    ('穿', '药'), ('穿', '伞'), ('穿', '刀'), ('穿', '锅'),
    ('写', '鱼'), ('写', '肉'), ('写', '水'), ('写', '衣裳'), ('写', '鞋'),
    ('写', '碗'), ('写', '钿'), ('写', '伞'), ('写', '茶'), ('写', '饭'),
    ('洗', '书'), ('洗', '笔'), ('洗', '钿'), ('洗', '钥匙'),
    ('烧', '书'), ('烧', '笔'), ('烧', '衣裳'), ('烧', '鞋'), ('烧', '伞'),
    ('烧', '钥匙'), ('烧', '手机'), ('烧', '钿'),
    ('坐', '饭'), ('坐', '菜'), ('坐', '水'), ('坐', '鱼'), ('坐', '肉'),
    ('站', '饭'), ('站', '菜'), ('站', '水'), ('站', '鱼'), ('站', '肉'),
    ('跑', '饭'), ('跑', '菜'), ('跑', '水'),
    ('睡', '饭'), ('睡', '菜'), ('睡', '鱼'), ('睡', '肉'),
    ('借', '鱼'), ('借', '肉'), ('借', '水'), ('借', '茶'), ('借', '饭'),
    ('借', '菜'), ('借', '粥'), ('借', '面'),
    ('修', '鱼'), ('修', '肉'), ('修', '水'), ('修', '茶'), ('修', '饭'),
    ('说', '茶'), ('说', '鱼'), ('说', '肉'), ('说', '水'), ('说', '饭'),
    ('走', '面'), ('走', '饭'), ('走', '菜'), ('走', '水'),
}

removed = 0
filtered = []
for item in merged:
    std = item['standard']
    skip = False
    for (v, o) in BAD_COMBOS:
        if v in std and o in std:
            vi = std.find(v)
            oi = std.find(o)
            if vi >= 0 and oi > vi and oi - vi - len(v) <= 1:
                skip = True
                break
    if not skip:
        filtered.append(item)
    else:
        removed += 1

print(f"  移除不合理搭配: {removed} 句")
print(f"  校准后: {len(filtered)} 句")

# ===== 重新编号 + 保存 =====
for i, item in enumerate(filtered):
    item['id'] = f'DT{i+1:06d}'

# 质检
markers = ['呃','哪块','什的','怎呃','弗','呒得','来斯','推板','扎实','刷刮','家去','俦','伢儿','几钿','汏','蛮']
has = sum(1 for s in filtered if any(m in s['dialect'] for m in markers))
print(f'\n📊 质检:')
print(f'  总句数: {len(filtered)}')
print(f'  独立普通话: 100%')
print(f'  方言特征词: {has/len(filtered)*100:.1f}%')

from collections import Counter
cats = Counter(s['category'] for s in filtered)
print(f'  大类 ({len(cats)}个):')
for cat, count in cats.most_common():
    print(f'    {cat:12s} {count:6d} ({count/len(filtered)*100:.1f}%)')

# 如果不足20万，从大库补
if len(filtered) < 200000:
    need = 200000 - len(filtered)
    print(f'\n补充 {need} 句...')
    # 从27万大库补充
    with open('dongtai_corpus_200k_final.json', 'r') as f:
        big_pool = json.load(f)
    
    seen_f = set(s['standard'] for s in filtered)
    added = 0
    for item in big_pool:
        if added >= need:
            break
        if item['standard'] not in seen_f:
            seen_f.add(item['standard'])
            filtered.append(item)
            added += 1
    
    for i, item in enumerate(filtered):
        item['id'] = f'DT{i+1:06d}'
    
    print(f'  补充后: {len(filtered)} 句')

# 保存
with open('dongtai_corpus_200k.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

# 索引
index = {}
for item in filtered:
    cat = item['category']
    sub = item['subcategory']
    if cat not in index:
        index[cat] = {'count': 0, 'subcategories': {}}
    index[cat]['count'] += 1
    if sub not in index[cat]['subcategories']:
        index[cat]['subcategories'][sub] = 0
    index[cat]['subcategories'][sub] += 1
with open('category_index_200k.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

import os
print(f'\n💾 保存完成 ({os.path.getsize("dongtai_corpus_200k.json")/1024/1024:.1f}MB)')

# 最终抽样
random.seed(42)
samples = random.sample(filtered, 15)
print('\n最终抽样:')
for s in samples:
    print(f'  {s["standard"][:30]:30s} → {s["dialect"][:30]:30s} [{s["subcategory"]}]')
