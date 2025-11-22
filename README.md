# Parallax OpsPilot 🚀

> **AI-Powered DevOps Command Assistant** - A terminal-based AI copilot that generates shell commands from natural language using distributed inference.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Hackathon](https://img.shields.io/badge/Hackathon-Project-orange.svg)](https://github.com/muzhi-hac/devops_assistant)

## 📖 项目简介

Parallax OpsPilot 是一个基于 AI 的 DevOps 命令行助手，通过自然语言生成精确的 shell 命令。项目使用 [GradientHQ/Parallax](https://github.com/GradientHQ/parallax) 分布式推理框架，支持在多个设备间共享 GPU 资源，实现高效的本地 AI 推理。

### ✨ 核心特性

- 🤖 **自然语言转命令**: 用中文或英文描述需求，自动生成对应的 shell 命令
- 🔒 **隐私保护**: 所有推理在本地完成，数据不会上传到云端
- 🌐 **分布式推理**: 支持跨设备（Mac、Linux、Azure VM）分布式运行模型
- 🎯 **智能识别**: 自动检测操作系统和 shell 类型，生成兼容的命令
- ⚠️ **安全提示**: 对危险命令（如删除、格式化）自动添加警告
- 🎨 **美观界面**: 使用 Rich 库提供彩色输出和实时流式响应

## 🏗️ 架构设计

```
┌─────────────────┐
│   User Input    │
│  (Natural Lang) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   pop gen       │────▶│  Parallax    │────▶│   LLM       │
│   Command       │     │  Client       │     │  Inference  │
└─────────────────┘     └──────────────┘     └─────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────┐
│  Command        │     │  Distributed │
│  Extraction     │     │  Cluster     │
│  & Validation   │     │  (Mac+Azure) │
└─────────────────┘     └──────────────┘
```

## 🚀 快速开始

### 前置要求

- Python 3.10+
- [Parallax](https://github.com/GradientHQ/parallax) 推理服务器
- macOS 或 Linux

### 安装

```bash
# 克隆仓库
git clone https://github.com/muzhi-hac/devops_assistant.git
cd devops_assistant

# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .
```

### 配置

```bash
# 交互式配置
pop configure

# 或手动编辑配置文件
# ~/.config/pop/config.yaml
```

配置文件示例：
```yaml
api_base: http://localhost:3000/v1
api_key: parallax
model: Qwen/Qwen3-0.6B
```

### 使用示例

```bash
# 生成命令
pop gen "列出当前目录的所有文件"

# 复杂查询
pop gen "查找所有 .py 文件并统计行数"

# Git 操作
pop gen "查看 git 状态并显示最近 3 次提交"
```

## 📚 功能说明

### 1. 命令生成 (`pop gen`)

将自然语言转换为 shell 命令：

```bash
$ pop gen "显示系统内存使用情况"
╭───────────────────────────── Generated Command ──────────────────────────────╮
│ vm_stat                                                                       │
╰───────────────────────────────────────────────────────────────────────────────╯

[E]xecute, [C]opy, [A]bort? [A]:
```

**特性**:
- 实时流式输出
- 自动检测 OS 和 Shell
- 智能命令提取和清理
- 危险命令警告

### 2. 配置管理 (`pop configure`)

交互式配置 Parallax 连接：

```bash
$ pop configure
API Base URL [http://localhost:3000/v1]: 
Model Name [Qwen/Qwen3-0.6B]: 

✓ Configuration saved successfully!
```

### 3. 分布式集群支持

支持在多个设备间分布式运行模型：

- **Mac (Scheduler)**: 运行调度器和部分模型层
- **Azure VM (Worker)**: 运行部分模型层，共享 GPU 资源

详见 [PARALLAX_CLUSTER_SETUP.md](PARALLAX_CLUSTER_SETUP.md)

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试用例
./test_gen.sh

# 查看测试结果
cat TEST_RESULTS.md
```

详细测试用例和结果见 [TEST_CASES.md](docs/TEST_CASES.md)

## 📁 项目结构

```
devops_assistant/
├── src/
│   ├── __init__.py          # 包初始化
│   ├── main.py              # CLI 入口点
│   ├── config.py            # 配置管理
│   ├── client.py            # Parallax 客户端
│   ├── prompts.py           # LLM 提示词
│   └── utils.py             # 工具函数
├── docs/
│   ├── TEST_CASES.md        # 测试用例
│   └── ARCHITECTURE.md      # 架构文档
├── README.md                # 项目说明
├── requirements.txt         # 依赖列表
├── pyproject.toml          # 项目配置
└── setup.py                # 安装脚本
```

## 🔧 技术栈

- **CLI 框架**: [Typer](https://typer.tiangolo.com/) - 现代 Python CLI 框架
- **UI 渲染**: [Rich](https://rich.readthedocs.io/) - 终端美化库
- **AI 推理**: [Parallax](https://github.com/GradientHQ/parallax) - 分布式推理框架
- **API 客户端**: [OpenAI Python SDK](https://github.com/openai/openai-python) - 兼容 OpenAI API
- **配置管理**: [Pydantic](https://docs.pydantic.dev/) - 数据验证
- **YAML 解析**: [PyYAML](https://pyyaml.org/) - YAML 文件处理

## 🎯 使用场景

1. **快速命令生成**: 忘记命令语法时，用自然语言描述需求
2. **跨平台兼容**: 自动生成适配当前系统的命令
3. **学习工具**: 通过生成的命令学习 shell 操作
4. **DevOps 自动化**: 集成到 CI/CD 流程中自动生成脚本

## 🔒 安全特性

- ✅ **危险命令警告**: 自动检测并警告危险操作
- ✅ **人工确认**: 执行前需要用户确认
- ✅ **本地推理**: 所有数据在本地处理，不上传云端
- ✅ **命令预览**: 执行前显示完整命令

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

Apache 2.0 License

## 🙏 致谢

- [GradientHQ/Parallax](https://github.com/GradientHQ/parallax) - 分布式推理框架
- [Typer](https://typer.tiangolo.com/) - CLI 框架
- [Rich](https://rich.readthedocs.io/) - 终端美化

## 📞 联系方式

- GitHub: [muzhi-hac/devops_assistant](https://github.com/muzhi-hac/devops_assistant)
- Issues: [GitHub Issues](https://github.com/muzhi-hac/devops_assistant/issues)

---

**Made with ❤️ for Hackathon**


