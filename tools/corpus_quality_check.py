#!/usr/bin/env python3
"""东台方言语料库质量检测脚本"""
import json
import sys
from collections import Counter

def check_quality(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = len(data)
    
    # 1. 唯一性检查
    dialect_set = set()
    standard_set = set()
    dup_dialect = 0
    dup_standard = 0
    for item in data:
        d = item.get('dialect', item.get('dongtai', ''))
        s = item.get('standard', item.get('mandarin', ''))
        if d in dialect_set: dup_dialect += 1
        if s in standard_set: dup_standard += 1
        dialect_set.add(d)
        standard_set.add(s)
    
    unique_dialect_pct = len(dialect_set) / total * 100 if total else 0
    unique_standard_pct = len(standard_set) / total * 100 if total else 0
    
    # 2. 分类分布
    cat_counter = Counter()
    subcat_counter = Counter()
    for item in data:
        cat = item.get('category', 'unknown')
        subcat = item.get('subcategory', 'unknown')
        cat_counter[cat] += 1
        subcat_counter[f"{cat}/{subcat}"] += 1
    
    # 3. 字段完整性
    required_fields = ['id', 'dialect', 'standard', 'category']
    missing_fields = 0
    for item in data:
        for field in required_fields:
            if field not in item or not item[field]:
                missing_fields += 1
                break
    
    # 4. 方言特征词检测（粗略判断是否有东台话特征）
    dongtai_markers = ['呃', '哪块', '什的', '怎呃', '杲昃', '来斯', '推板', '扎实', 
                       '刷刮', '家去', '俦', '伢儿', '几钿', '今呃', '明呃', '后呃',
                       '咯', '呐', '蛮', '弗', '覅', '呒']
    has_marker = 0
    for item in data:
        d = item.get('dialect', item.get('dongtai', ''))
        if any(m in d for m in dongtai_markers):
            has_marker += 1
    
    dialect_feature_pct = has_marker / total * 100 if total else 0
    
    # 输出报告
    print("=" * 60)
    print("📊 东台方言语料库质量检测报告")
    print("=" * 60)
    print(f"总句数: {total}")
    print(f"独立方言句: {len(dialect_set)} ({unique_dialect_pct:.1f}%)")
    print(f"独立普通话句: {len(standard_set)} ({unique_standard_pct:.1f}%)")
    print(f"方言重复句: {dup_dialect}")
    print(f"普通话重复句: {dup_standard}")
    print(f"字段缺失: {missing_fields}")
    print(f"方言特征词覆盖率: {dialect_feature_pct:.1f}%")
    
    # 判定
    pass_all = True
    print("\n" + "=" * 60)
    print("🎯 质量红线检查")
    print("=" * 60)
    
    checks = [
        ("唯一率 ≥ 95%", unique_standard_pct >= 95),
        ("方言特征词 ≥ 80%", dialect_feature_pct >= 80),
        ("字段完整", missing_fields == 0),
        ("每类 > 100句", min(cat_counter.values()) > 100 if cat_counter else False),
    ]
    
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if not result: pass_all = False
    
    print("\n" + "=" * 60)
    print("📂 分类分布 (Top 15)")
    print("=" * 60)
    for cat, count in cat_counter.most_common(15):
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"  {cat:20s} {count:6d} ({pct:5.1f}%) {bar}")
    
    if len(cat_counter) > 15:
        print(f"  ... 还有 {len(cat_counter) - 15} 个分类")
    
    print(f"\n🏁 总评: {'✅ 合格' if pass_all else '❌ 不合格，需打回重做'}")
    return pass_all

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'dongtai_corpus_100k.json'
    check_quality(filepath)
