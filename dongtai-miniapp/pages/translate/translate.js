const engine = require('../../utils/dialect-engine')

Page({
  data: {
    inputText: '',
    result: '',
    direction: 'auto',
    inputLabel: '输入普通话或东台话',
    outputLabel: '翻译结果',
    inputPlaceholder: '输入要翻译的内容...',
    confidence: 0,
    asrCorrected: false,
    isSpeaking: false,
    quickPhrases: [
      '今天去哪里吃饭', '我俫今朝去哪块', '多少钱', '几钿',
      '不知道', '勿晓得', '晚上吃什么', '侯告吃什的',
      '你好', '蛮好呃', '很厉害', '蛮蛮结棍',
      '帮忙', '帮衬下', '回家', '家去',
    ],
  },
  translateTimer: null,

  onInput(e) {
    this.setData({ inputText: e.detail.value })
    clearTimeout(this.translateTimer)
    this.translateTimer = setTimeout(() => this.doTranslate(), 300)
  },

  doTranslate() {
    const text = this.data.inputText.trim()
    if (!text) { this.setData({ result: '', confidence: 0 }); return }
    const r = engine.translate(text, this.data.direction, true)
    this.setData({
      result: r.result,
      confidence: r.confidence,
      outputLabel: r.directionLabel || (r.direction === 'm2d' ? '东台方言' : '普通话'),
      asrCorrected: r.asrCorrected,
    })
  },

  usePhrase(e) {
    const text = e.currentTarget.dataset.text
    this.setData({ inputText: text })
    const r = engine.translate(text, this.data.direction, true)
    this.setData({ result: r.result, confidence: r.confidence, outputLabel: r.directionLabel || '' })
  },

  // 真正可用的TTS
  speakResult() {
    const text = this.data.result
    if (!text) { wx.showToast({ title: '请先翻译', icon: 'none' }); return }
    
    this.setData({ isSpeaking: true })
    this._baiduTTS(text)
  },

  speakInput() {
    const text = this.data.inputText
    if (!text) return
    this.setData({ isSpeaking: true })
    this._baiduTTS(text)
  },

  _baiduTTS(text) {
    const that = this
    wx.request({
      url: 'https://tts.baidu.com/text2audio',
      data: { lan: 'zh', text: text, spd: 5, pit: 5, vol: 9, per: 4 },
      responseType: 'arraybuffer',
      success(res) {
        if (res.statusCode === 200 && res.data && res.data.byteLength > 0) {
          const fs = wx.getFileSystemManager()
          const filePath = `${wx.env.USER_DATA_PATH}/tts_${Date.now()}.mp3`
          try {
            fs.writeFile({
              filePath: filePath,
              data: res.data,
              encoding: 'binary',
              success() {
                const innerAudio = wx.createInnerAudioContext()
                innerAudio.src = filePath
                innerAudio.onEnded(() => { 
                  that.setData({ isSpeaking: false })
                  try { fs.unlinkSync(filePath) } catch(e) {}
                })
                innerAudio.onError(() => that.setData({ isSpeaking: false }))
                innerAudio.play()
              },
              fail() { that.setData({ isSpeaking: false }) }
            })
          } catch(e) { that.setData({ isSpeaking: false }) }
        } else { that.setData({ isSpeaking: false }) }
      },
      fail() { that.setData({ isSpeaking: false }) }
    })
  },

  copyResult() {
    wx.setClipboardData({ data: this.data.result, success() { wx.showToast({ title: '已复制' }) } })
  },

  clearAll() {
    this.setData({ inputText: '', result: '', confidence: 0 })
  },
})
