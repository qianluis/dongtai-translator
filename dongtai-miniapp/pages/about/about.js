Page({
  data: {
    categories: [
      { icon: '🏠', name: '生存刚需', count: '60K' },
      { icon: '🏛️', name: '政务办事', count: '60K' },
      { icon: '🤝', name: '社交融入', count: '60K' },
      { icon: '💼', name: '职场沟通', count: '60K' },
      { icon: '🏥', name: '医疗健康', count: '60K' },
      { icon: '🎭', name: '文化生活', count: '50K' },
      { icon: '📖', name: '方言文化', count: '50K' },
    ],
  },
  openGithub() {
    wx.setClipboardData({ data: 'https://github.com/qianluis/dongtai-translator' })
  },
})
