# 贡献指南

感谢您对东台方言项目的兴趣！我们欢迎各种形式的贡献。

## 如何贡献

### 1. 报告问题

如果您发现了 bug 或有功能建议，请：
1. 搜索现有 issues 确保不是重复
2. 创建新的 issue
3. 详细描述问题或建议

### 2. 提交代码

#### 分支命名规范
- `feature/` - 新功能
- `bugfix/` - Bug 修复
- `docs/` - 文档更新
- `corpus/` - 语料贡献

#### Pull Request 流程
1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到 GitHub
5. 创建 Pull Request

### 3. 语料贡献

如果您是东台方言母语者，欢迎贡献语料！

#### 语料格式
```json
{
  "dongtai": "你上哪块去呃？",
  "mandarin": "你去哪里？",
  "category": "1.1 日常问候",
  "difficulty": 1
}
```

#### 贡献要求
- 方言原文需地道、自然
- 普通话翻译需准确、流畅
- 标注正确的分类和难度
- 说明使用场景（如有）

### 4. 文档贡献

- 修正错别字
- 完善使用说明
- 翻译成其他语言
- 添加使用案例

## 开发设置

```bash
# 克隆
git clone https://github.com/dongtai-dialect/dongtai-translator.git
cd dongtai-translator

# 开发（直接编辑 src/ 目录）
# 完成后复制到 dist/ 发布
```

## 代码规范

- 使用 2 空格缩进
- 变量命名使用 camelCase
- 注释使用中文/英文均可
- 确保代码可通过 HTML 验证

## 许可证

通过贡献代码，您同意将您的贡献以 MIT 许可证发布。
