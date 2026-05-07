# 🤖 AI Code Reviewer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Platform">
</p>

<p align="center">
  <b>🌐 多語言文件</b> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.zh-TW.md">繁體中文</a> |
  <a href="README.md">English</a>
</p>

---

## 🎉 專案介紹

**AI Code Reviewer** 是一款輕量級、智能化的程式碼審查 CLI 工具，專為開發者打造。它能夠自動檢測程式碼中的安全漏洞、品質問題、效能瓶頸，並透過 AI 提供專業的改進建議。

### 靈感來源

本專案靈感來源於 GitHub Trending 上的熱門程式碼審查工具，但我們進行了**完全獨立自研**，專注於以下差異化優勢：
- 🔒 **本地優先** - 程式碼不上傳雲端，保護您的程式碼隱私
- ⚡ **零依賴核心** - 純 Python 標準庫實現核心功能
- 🧠 **多 LLM 支援** - 支援 OpenAI、Claude、Ollama、DeepSeek 等多種 AI 後端
- 📊 **增量審查** - 僅審查 Git 變更，節省時間和 API 成本

---

## ✨ 核心特性

| 特性 | 描述 | 狀態 |
|------|------|------|
| 🔐 **安全漏洞檢測** | 自動檢測 OWASP Top 10 安全漏洞、硬編碼金鑰、SQL 注入等 | ✅ |
| 📏 **程式碼品質分析** | 檢測程式碼異味、過長函數、未使用匯入等問題 | ✅ |
| ⚡ **效能最佳化建議** | 識別效能瓶頸，提供最佳化建議 | ✅ |
| 🤖 **AI 智能審查** | 支援 GPT-4、Claude、本地 Ollama 等多種 LLM | ✅ |
| 📈 **增量審查** | 僅審查 Git diff 變更，節省 API 呼叫 | ✅ |
| 📄 **多格式報告** | 支援 Terminal、Markdown、JSON、SARIF 格式 | ✅ |
| 🎨 **精美終端介面** | 使用 Rich 函式庫打造美觀的終端輸出 | ✅ |
| 🔌 **多語言支援** | Python、JavaScript、TypeScript、Java、Go、Rust 等 | ✅ |

---

## 🚀 快速開始

### 環境要求

- **Python**: 3.8 或更高版本
- **作業系統**: Linux、macOS、Windows

### 安裝步驟

#### 方式一：透過 pip 安裝（推薦）

```bash
pip install ai-code-reviewer
```

#### 方式二：從原始碼安裝

```bash
git clone https://github.com/gitstq/ai-code-reviewer.git
cd ai-code-reviewer
pip install -r requirements.txt
pip install -e .
```

#### 方式三：直接執行

```bash
git clone https://github.com/gitstq/ai-code-reviewer.git
cd ai-code-reviewer/src
python cli.py --help
```

### 設定 API 金鑰

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# DeepSeek
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Ollama（本地執行，無需 API 金鑰）
ollama run codellama
```

---

## 📖 詳細使用指南

### 1️⃣ 基礎程式碼分析

分析單個檔案：
```bash
ai-review analyze ./src/main.py
```

分析整個目錄：
```bash
ai-review analyze ./src --format markdown --output report.md
```

### 2️⃣ AI 智能審查

使用 OpenAI GPT-4 審查程式碼：
```bash
ai-review review ./src/main.py --provider openai
```

使用本地 Ollama：
```bash
ai-review review ./src/main.py --provider ollama --model codellama
```

串流輸出：
```bash
ai-review review ./src/main.py --provider openai --stream
```

### 3️⃣ 增量審查（Git Diff）

審查目前工作區的變更：
```bash
ai-review diff .
```

審查與指定分支的差異：
```bash
ai-review diff . --base main
```

### 4️⃣ 產生不同格式報告

```bash
# Markdown 報告
ai-review analyze ./src --format markdown --output report.md

# JSON 報告（適合 CI/CD 整合）
ai-review analyze ./src --format json --output report.json

# SARIF 報告（GitHub/GitLab 相容）
ai-review analyze ./src --format sarif --output report.sarif
```

### 5️⃣ 查看設定

```bash
ai-review config
```

---

## 💡 設計思路與迭代規劃

### 技術選型原因

| 技術 | 選型原因 |
|------|----------|
| **Python** | 生態豐富，開發效率高，適合 CLI 工具 |
| **Click** | 成熟的 Python CLI 框架，支援豐富的命令列特性 |
| **Rich** | 打造精美的終端介面，提升使用者體驗 |
| **GitPython** | 便捷的 Git 操作，支援增量審查 |

### 架構設計

```
ai-code-reviewer/
├── src/
│   ├── core/
│   │   ├── analyzer.py      # 程式碼分析引擎
│   │   ├── llm_client.py    # LLM 客戶端抽象
│   │   └── reporter.py      # 報告產生器
│   ├── rules/               # 檢測規則庫
│   └── cli.py               # 命令列介面
```

### 後續迭代計劃

- [ ] **v1.1.0** - 支援更多程式語言（C++、C#、Ruby）
- [ ] **v1.2.0** - 自訂規則設定
- [ ] **v1.3.0** - IDE 外掛（VS Code、JetBrains）
- [ ] **v1.4.0** - CI/CD 整合最佳化
- [ ] **v2.0.0** - Web 介面版本

---

## 📦 打包與部署指南

### 本地開發

```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
pip install -e ".[all]"

# 執行測試
python -m pytest tests/
```

### 打包發布

```bash
# 建構分發包
python setup.py sdist bdist_wheel

# 上傳到 PyPI
twine upload dist/*
```

---

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！

### 提交 Issue

- 使用清晰的標題描述問題
- 提供復現步驟
- 附上相關程式碼片段和錯誤日誌

### 提交 PR

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立 Pull Request

### 程式碼規範

- 遵循 PEP 8 規範
- 使用 Black 格式化程式碼
- 新增適當的註解和文件

---

## 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">longxiaokong</a>
</p>
