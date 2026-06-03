# 东台方言翻译器 - 三大硬伤修复说明

## 修复的三个硬伤

### 1. ❌ 普通话识别了但没有及时翻译
**原因**: 语音识别的`onresult`回调中，`isFinal`检测后翻译调用时序不对
**修复**: 
- v8翻译器: `onresult`的`isFinal`分支中直接用`setTimeout(doTranslate, 50)`确保翻译
- 小程序: 识别结束`onStop`回调中直接调用`doTranslate()`
- 翻译后自动朗读结果

### 2. ❌ 东台话识别不准确
**原因**: 浏览器/微信的ASR只支持标准普通话(zh-CN)，不认识江淮官话方言
**修复**:
- 添加100+方言语音纠错映射(SPEECH_FIX/correctSpeech)
- 获取5个候选结果(maxAlternatives=5)，选纠错得分最高的
- 纠错示例: "什地"→"什的", "来死"→"来斯", "我仇"→"我俦"
- **东台话模式强烈建议文字输入**

### 3. ❌ 东台话和普通话都发音不出来
**原因**: TTS没有选择中文语音(voice)，浏览器可能用英文voice朗读中文
**修复**:
- v8翻译器: `initVoices()`加载中文语音，`speakText()`强制选择zh-CN voice
- 小程序: 接入微信同声传译插件TTS(`plugin.translate({tts:true})`)
- 翻译完成后自动朗读结果
- 朗读失败时有降级方案

## 在线地址
https://qianluis.github.io/dongtai-translator

## 微信小程序使用
1. 下载[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 导入`dongtai-mini`目录
3. 在app.json中填入你的AppID
4. 在微信后台添加"微信同声传译"插件(wx069ba97219f66d99)
5. 编译运行

## Coze上使用
将`dongtai-dialect-skill.md`作为Bot知识库，或直接告诉Bot翻译规则即可实时翻译。
