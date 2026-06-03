# 东台方言实时翻译器

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/dongtai-dialect/dongtai-translator?style=social)](https://github.com/dongtai-dialect/dongtai-translator/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/dongtai-dialect/dongtai-translator?style=social)](https://github.com/dongtai-dialect/dongtai-translator/network/members)

**智能方言翻译工具 | 支持语音识别 | 18000+语料库**

[English](./README_en.md) | 简体中文

</div>

---

## 功能特色

### 语音输入
- **按住说话**：长按语音按钮，实时语音识别
- **自动翻译**：语音识别后自动翻译为目标方言/普通话
- **语音播报**：翻译结果支持朗读发音

### 双向翻译
- **东台话 → 普通话**：帮助外地人理解东台方言
- **普通话 → 东台话**：帮助本地人学习方言表达

### 方言切换
- 东台城区 / 阜宁话 / 大丰话 / 盐城话

### 语料库
- **18000+** 精选语料
- **10大分类** × **60+子类**
- **5级难度** 递进学习

### 思维导图
- 可视化分类体系
- 层级关系一目了然
- 可导出编辑

### 学习闯关
- 难度分级挑战
- 即时答题反馈
- 学习进度追踪

---

## 快速开始

### 方法一：直接使用（推荐）

1. 下载 `dist/dongtai-translator-v4.html`
2. 使用 **Chrome/Edge/Safari** 浏览器打开
3. 开始使用！

> 注意：语音识别功能需要授权麦克风权限

### 方法二：本地开发

```bash
# 克隆项目
git clone https://github.com/dongtai-dialect/dongtai-translator.git
cd dongtai-translator

# 直接打开
open dist/dongtai-translator-v4.html
```

---

## 技术架构

### 前端技术
- **HTML5** + **CSS3** + **JavaScript** (原生，无框架依赖)
- **Web Speech API** - 语音识别
- **Web Speech Synthesis** - 语音合成
- **LocalStorage** - 本地存储

### 设计理念
- 零依赖：纯原生实现，无需安装任何包
- 响应式：适配手机/平板/桌面
- 离线可用：数据本地存储，无需服务器
- 隐私安全：数据仅存储在本地

---

## 项目结构

```
dongtai-translator/
├── src/
│   └── dongtai-translator-v4.html    # 完整应用源码
├── corpus/
│   ├── dongtai_corpus_full.json      # 18000句完整语料库
│   └── category_index.json           # 分类索引
├── docs/
│   └── dongtai-corpus-design.md     # 语料库设计文档
├── assets/
│   └── mindmap/
│       └── 东台方言_思维导图.drawio  # 思维导图源文件
├── README.md
├── README_en.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## 语料库结构

| 分类 | 句数 | 子类 |
|------|------|------|
| 生存刚需 | 2200 | 日常问候/问路出行/饮食餐饮... |
| 政务办事 | 2000 | 户籍身份/社保医保/教育入学... |
| 医疗健康 | 1800 | 挂号就诊/症状描述/中医养生... |
| 社交融入 | 1800 | 邻里交往/朋友聚会/节庆祝福... |
| 职场沟通 | 1600 | 求职应聘/商务洽谈/劳动权益... |
| 文化生活 | 2000 | 东台非遗/东台美食/方言谚语... |
| 方言文化 | 2000 | 方言成语/亲属称谓/形容词... |
| 专项场景 | 1400 | 银行金融/电信网络/快递物流... |
| 新词新语 | 1200 | 网络用语/流行词汇/科技词汇... |
| 经典场景 | 2000 | 菜市场/公交车上/医院挂号... |

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 贡献方式
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 语料贡献
如果您是东台方言母语者，欢迎贡献语料：
- 每条语料包含：方言原文 + 普通话翻译
- 请确保翻译准确、地道
- 提交时注明来源和背景

---

## 许可证

本项目采用 MIT 许可证。

---

## 致谢

- 东台方言研究学者和母语者们
- 所有贡献者的辛勤付出

---

如果这个项目对您有帮助，请给我们一个 ⭐
