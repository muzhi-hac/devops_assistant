# 安装指南

## 快速安装

### 使用 pip

```bash
pip install -r requirements.txt
pip install -e .
```

### 使用 pipx (推荐)

```bash
pipx install git+https://github.com/muzhi-hac/devops_assistant.git
```

## 详细步骤

### 1. 克隆仓库

```bash
git clone https://github.com/muzhi-hac/devops_assistant.git
cd devops_assistant
```

### 2. 创建虚拟环境（可选但推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装项目

```bash
pip install -e .
```

### 5. 配置 Parallax

确保 Parallax 服务器正在运行：

```bash
# 安装 Parallax (如果未安装)
pipx install git+https://github.com/GradientHQ/parallax.git

# 启动 Parallax 服务器
parallax run -m Qwen/Qwen3-0.6B
```

### 6. 配置 OpsPilot

```bash
pop configure
```

## 验证安装

```bash
pop --version
pop --help
```

## 故障排除

### 问题: 找不到 pop 命令

**解决方案**:
- 确保虚拟环境已激活
- 检查 PATH 环境变量
- 重新安装: `pip install -e .`

### 问题: Parallax 连接失败

**解决方案**:
- 确保 Parallax 服务器正在运行
- 检查配置文件中的 `api_base` 设置
- 验证端口是否可访问

### 问题: 依赖安装失败

**解决方案**:
- 升级 pip: `pip install --upgrade pip`
- 使用 Python 3.10+
- 检查网络连接


