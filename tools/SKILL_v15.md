---
name: dongtai-dialect-translator
description: 东台方言翻译+TTS语音朗读+双模型ASR语音识别。支持普通话↔东台方言双向翻译，53K精选语料库+短语级翻译引擎V2+上下文感知+160+ASR纠错规则。当用户提到东台话、东台方言、方言翻译、如泰片、江淮官话翻译、方言说、方言词典等需求时使用
---

# 东台方言翻译技能 v15

## 功能
实时双向翻译东台方言与普通话，支持：
- 东台方言 → 普通话
- 普通话 → 东台方言
- **53K高质量语料库**（从400K精选，99.4%≥1方言标记，95.7%≥2，平均5个）
- **短语级翻译引擎V2**（上下文感知+天气模式+后缀智能处理）
- **双模型ASR语音识别**（WenetSpeech-Wu吴语专 + SenseVoiceSmall通用）
- 语音输入自动纠错（160+ ASR纠错规则）
- **TTS语音朗读**（翻译后自动生成原文+译文MP3音频）

## 核心API

### translate_with_tts(text, direction='auto', asr_mode=False, voice='zh-CN-XiaoxiaoNeural')
**推荐使用。** 翻译并生成音频。

返回：
```python
{
    'result': '翻译结果',
    'direction': 'm2d' 或 'd2m',
    'method': 'exact/exact_normalized/corpus_substring+rules/rules/fuzzy/fallback/no_translation',
    'confidence': 0-100,
    'audio_original': '原文MP3路径',
    'audio_translated': '译文MP3路径',
    'asr_corrected': True/False
}
```

**调用后必须做的事：**
1. 用 `file_to_url(r['audio_original'])` 和 `file_to_url(r['audio_translated'])` 生成可播放链接
2. 在回复中同时展示翻译结果和音频链接
3. 格式示例：`🔊 朗读原文: [点击播放](url)` 和 `🔊 朗读译文: [点击播放](url)`

### translate(text, direction='auto', asr_mode=False)
仅翻译不生成音频。

## 翻译方法说明
| 方法 | 置信度 | 说明 |
|------|--------|------|
| exact | 100% | 语料库精确匹配（O(1)哈希查找） |
| exact_normalized | 98% | 去标点后精确匹配 |
| corpus_substring+rules | 88% | 语料子串匹配+规则补充 |
| rules | 75-90% | 短语级规则翻译（上下文感知） |
| fuzzy | 70% | 倒排索引+n-gram模糊匹配 |
| fallback | 50% | 仅规则，翻译不完整 |
| no_translation | 20% | 无法翻译 |

## 语音选择
- `zh-CN-XiaoxiaoNeural`: 女声晓晓（默认，清晰自然）
- `zh-CN-YunxiNeural`: 男声云希（沉稳有力）
- 方言原文→男声，普通话译文→女声（translate_with_tts自动分配）

## V15改进
1. **语料库3.6倍扩容**：14.6K→53.4K，精确匹配率大幅提升
2. **翻译引擎V2重写**：短语级翻译+上下文感知+倒排索引模糊匹配
3. **天气模式识别**：下了X雨→落咧X雨，下X雨了→落X雨咧
4. **后缀智能处理**：消除双重后缀bug
5. **语境代词**：这→搿个/搿搭，那→嗨个/嗨搭
6. **精确匹配O(1)**：哈希索引替代线性搜索

## ASR语音识别管线

### recognize_audio(wav_path, fusion=True)
双模型融合语音识别。

**模型说明：**
- **WenetSpeech-Wu**: 8000小时吴语语料训练，INT8量化，CPU推理0.1s/句
- **SenseVoiceSmall**: 30万小时多语言训练，通用性强
- **融合策略**: 一致→0.95置信度；不一致→优先吴语模型+纠错层

## 语料库
- 53,421条精选 | 强方言率99.4% | 深度方言(≥2)95.7% | 平均5个方言标记
- 7大类：医疗健康/政务办事/生存刚需/社交融入/职场沟通/文化生活/方言文化
