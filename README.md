# 🤖 AI Code Reviewer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Platform">
</p>

<p align="center">
  <b>🌐 多语言文档</b> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.zh-TW.md">繁體中文</a> |
  <a href="README.md">English</a>
</p>

---

## 🎉 项目介绍

**AI Code Reviewer** 是一款轻量级、智能化的代码审查 CLI 工具，专为开发者打造。它能够自动检测代码中的安全漏洞、质量问题、性能瓶颈，并通过 AI 提供专业的改进建议。

### 灵感来源

本项目灵感来源于 GitHub Trending 上的热门代码审查工具，但我们进行了**完全独立自研**，专注于以下差异化优势：
- 🔒 **本地优先** - 代码不上传云端，保护您的代码隐私
- ⚡ **零依赖核心** - 纯 Python 标准库实现核心功能
- 🧠 **多 LLM 支持** - 支持 OpenAI、Claude、Ollama、DeepSeek 等多种 AI 后端
- 📊 **增量审查** - 仅审查 Git 变更，节省时间和 API 成本

---

## ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| 🔐 **安全漏洞检测** | 自动检测 OWASP Top 10 安全漏洞、硬编码密钥、SQL 注入等 | ✅ |
| 📏 **代码质量分析** | 检测代码异味、过长函数、未使用导入等问题 | ✅ |
| ⚡ **性能优化建议** | 识别性能瓶颈，提供优化建议 | ✅ |
| 🤖 **AI 智能审查** | 支持 GPT-4、Claude、本地 Ollama 等多种 LLM | ✅ |
| 📈 **增量审查** | 仅审查 Git diff 变更，节省 API 调用 | ✅ |
| 📄 **多格式报告** | 支持 Terminal、Markdown、JSON、SARIF 格式 | ✅ |
| 🎨 **精美终端界面** | 使用 Rich 库打造美观的终端输出 | ✅ |
| 🔌 **多语言支持** | Python、JavaScript、TypeScript、Java、Go、Rust 等 | ✅ |

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Linux、macOS、Windows

### 安装步骤

#### 方式一：通过 pip 安装（推荐）

```bash
pip install ai-code-reviewer
```

#### 方式二：从源码安装

```bash
git clone https://github.com/gitstq/ai-code-reviewer.git
cd ai-code-reviewer
pip install -r requirements.txt
pip install -e .
```

#### 方式三：直接运行

```bash
git clone https://github.com/gitstq/ai-code-reviewer.git
cd ai-code-reviewer/src
python cli.py --help
```

### 配置 API 密钥

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# DeepSeek
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Ollama（本地运行，无需 API 密钥）
ollama run codellama
```

---

## 📖 详细使用指南

### 1️⃣ 基础代码分析

分析单个文件：
```bash
ai-review analyze ./src/main.py
```

分析整个目录：
```bash
ai-review analyze ./src --format markdown --output report.md
```

### 2️⃣ AI 智能审查

使用 OpenAI GPT-4 审查代码：
```bash
ai-review review ./src/main.py --provider openai
```

使用本地 Ollama：
```bash
ai-review review ./src/main.py --provider ollama --model codellama
```

流式输出：
```bash
ai-review review ./src/main.py --provider openai --stream
```

### 3️⃣ 增量审查（Git Diff）

审查当前工作区的变更：
```bash
ai-review diff .
```

审查与指定分支的差异：
```bash
ai-review diff . --base main
```

### 4️⃣ 生成不同格式报告

```bash
# Markdown 报告
ai-review analyze ./src --format markdown --output report.md

# JSON 报告（适合 CI/CD 集成）
ai-review analyze ./src --format json --output report.json

# SARIF 报告（GitHub/GitLab 兼容）
ai-review analyze ./src --format sarif --output report.sarif
```

### 5️⃣ 查看配置

```bash
ai-review config
```

---

## 💡 设计思路与迭代规划

### 技术选型原因

| 技术 | 选型原因 |
|------|----------|
| **Python** | 生态丰富，开发效率高，适合 CLI 工具 |
| **Click** | 成熟的 Python CLI 框架，支持丰富的命令行特性 |
| **Rich** | 打造精美的终端界面，提升用户体验 |
| **GitPython** | 便捷的 Git 操作，支持增量审查 |

### 架构设计

```
ai-code-reviewer/
├── src/
│   ├── core/
│   │   ├── analyzer.py      # 代码分析引擎
│   │   ├── llm_client.py    # LLM 客户端抽象
│   │   └── reporter.py      # 报告生成器
│   ├── rules/               # 检测规则库
│   └── cli.py               # 命令行接口
```

### 后续迭代计划

- [ ] **v1.1.0** - 支持更多编程语言（C++、C#、Ruby）
- [ ] **v1.2.0** - 自定义规则配置
- [ ] **v1.3.0** - IDE 插件（VS Code、JetBrains）
- [ ] **v1.4.0** - CI/CD 集成优化
- [ ] **v2.0.0** - Web 界面版本

---

## 📦 打包与部署指南

### 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -e ".[all]"

# 运行测试
python -m pytest tests/
```

### 打包发布

```bash
# 构建分发包
python setup.py sdist bdist_wheel

# 上传到 PyPI
twine upload dist/*
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 提交 Issue

- 使用清晰的标题描述问题
- 提供复现步骤
- 附上相关代码片段和错误日志

### 提交 PR

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 规范
- 使用 Black 格式化代码
- 添加适当的注释和文档

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">longxiaokong</a>
</p>
