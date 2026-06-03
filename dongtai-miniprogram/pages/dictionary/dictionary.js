const { dialectWords } = require('../../utils/translator');

const dictCategories = {
  '人称代词': ['我们','你们','他们','自己','这里','那里','这个','那个'],
  '疑问词': ['什么','怎么','哪里','多少','谁','为什么'],
  '核心动词': ['知道','看','找','洗','玩','说','回家','聊天','睡觉','走','拿','放','扔','想','喝','给','丢','涂','帮','吃'],
  '时间词': ['今天','明天','昨天','晚上','早上','中午','上午','下午','现在','以前','刚才','经常','休息','赶紧'],
  '称谓': ['爷爷','奶奶','爸爸','妈妈','哥哥','姐姐','丈夫','老婆','小孩','邻居'],
  '身体部位': ['头','肚子','脸','眼睛','耳朵','鼻子','脖子','膝盖'],
  '食物': ['早饭','午饭','晚饭','黄鳝','螃蟹','东西','勺子','鸡蛋'],
  '家居': ['客厅','厨房','衣服','火柴','肥皂','毛巾','椅子','桌子','窗户','院子'],
  '形容词': ['厉害','差劲','能干','干净','舒服','热闹','聪明','笨','漂亮','马虎','便宜','讨厌','不行','高兴','烦','累'],
  '程度/否定': ['很','非常','太','没有','不要','不'],
  '动物/自然': ['太阳','蜈蚣','蟾蜍','蛇','老鼠','蚯蚓','下雨'],
};

Page({
  data: {
    searchKey: '',
    dictSections: []
  },

  onLoad() {
    this.loadDict();
  },

  loadDict(searchKey) {
    const sections = [];
    for (const [title, words] of Object.entries(dictCategories)) {
      const items = words
        .filter(w => dialectWords[w])
        .map(w => ({ from: w, to: dialectWords[w] }))
        .filter(item => {
          if (!searchKey) return true;
          return item.from.includes(searchKey) || item.to.includes(searchKey);
        });
      if (items.length) sections.push({ title, items });
    }
    this.setData({ dictSections: sections });
  },

  onSearch(e) {
    this.setData({ searchKey: e.detail.value });
    this.loadDict(e.detail.value);
  },

  useWord(e) {
    const { from, to } = e.currentTarget.dataset;
    wx.setClipboardData({
      data: `${from} → ${to}`,
      success() {
        wx.showToast({ title: '已复制', icon: 'success' });
      }
    });
  }
});
