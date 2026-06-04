# WenetSpeech-Wu 本地下载与东台方言语料提取指南

## 数据集概况

**WenetSpeech-Wu** 是首个大规模吴语方言语料库，包含约 **8,000小时** 语音数据，覆盖 **8个吴语子方言**，带有多维度标注（转写、吴语→普通话翻译、子方言标签、说话人属性、情感标注等）。

- 🤗 数据集地址：https://huggingface.co/datasets/ASLP-lab/WenetSpeech-Wu
- 📊 Benchmark地址：https://huggingface.co/datasets/ASLP-lab/WenetSpeech-Wu-Bench
- 📄 论文：https://arxiv.org/abs/2601.11027
- 🐙 GitHub：https://github.com/ASLP-lab/WenetSpeech-Wu-Repo

## 8个吴语子方言

| 编号 | 子方言 | 英文名 | 与东台话关系 |
|------|--------|--------|-------------|
| 1 | 上海话 | Shanghainese | 远 |
| 2 | 苏州话 | Suzhounese | 远 |
| 3 | 绍兴话 | Shaoxingnese | 中 |
| 4 | 宁波话 | Ningbonese | 近 |
| 5 | 杭州话 | Hangzhounese | 中 |
| 6 | 嘉兴话 | Jiaxingnese | 中 |
| 7 | **台州话** | **Taizhounese** | **最近** |
| 8 | 温州话 | Wenzhounese | 远 |

> ⚠️ 约37%的数据子方言标签为"Unknown"，其中可能也包含台州话。
> 
> 东台话属江淮官话东通片，受吴语（特别是泰如片/台州片）深度影响。**台州话子集**是东台方言ASR训练最相关的数据源。

## 方法一：HuggingFace datasets 流式下载（推荐）

### 前提条件
```bash
pip install datasets huggingface_hub
```

### 步骤1：申请数据集访问权限
1. 访问 https://huggingface.co/datasets/ASLP-lab/WenetSpeech-Wu
2. 点击 **"Request access"** 提交申请
3. 等待审批（通常1-3个工作日）
4. 审批通过后即可下载

### 步骤2：仅下载标注元数据（分析子方言分布）
```python
#!/usr/bin/env python3
"""扫描WenetSpeech-Wu子方言分布（不下载音频）"""
from datasets import load_dataset
import json

ds = load_dataset("ASLP-lab/WenetSpeech-Wu", streaming=True, trust_remote_code=True)

dialect_dist = {}
total = 0

for split_name in ds.keys():
    print(f"Scanning split: {split_name}")
    for item in ds[split_name]:
        total += 1
        dialect = None
        for key in ['dialect', 'sub_dialect', 'dialect_label', 'label']:
            if key in item:
                dialect = str(item[key])
                break
        if dialect:
            dialect_dist[dialect] = dialect_dist.get(dialect, 0) + 1
        if total % 10000 == 0:
            print(f"  Scanned {total}, found {len(dialect_dist)} dialects")
        if total >= 200000:
            break
    if total >= 200000:
        break

print(f"\n=== 子方言分布 (scanned {total}) ===")
for d, c in sorted(dialect_dist.items(), key=lambda x: -x[1]):
    print(f"  {d}: {c} ({c/total*100:.1f}%)")

with open("wenetspeech_wu_dialect_dist.json", "w") as f:
    json.dump(dialect_dist, f, indent=2, ensure_ascii=False)
```

