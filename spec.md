# AI Code Reviewer - 项目规格说明书

## 项目概述
轻量级AI代码审查CLI工具，为开发者提供智能化的代码质量分析和改进建议。

## 核心功能
1. **智能代码审查**
   - 支持多种编程语言（Python, JavaScript, TypeScript, Java, Go, Rust等）
   - 基于AST的代码结构分析
   - 代码异味检测
   - 性能瓶颈识别

2. **安全漏洞扫描**
   - 内置常见安全漏洞检测规则（OWASP Top 10）
   - 敏感信息泄露检测
   - 不安全的依赖检测

3. **增量审查模式**
   - Git diff分析，仅审查变更代码
   - PR/MR预审查支持
   - 与CI/CD流程集成

4. **多LLM后端支持**
   - OpenAI GPT-4/GPT-3.5
   - Anthropic Claude
   - 本地Ollama模型
   - DeepSeek API

5. **报告生成**
   - 终端彩色输出
   - Markdown报告
   - JSON格式（供CI集成）
   - SARIF格式（GitHub/GitLab兼容）

## 技术栈
- **语言**: Python 3.8+
- **核心依赖**: 
  - `click` - CLI框架
  - `rich` - 终端美化
  - `tree-sitter` - 代码解析
  - `gitpython` - Git操作
- **零依赖设计**: 纯Python标准库实现核心功能

## 架构设计
```
ai-code-reviewer/
├── src/
│   ├── core/
│   │   ├── analyzer.py      # 代码分析引擎
│   │   ├── llm_client.py    # LLM客户端
│   │   └── reporter.py      # 报告生成器
│   ├── rules/
│   │   ├── security/        # 安全规则
│   │   ├── quality/         # 质量规则
│   │   └── performance/     # 性能规则
│   ├── parsers/             # 语言解析器
│   └── cli.py               # 命令行接口
├── tests/
├── docs/
└── scripts/
```

## 差异化优势
1. 比CodeLens更专注审查场景
2. 增量审查节省时间和API成本
3. 本地优先，保护代码隐私
4. 零依赖，部署简单
