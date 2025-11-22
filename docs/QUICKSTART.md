# 快速启动指南

## 前置要求

### 确保 Parallax 已安装

如果遇到 `parallax: command not found` 错误，请先安装 Parallax：

```bash
# 检查 Parallax 是否安装
which parallax

# 如果未安装，使用 pipx（推荐）
pipx install git+https://github.com/GradientHQ/parallax.git
pipx ensurepath

# 或从源码安装（详见 docs/SETUP_PARALLAX.md）
```

### 确保 PATH 配置正确

```bash
# 检查 PATH
echo $PATH | grep .local/bin

# 如果未配置，添加到 ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## 启动 Parallax 服务器

### 方法 1: 前台运行（推荐用于调试）

```bash
parallax run -m Qwen/Qwen3-0.6B --host 0.0.0.0
```

### 方法 2: 后台运行

```bash
nohup parallax run -m Qwen/Qwen3-0.6B --host 0.0.0.0 > parallax.log 2>&1 &
```

### 验证服务器运行

```bash
# 检查端口
lsof -i :3000  # API 端口
lsof -i :3001  # Web 界面端口

# 测试 API
curl http://localhost:3000/v1/models

# 访问 Web 界面
open http://localhost:3001
```

## 使用 pop gen

```bash
# 配置（首次使用）
pop configure

# 生成命令
pop gen "列出当前目录的所有文件"
```

## 故障排除

如果 Parallax 无法启动：

1. **检查模型是否可用**
   ```bash
   # 查看 Parallax 支持的模型
   parallax --help
   ```

2. **检查端口占用**
   ```bash
   lsof -i :3000
   lsof -i :3001
   ```

3. **查看日志**
   ```bash
   tail -f parallax.log
   ```

4. **使用诊断脚本**
   ```bash
   ./docs/diagnose_parallax.sh
   ```