### 步骤3：筛选并下载台州话子集
```python
#!/usr/bin/env python3
"""下载WenetSpeech-Wu台州话子集"""
from datasets import load_dataset
import json, os, soundfile as sf

output_dir = "./wenetspeech_wu_taizhou"
os.makedirs(f"{output_dir}/audio", exist_ok=True)

ds = load_dataset("ASLP-lab/WenetSpeech-Wu", streaming=True, trust_remote_code=True)

taizhou_count = 0
max_samples = 50000

for split_name in ds.keys():
    print(f"Processing split: {split_name}")
    for item in ds[split_name]:
        dialect = None
        for key in ['dialect', 'sub_dialect', 'dialect_label', 'label']:
            if key in item:
                dialect = str(item[key])
                break
        
        if dialect and ('taizhou' in dialect.lower() or '台州' in dialect):
            # 保存元数据
            meta = {k: v for k, v in item.items() if k != 'audio'}
            with open(f"{output_dir}/metadata.jsonl", "a") as f:
                f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            
            # 保存音频
            if 'audio' in item and item['audio']:
                audio_path = f"{output_dir}/audio/{taizhou_count:06d}.wav"
                audio_data = item['audio']
                if isinstance(audio_data, dict):
                    if 'array' in audio_data and 'sampling_rate' in audio_data:
                        sf.write(audio_path, audio_data['array'], audio_data['sampling_rate'])
                    elif 'bytes' in audio_data:
                        with open(audio_path, 'wb') as f:
                            f.write(audio_data['bytes'])
                    elif 'path' in audio_data:
                        import shutil
                        shutil.copy(audio_data['path'], audio_path)
            
            taizhou_count += 1
            if taizhou_count % 100 == 0:
                print(f"  Collected {taizhou_count} Taizhou samples")
            if taizhou_count >= max_samples:
                break
    if taizhou_count >= max_samples:
        break

print(f"\nTotal Taizhou samples: {taizhou_count}")
```

## 方法二：HuggingFace CLI 批量下载

```bash
pip install huggingface_hub

# 下载完整数据集（约8000小时，需大量磁盘空间≥500GB）
huggingface-cli download ASLP-lab/WenetSpeech-Wu --repo-type dataset --local-dir ./WenetSpeech-Wu

# 仅下载Benchmark（较小，用于测试）
huggingface-cli download ASLP-lab/WenetSpeech-Wu-Bench --repo-type dataset --local-dir ./WenetSpeech-Wu-Bench
```

## 方法三：探索数据集文件结构

```python
from huggingface_hub import HfApi
api = HfApi()

# 列出数据集所有文件
files = api.list_repo_files("ASLP-lab/WenetSpeech-Wu", repo_type="dataset")
for f in sorted(files)[:100]:
    print(f)
```

## 数据格式

WenetSpeech-Wu标注为JSONL格式：
```json
{
    "key": "utterance_id",
    "wav": "path/to/audio.wav",
    "txt": "吴语转写文本",
    "mandarin": "对应普通话翻译",
    "dialect": "子方言标签(如Taizhounese)",
    "domain": "领域标签",
    "confidence": 0.95,
    "speaker_gender": "男/女",
    "speaker_age": "年龄段",
    "emotion": "情感标签"
}
```

## ASR模型排行榜（WenetSpeech-Wu-Bench CER%）

| 模型 | Dialogue | Reading | ASR | 可用性 |
|------|----------|---------|-----|--------|
| Step-Audio2-Wu-ASR ⭐ | 8.68 | 7.86 | **12.85** | 需GPU+ms-swift |
| Whisper-medium-Wu ⭐ | 14.19 | 11.09 | 14.33 | 需GPU |
| Conformer-U2pp-Wu ⭐ | 15.20 | 12.24 | 15.14 | ✅已部署(INT8) |
| Qwen3-ASR | 23.96 | 24.13 | 29.31 | CPU可跑但东台话差 |
| SenseVoice-small | 29.20 | 31.00 | 46.85 | ✅已部署 |

## 东台方言语料提取工作流

```
1. 用户本地下载 WenetSpeech-Wu 数据集（需申请权限）
2. 筛选台州话子集 → 预计数百小时
3. 用ASR管线(dongtai_asr_v3.py)自动转写
4. 人工校对 + 东台本地人审核
5. 合并到400K语料库
6. 微调ASR模型适配东台话
```

## 用户辅助训练协作方式

1. **用户本地GPU** → 运行Step-Audio2-Wu-ASR（CER 8.68%最佳模型）
2. **用户下载WenetSpeech-Wu** → 筛选台州话子集用于微调
3. **用户本地下载东台老王571个视频** → ASR转写为纯东台方言语料
4. **微调Conformer-U2pp-Wu模型** → 适配东台话特有发音和词汇
