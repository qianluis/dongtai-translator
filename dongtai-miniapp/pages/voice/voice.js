const engine = require('../../utils/dialect-engine')

Page({
  data: {
    isListening: false,
    recognized: '',
    corrected: '',
    translated: '',
    asrCorrected: false,
    history: [],
    isSpeaking: false,
    authRequested: false,
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
      if (err.errMsg && err.errMsg.includes('auth')) {
        this._requestAuth()
      } else {
        wx.showToast({ title: '识别出错，请重试', icon: 'none' })
      }
    })
  },

  _requestAuth() {
    if (this.data.authRequested) {
      wx.showModal({
        title: '需要麦克风权限',
        content: '请在设置中开启麦克风权限',
        confirmText: '去设置',
        success: (r) => { if (r.confirm) wx.openSetting() }
      })
      return
    }
    this.setData({ authRequested: true })
    wx.authorize({
      scope: 'scope.record',
      success: () => { this._startRecord() },
      fail: () => {
        wx.showModal({
          title: '需要麦克风权限',
          content: '请在设置中开启麦克风权限',
          confirmText: '去设置',
          success: (r) => { if (r.confirm) wx.openSetting() }
        })
      }
    })
  },

  toggleRecord() {
    if (this.data.isListening) {
      this.manager.stop()
    } else {
      this._startRecord()
    }
  },

  _startRecord() {
    wx.getSetting({
      success: (res) => {
        if (res.authSetting['scope.record'] === false) {
          this._requestAuth()
        } else if (res.authSetting['scope.record'] === undefined) {
          this._requestAuth()
        } else {
          this.manager.start({ lang: 'zh_CN', continuous: false })
        }
      }
    })
  },

  processVoice(asrText) {
    // ASR纠错
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
    history.unshift({ from: asrText, to: r.result, time: new Date().toLocaleTimeString() })
    if (history.length > 20) history.pop()
    this.setData({ history })
    // 自动朗读翻译结果
    setTimeout(() => this.speakText(this.data.translated), 500)
  },

  // 真正可用的TTS - 使用微信插件同声传译
  speakText(text) {
    if (!text) text = this.data.translated
    if (!text) { wx.showToast({ title: '没有可朗读的内容', icon: 'none' }); return }
    
    this.setData({ isSpeaking: true })
    
    // 方案1: 使用微信同声传译插件（推荐）
    const plugin = requirePlugin('WechatSI')
    if (plugin && plugin.translate) {
      plugin.translate({
        lfrom: 'zh_CN',
        lto: 'zh_CN', 
        content: text,
        success: (res) => {
          if (res.filename) {
            const innerAudio = wx.createInnerAudioContext()
            innerAudio.src = res.filename
            innerAudio.onEnded(() => this.setData({ isSpeaking: false }))
            innerAudio.onError(() => this._fallbackTTS(text))
            innerAudio.play()
          }
        },
        fail: () => this._fallbackTTS(text)
      })
      return
    }
    
    // 方案2: 备用 - 百度TTS
    this._baiduTTS(text)
  },

  _baiduTTS(text) {
    const that = this
    wx.request({
      url: 'https://tts.baidu.com/text2audio',
      data: { 
        lan: 'zh', 
        text: text, 
        spd: 5,    // 语速
        pit: 5,    // 音调
        vol: 9,    // 音量
        per: 4     // 发音人（4=情感女声）
      },
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
                  // 清理临时文件
                  try { fs.unlinkSync(filePath) } catch(e) {}
                })
                innerAudio.onError(() => that.setData({ isSpeaking: false }))
                innerAudio.play()
              },
              fail() { that.setData({ isSpeaking: false }) }
            })
          } catch(e) { that.setData({ isSpeaking: false }) }
        } else {
          that.setData({ isSpeaking: false })
        }
      },
      fail() { that.setData({ isSpeaking: false }) }
    })
  },

  _fallbackTTS(text) {
    // 最终兜底
    this._baiduTTS(text)
  },

  copyText() {
    wx.setClipboardData({ data: this.data.translated, success() { wx.showToast({ title: '已复制' }) } })
  },
})
