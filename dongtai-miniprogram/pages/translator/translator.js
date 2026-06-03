const { translate } = require('../../utils/translator');
// 微信同声传译插件 - 语音识别+TTS
const plugin = requirePlugin('WechatSI');
const manager = plugin.getRecordRecognitionManager();

Page({
  data: {
    mode: 'd',
    inputText: '',
    resultText: '',
    recording: false,
    speaking: false,
    ttsReady: false,
    voiceTip: '点击语音输入',
    history: [],
    quickPhrases: [
      '我们今天去哪里玩',
      '这个东西多少钱',
      '你知道吗',
      '我很好谢谢',
      '怎么走',
      '我俫今朝去咯块白相',
      '咯个杲昃好多钱呃',
      '你晓得弗'
    ]
  },

  onLoad() {
    this.initTTS();
    this.initSTT();
    this.checkPermission();
  },

  // === TTS初始化 ===
  initTTS() {
    const that = this;
    // 微信同声传译插件的TTS
    if (plugin && plugin.textToSpeech) {
      this.setData({ ttsReady: true });
      console.log('[TTS] 同声传译插件TTS就绪');
    } else {
      console.warn('[TTS] 同声传译插件未加载，TTS不可用');
    }
  },

  // === STT初始化 ===
  initSTT() {
    const that = this;
    
    manager.onRecognize((res) => {
      // 实时识别结果
      const text = res.result;
      if (text) {
        that.setData({ inputText: text });
        that.doTranslate();
      }
    });

    manager.onStop((res) => {
      // 识别结束
      const text = res.result;
      that.setData({ recording: false, voiceTip: '点击语音输入' });
      if (text) {
        that.setData({ inputText: text });
        that.doTranslate();
        // 自动朗读翻译结果
        that.speakResult();
      }
    });

    manager.onStart(() => {
      that.setData({ recording: true, voiceTip: '正在听...请说话' });
    });

    manager.onError((err) => {
      console.error('[STT] 错误:', err);
      that.setData({ recording: false, voiceTip: '识别失败，请重试' });
      if (err.errMsg && err.errMsg.includes('auth')) {
        wx.showModal({
          title: '需要录音权限',
          content: '请在设置中允许麦克风权限',
          confirmText: '去设置',
          success(r) { if (r.confirm) wx.openSetting(); }
        });
      }
    });
  },

  // === 权限检查（只弹一次） ===
  checkPermission() {
    wx.getSetting({
      success(res) {
        if (res.authSetting['scope.record'] === false) {
          wx.showModal({
            title: '语音翻译需要录音权限',
            content: '说普通话→自动翻译+朗读东台话 | 说东台话时请放慢语速',
            confirmText: '去授权',
            success(r) { if (r.confirm) wx.openSetting(); }
          });
        }
      }
    });
  },

  // === TTS朗读 ===
  speak(text) {
    if (!text || !this.data.ttsReady) return;
    
    const that = this;
    that.setData({ speaking: true });

    plugin.textToSpeech({
      lang: 'zh_CN',
      tts: true,
      content: text,
      success(res) {
        // res.filename 是音频文件路径
        const innerAudio = wx.createInnerAudioContext();
        innerAudio.src = res.filename;
        innerAudio.rate = 0.8;
        innerAudio.onEnded(() => {
          that.setData({ speaking: false });
          innerAudio.destroy();
        });
        innerAudio.onError(() => {
          that.setData({ speaking: false });
          innerAudio.destroy();
        });
        innerAudio.play();
      },
      fail(err) {
        console.error('[TTS] 朗读失败:', err);
        that.setData({ speaking: false });
        wx.showToast({ title: '朗读失败', icon: 'none' });
      }
    });
  },

  // === 模式切换 ===
  setModeD() { this.setData({ mode: 'd' }); this.doTranslate(); },
  setModeM() { this.setData({ mode: 'm' }); this.doTranslate(); },

  // === 输入 ===
  onInput(e) {
    this.setData({ inputText: e.detail.value });
    this.doTranslate();
  },

  doTranslate() {
    const { inputText, mode } = this.data;
    if (!inputText.trim()) {
      this.setData({ resultText: '' });
      return;
    }
    const result = translate(inputText, mode);
    const history = this.data.history.slice(0, 19);
    history.unshift({
      from: inputText,
      to: result,
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    });
    this.setData({ resultText: result, history });
  },

  usePhrase(e) {
    this.setData({ inputText: e.currentTarget.dataset.text });
    this.doTranslate();
  },

  // === 语音按钮 ===
  toggleVoice() {
    if (this.data.recording) {
      manager.stop();
      return;
    }
    manager.start({ lang: 'zh_CN' });
  },

  // === 朗读结果 ===
  speakResult() {
    this.speak(this.data.resultText);
  },

  speakOriginal() {
    this.speak(this.data.inputText);
  },

  copyResult() {
    if (!this.data.resultText) return;
    wx.setClipboardData({
      data: this.data.resultText,
      success() { wx.showToast({ title: '已复制', icon: 'success' }); }
    });
  },

  clearInput() {
    this.setData({ inputText: '', resultText: '' });
  }
});
