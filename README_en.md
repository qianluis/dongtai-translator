# Dongtai Dialect Real-time Translator

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/dongtai-dialect/dongtai-translator?style=social)](https://github.com/dongtai-dialect/dongtai-translator/stargazers)

**Smart Dialect Translation Tool | Voice Recognition | 18000+ Corpus**

English | [简体中文](./README.md)

</div>

---

## Features

### Voice Input
- **Press and Speak**: Long press the voice button for real-time speech recognition
- **Auto Translate**: Automatically translates after speech recognition
- **Voice Playback**: Read aloud the translation results

### Bidirectional Translation
- **Dongtai → Mandarin**: Help outsiders understand Dongtai dialect
- **Mandarin → Dongtai**: Help locals learn dialect expressions

### Dialect Switching
- Dongtai City / Funing / Dafeng / Yancheng

### Corpus
- **18000+** curated phrases
- **10 Major Categories** × **60+ Subcategories**
- **5 Difficulty Levels** progressive learning

### Mind Map
- Visual classification system
- Clear hierarchical relationships
- Exportable for editing

### Learning Quiz
- Difficulty-based challenges
- Instant feedback
- Progress tracking

---

## Quick Start

### Method 1: Direct Use (Recommended)

1. Download `dist/dongtai-translator-v4.html`
2. Open with **Chrome/Edge/Safari** browser
3. Start using!

### Method 2: Local Development

```bash
# Clone project
git clone https://github.com/dongtai-dialect/dongtai-translator.git
cd dongtai-translator

# Open
open dist/dongtai-translator-v4.html
```

---

## Tech Stack

### Frontend
- **HTML5** + **CSS3** + **JavaScript** (vanilla, no framework)
- **Web Speech API** - Speech recognition
- **Web Speech Synthesis** - Speech synthesis
- **LocalStorage** - Local storage

### Design Principles
- Zero dependencies: Pure vanilla implementation
- Responsive: Adapts to mobile/tablet/desktop
- Offline available: Local storage, no server needed
- Privacy secure: Data stored locally only

---

## Project Structure

```
dongtai-translator/
├── src/
│   └── dongtai-translator-v4.html
├── corpus/
│   ├── dongtai_corpus_full.json
│   └── category_index.json
├── docs/
│   └── dongtai-corpus-design.md
├── assets/
│   └── mindmap/
│       └── mindmap.drawio
├── README.md
├── README_en.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Show your support

Give a ⭐ if this project helped you!
