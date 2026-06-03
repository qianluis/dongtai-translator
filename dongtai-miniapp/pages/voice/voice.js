const engine = require('../../utils/dialect-engine')

Page({
  data: {
    isListening: false,
    recognized: '',
    corrected: '',
    translated: '',
    asrCorrected: false,
    history: [],
  },
  manager: null,

  onLoad() {
    this.manager = wx.getRecordRecognitionManager()
    this.manager.onStart(() => { this.setData({ isListening: true }) })
    this.manager.onStop((res) => {
      this.setData({ isListening: false })
      if (res.result) this.processVoice(res.result)
    })
    this.manager.onError((err) => {
      this.setData({ isListening: false })
      wx.showToast({ title: '识别出错', icon: 'none' })
    })
  },

  toggleRecord() {
    if (this.data.isListening) {
      this.manager.stop()
    } else {
      wx.authorize({
        scope: 'scope.record',
        success: () => {
          this.manager.start({ lang: 'zh_CN', continuous: false })
        },
        fail: () => {
          wx.showModal({ title: '需要麦克风权限', content: '请在设置中开启麦克风权限', confirmText: '去设置',
            success: (r) => { if (r.confirm) wx.openSetting() }
          })
        }
      })
    }
  },

  processVoice(asrText) {
    const corrected = engine.correctASR(asrText)
    const r = engine.translate(corrected, 'auto', false)
    this.setData({
      recognized: asrText,
      corrected: corrected,
      translated: r.result,
      asrCorrected: asrText !== corrected,
    })
    // 添加历史
    const history = this.data.history
    history.unshift({ from: asrText, to: r.result })
    if (history.length > 20) history.pop()
    this.setData({ history })
  },

  copyText() {
    wx.setClipboardData({ data: this.data.translated, success() { wx.showToast({ title: '已复制' }) } })
  },

  speakText() {
    wx.showToast({ title: '朗读功能开发中', icon: 'none' })
  },
})
