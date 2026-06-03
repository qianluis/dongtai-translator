const { translate } = require('../../utils/translator');

Page({
  data: {
    mode: 'd',
    inputText: '',
    resultText: '',
    recording: false,
    voiceText: '',
    voiceResult: '',
    history: [],
    quickPhrases: [
      '我们今天去哪里玩',
      '这个东西多少钱',
      '你知道吗',
      '我很好谢谢',
      '怎么走',
      '在这里等一下',
      '你在说什么',
      '我俫今朝去咯块白相',
      '咯个杲昃好多钱呃',
      '你晓得弗',
      '我蛮蛮好谢谢呃',
      '怎呃跑',
      '勒咯块等一歇歇',
      '你勒讲什的'
    ]
  },

  onLoad() {
    // Check and request record permission ONCE on load, not every time
    this.checkRecordPermission();
  },

  checkRecordPermission() {
    const that = this;
    wx.getSetting({
      success(res) {
        if (res.authSetting['scope.record'] === false) {
          // User previously denied - show one-time explanation
          wx.showModal({
            title: '语音翻译需要录音权限',
            content: '东台方言翻译需要使用麦克风进行语音识别。说普通话时正常语速，说东台话时请放慢语速。',
            confirmText: '去授权',
            cancelText: '暂不',
            success(r) {
              if (r.confirm) wx.openSetting();
            }
          });
        }
      }
    });
  },

  onShow() {},

  setModeD() {
    this.setData({ mode: 'd' });
    this.doTranslate();
  },

  setModeM() {
    this.setData({ mode: 'm' });
    this.doTranslate();
  },

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
    const text = e.currentTarget.dataset.text;
    this.setData({ inputText: text });
    this.doTranslate();
  },

  // FIXED: Only authorize once, use RecorderManager after that
  toggleVoice() {
    const that = this;
    
    if (this.data.recording) {
      this.stopRecording();
      return;
    }
    
    // Check if we already have permission
    wx.getSetting({
      success(res) {
        if (res.authSetting['scope.record'] === false) {
          // Previously denied
          wx.showModal({
            title: '需要录音权限',
            content: '请在设置中开启录音权限以使用语音翻译。说东台话时请放慢语速。',
            confirmText: '去设置',
            success(r) {
              if (r.confirm) wx.openSetting();
            }
          });
          return;
        }
        
        // Either granted or not yet asked - start recording
        // wx.getRecorderManager doesn't need authorize again if already granted
        that.startRecording();
      }
    });
  },

  startRecording() {
    const that = this;
    const manager = wx.getRecorderManager();
    
    manager.onStart(() => {
      that.setData({ 
        recording: true,
        voiceText: '正在录音...请说话',
        voiceResult: '等待翻译...'
      });
    });
    
    manager.onStop((res) => {
      that.setData({ 
        recording: false,
        voiceText: '识别中...'
      });
      
      // Use WeChat speech recognition plugin or built-in
      // For now, show the result of recording
      that.recognizeVoice(res);
    });
    
    manager.onError((err) => {
      that.setData({ recording: false });
      if (err.errMsg && err.errMsg.includes('auth deny')) {
        wx.showModal({
          title: '需要录音权限',
          content: '请在设置中开启录音权限',
          confirmText: '去设置',
          success(r) {
            if (r.confirm) wx.openSetting();
          }
        });
      } else {
        wx.showToast({ title: '录音失败，请重试', icon: 'none' });
      }
    });
    
    manager.start({ 
      format: 'mp3', 
      duration: 10000,  // 10 seconds max
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 96000
    });
    
    // Auto-stop after 10s
    setTimeout(() => {
      if (that.data.recording) {
        that.stopRecording();
      }
    }, 10000);
  },

  stopRecording() {
    const manager = wx.getRecorderManager();
    manager.stop();
  },

  recognizeVoice(res) {
    // WeChat mini program speech recognition requires:
    // 1. WeChat同声传译插件 (plugin: wx6e2a088ae8371c11) for speech-to-text
    // 2. Or use server-side API
    
    // For now, prompt user to use input method voice
    this.setData({
      voiceText: '语音识别需配置同声传译插件',
      voiceResult: '请使用输入法语音功能'
    });
    
    wx.showToast({ 
      title: '请使用输入法语音输入', 
      icon: 'none',
      duration: 2000
    });
  },

  copyResult() {
    const text = this.data.resultText;
    if (!text) return;
    wx.setClipboardData({
      data: text,
      success() {
        wx.showToast({ title: '已复制', icon: 'success' });
      }
    });
  },

  speakResult() {
    // TTS in WeChat mini program requires plugin or server API
    // The WeChat同声传译插件 also supports TTS
    wx.showToast({ title: '朗读需配置同声传译插件', icon: 'none' });
  },

  clearInput() {
    this.setData({ inputText: '', resultText: '' });
  }
});
