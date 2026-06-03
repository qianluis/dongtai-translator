const engine = require('../../utils/dialect-engine')
const plugin = requirePlugin('WechatSI')

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
    quickPhrases: [
      '今天去哪里吃饭', '我俫今朝去哪块', '多少钱', '几钿',
      '不知道', '勿晓得', '晚上吃什么', '侯告吃什的',
      '你好', '蛮好呃', '很厉害', '蛮蛮结棍',
      '帮忙', '帮衬下', '回家', '家去',
    ],
    isListening: false,
  },

  onInput(e) {
    this.setData({ inputText: e.detail.value })
  },

  switchDirection() {
    const d = this.data.direction === 'm2d' ? 'd2m' : 'm2d'
    this.setData({
      direction: d,
      inputLabel: d === 'm2d' ? '输入普通话' : '输入东台话',
      outputLabel: d === 'm2d' ? '东台方言' : '普通话',
      inputPlaceholder: d === 'm2d' ? '输入普通话句子...' : '输入东台方言...',
      result: '',
    })
  },

  doTranslate() {
    const text = this.data.inputText.trim()
    if (!text) { wx.showToast({ title: '请输入内容', icon: 'none' }); return }
    const r = engine.translate(text, this.data.direction, true)
    this.setData({
      result: r.result,
      confidence: r.confidence,
      outputLabel: r.directionLabel,
      asrCorrected: r.asrCorrected,
    })
  },

  usePhrase(e) {
    const text = e.currentTarget.dataset.text
    this.setData({ inputText: text })
    const r = engine.translate(text, this.data.direction, true)
    this.setData({ result: r.result, confidence: r.confidence, outputLabel: r.directionLabel })
  },

  startVoice() {
    const that = this
    wx.authorize({ scope: 'scope.record', success() {
      const manager = wx.getRecordRecognitionManager()
      manager.onStart(() => { that.setData({ isListening: true }) })
      manager.onStop((res) => {
        that.setData({ isListening: false })
        if (res.result) {
          that.setData({ inputText: res.result })
          that.doTranslate()
        }
      })
      manager.onError(() => { that.setData({ isListening: false }) })
      manager.start({ lang: 'zh_CN', continuous: false })
      wx.showToast({ title: '正在聆听...', icon: 'none', duration: 3000 })
    }, fail() {
      wx.showToast({ title: '请授权麦克风', icon: 'none' })
    }})
  },

  copyResult() {
    wx.setClipboardData({ data: this.data.result, success() { wx.showToast({ title: '已复制' }) } })
  },

  speakResult() {
    const text = this.data.result
    if (!text) return
    wx.request({
      url: 'https://dds.dui.ai/runtime/v1/synthesize',
      data: { text, voice: 'xiaoyan', speed: 1 },
      success(res) {
        if (res.data && res.data.audio) {
          const innerAudio = wx.createInnerAudioContext()
          innerAudio.src = 'data:audio/mp3;base64,' + res.data.audio
          innerAudio.play()
        }
      },
      fail() {
        // 备选：用系统TTS
        wx.showToast({ title: '暂不支持朗读', icon: 'none' })
      }
    })
  },
})
