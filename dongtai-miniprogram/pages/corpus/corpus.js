// 精选语料数据 (嵌入小程序，完整400K数据可从服务器加载)
const sampleCorpus = [
  {id:1,d:'我俫今朝去咯块望望好弗好？',m:'我们今天去那里看看行不行？',c:'社交融入',s:'日常对话',f:4},
  {id:2,d:'咯个杲昃好多钱呃？',m:'这个东西多少钱了？',c:'生存刚需',s:'购物消费',f:4},
  {id:3,d:'先生，我肚皮蛮蛮痛呃',m:'医生，我肚子很疼了',c:'医疗健康',s:'门诊就医',f:5},
  {id:4,d:'你晓得怎呃去社保局弗？',m:'你知道怎么去社保局吗？',c:'政务办事',s:'社保咨询',f:3},
  {id:5,d:'搿歇没得班上呃，怎呃办？',m:'现在没有班上了，怎么办？',c:'职场沟通',s:'求职就业',f:4},
  {id:6,d:'今朝个鱼汤面蛮蛮好吃',m:'今天的鱼汤面很好吃',c:'文化生活',s:'东台特色',f:3},
  {id:7,d:'杲昃蛮蛮推板呃',m:'东西很差劲了',c:'方言文化',s:'方言成语',f:5},
  {id:8,d:'活鲜活跳——蛮蛮来斯',m:'活蹦乱跳——很厉害',c:'方言文化',s:'歇后语',f:5},
  {id:9,d:'拖汤滴水——弗爽气',m:'拖拖拉拉——不干脆',c:'方言文化',s:'歇后语',f:5},
  {id:10,d:'假马日鬼——装模作样',m:'假马日鬼——装模作样',c:'方言文化',s:'俏皮话',f:5},
  {id:11,d:'快递勒哪块取呃？',m:'快递在哪里取了？',c:'生存刚需',s:'快递物流',f:3},
  {id:12,d:'今夜头跳弗跳舞呃？',m:'今晚跳不跳舞了？',c:'社交融入',s:'广场舞太极',f:4},
  {id:13,d:'老早没得望见呃！',m:'很久没有看见了！',c:'社交融入',s:'同学聚会',f:4},
  {id:14,d:'把只脉望望',m:'把一个脉看看',c:'医疗健康',s:'中医养生',f:3},
  {id:15,d:'发绣怎呃学呃？',m:'发绣怎么学了？',c:'文化生活',s:'非遗传承',f:3},
  {id:16,d:'董永卖身葬父个故事',m:'董永卖身葬父的故事',c:'方言文化',s:'方言故事',f:3},
  {id:17,d:'我俫蛮蛮吃力呃，寻歇一歇',m:'我很累了，要休息一下',c:'职场沟通',s:'职场日常',f:4},
  {id:18,d:'嗲嗲颈椎病蛮久呃，你晓得怎呃办',m:'爷爷颈椎病很久的，你知道怎么办',c:'医疗健康',s:'老年健康',f:4},
  {id:19,d:'嫲嫲腰蛮蛮痛呃，我俫寻先生望望',m:'奶奶腰很疼了，我们找医生看看',c:'医疗健康',s:'老年健康',f:4},
  {id:20,d:'咯块个房价蛮蛮贵呃',m:'这里的房价很贵了',c:'生存刚需',s:'住房租房',f:3},
  {id:21,d:'明朝我俫去弶港吃海鲜',m:'明天我们去弶港吃海鲜',c:'文化生活',s:'东台特色',f:4},
  {id:22,d:'你俫阿要一淘去白相？',m:'你们要不要一起去玩？',c:'社交融入',s:'日常对话',f:5},
  {id:23,d:'弗晓得咯个怎呃弄呃',m:'不知道这个怎么弄了',c:'职场沟通',s:'职场日常',f:4},
  {id:24,d:'我俫家个伢子蛮蛮灵光',m:'我们家的孩子很聪明',c:'社交融入',s:'家庭关系',f:4},
  {id:25,d:'啥人晓得咯块阿有银行弗？',m:'谁知道这里有没有银行？',c:'生存刚需',s:'银行服务',f:5},
];

Page({
  data: {
    searchKey: '',
    curCat: 'all',
    corpusItems: [],
    page: 0,
    hasMore: true
  },

  onLoad() {
    this.loadCorpus();
  },

  loadCorpus() {
    const { curCat, searchKey, page } = this.data;
    let items = sampleCorpus;
    
    if (curCat !== 'all') {
      const catMap = {
        survival: '生存刚需', social: '社交融入', medical: '医疗健康',
        government: '政务办事', workplace: '职场沟通', culture: '文化生活', dialect: '方言文化'
      };
      const catName = catMap[curCat];
      if (catName) items = items.filter(i => i.c === catName);
    }
    
    if (searchKey) {
      items = items.filter(i => i.d.includes(searchKey) || i.m.includes(searchKey));
    }

    this.setData({ 
      corpusItems: items,
      hasMore: false // 本地数据有限，后续可接入API
    });
  },

  onSearch(e) {
    this.setData({ searchKey: e.detail.value });
    this.loadCorpus();
  },

  doSearch() {
    this.loadCorpus();
  },

  filterCat(e) {
    const cat = e.currentTarget.dataset.cat;
    this.setData({ curCat: cat, page: 0 });
    this.loadCorpus();
  },

  loadMore() {
    // 后续可接入服务器API加载更多数据
    wx.showToast({ title: '更多语料需联网加载', icon: 'none' });
  },

  copyItem(e) {
    const { d, m } = e.currentTarget.dataset;
    wx.setClipboardData({
      data: `东台话: ${d}\n普通话: ${m}`,
      success() {
        wx.showToast({ title: '已复制', icon: 'success' });
      }
    });
  }
});
