# Parallax 安装和配置指南

## 问题诊断

如果遇到 `parallax: command not found` 错误，可能是以下原因：

1. Parallax 未安装
2. 符号链接损坏（指向不存在的路径）
3. PATH 环境变量未配置

## 安装 Parallax

### 方法 1: 使用 pipx（推荐）

```bash
pipx install git+https://github.com/GradientHQ/parallax.git
pipx ensurepath
```

### 方法 2: 从源码安装（macOS）

```bash
# 克隆仓库
git clone https://github.com/GradientHQ/parallax.git
cd parallax

# 创建虚拟环境
python3.12 -m venv ./venv
source ./venv/bin/activate

# 安装（macOS）
pip install -e '.[mac]'

# 创建符号链接到 PATH
ln -sf $(pwd)/venv/bin/parallax ~/.local/bin/parallax
```

### 方法 3: 使用虚拟环境（临时）

```bash
cd /tmp
git clone https://github.com/GradientHQ/parallax.git parallax-repo
cd parallax-repo
python3.12 -m venv ./venv
source ./venv/bin/activate
pip install -e '.[mac]'

# 创建符号链接
ln -sf /tmp/parallax-repo/venv/bin/parallax ~/.local/bin/parallax
```

## 配置 PATH

确保 `~/.local/bin` 在 PATH 中：

```bash
# 添加到 ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# 重新加载配置
source ~/.zshrc
```

## 验证安装

```bash
# 检查命令是否可用
which parallax

# 检查版本
parallax --version

# 查看帮助
parallax --help
```

## 启动 Parallax 服务器

```bash
# 前台运行（推荐用于调试）
parallax run -m Qwen/Qwen3-0.6B --host 0.0.0.0

# 后台运行
nohup parallax run -m Qwen/Qwen3-0.6B --host 0.0.0.0 > parallax.log 2>&1 &
```

## 故障排除

### 问题 1: 符号链接损坏

**症状**: `parallax: command not found` 但 `~/.local/bin/parallax` 存在

**解决**:
```bash
# 删除损坏的链接
rm ~/.local/bin/parallax

# 重新创建（使用实际路径）
ln -sf /path/to/parallax/venv/bin/parallax ~/.local/bin/parallax
```

### 问题 2: PATH 未配置

**症状**: `which parallax` 返回空

**解决**:
```bash
# 临时添加
export PATH="$HOME/.local/bin:$PATH"

# 永久添加（添加到 ~/.zshrc）
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 问题 3: 虚拟环境路径变化

如果 Parallax 安装在临时目录（如 `/tmp`），重启后可能丢失。

**解决**: 使用 pipx 安装，或安装到永久目录。

