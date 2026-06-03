const { translate } = require('../../utils/translator');

Page({
  data: {
    mode: 'd',
    inputText: '',
    resultText: '',
    recording: false,
    rtRecording: false,
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

  onShow() {
    // 页面显示时
  },

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
    
    // 保存到历史
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

  toggleVoice() {
    const that = this;
    if (this.data.recording) {
      this.setData({ recording: false });
      return;
    }
    
    wx.authorize({
      scope: 'scope.record',
      success() {
        that.setData({ recording: true });
        const manager = wx.getRecorderManager();
        
        manager.onStop((res) => {
          that.setData({ recording: false });
          // 使用微信同声传译插件或降级
          wx.showToast({ title: '语音识别需配置同声传译插件', icon: 'none' });
        });
        
        manager.onStart(() => {});
        manager.start({ format: 'mp3', duration: 60000 });
        
        // 自动5秒后停止
        setTimeout(() => {
          if (that.data.recording) {
            manager.stop();
          }
        }, 5000);
      },
      fail() {
        wx.showModal({
          title: '需要录音权限',
          content: '请在设置中开启录音权限',
          confirmText: '去设置',
          success(res) {
            if (res.confirm) wx.openSetting();
          }
        });
      }
    });
  },

  toggleRealtimeVoice() {
    this.toggleVoice();
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
    wx.showToast({ title: '朗读需TTS插件', icon: 'none' });
  },

  clearInput() {
    this.setData({ inputText: '', resultText: '' });
  }
});
