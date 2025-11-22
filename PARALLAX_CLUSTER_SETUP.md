# Parallax 分布式集群设置指南

## 概述

本指南将帮助你将 Azure VM 和 Mac 连接成一个 Parallax 分布式集群，以便在两个节点上共同运行模型。

## 前置要求

1. **Mac 端**:
   - Parallax 已安装
   - Python 3.11-3.13
   - 网络访问（允许外部连接）

2. **Azure VM 端**:
   - SSH 访问权限
   - Python 3.11-3.13
   - 如果有 GPU，需要 CUDA 支持

## 步骤 1: 在 Mac 上启动 Parallax Scheduler

### 1.1 启动调度器（带前端界面）

```bash
# 允许外部连接（重要！）
parallax run -m Qwen/Qwen3-0.6B --host 0.0.0.0
```

### 1.2 获取调度器地址

启动后，在日志中查找类似以下的信息：
```
Scheduler address: 12D3KooWxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**重要**: 保存这个地址，后续在 Azure VM 上需要用到。

### 1.3 访问 Web 界面

打开浏览器访问: `http://localhost:3001`

## 步骤 2: 在 Azure VM 上安装 Parallax

### 2.1 连接到 Azure VM

```bash
ssh muzhi777@4.211.203.33
```

### 2.2 安装 Parallax

```bash
# 检查 Python 版本（需要 3.11-3.13）
python3 --version

# 如果没有 Python 3.11+，安装它
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-pip

# 克隆 Parallax 仓库
git clone https://github.com/GradientHQ/parallax.git
cd parallax

# 创建虚拟环境
python3.11 -m venv ./venv
source ./venv/bin/activate

# 安装 Parallax
# 如果有 GPU，使用:
pip install -e '.[gpu]'
# 如果只有 CPU，使用:
pip install -e '.[cpu]'  # 或者直接 pip install -e .
```

## 步骤 3: 将 Azure VM 加入集群

### 3.1 在 Azure VM 上运行 join 命令

```bash
# 确保在 parallax 目录并激活虚拟环境
cd ~/parallax
source venv/bin/activate

# 加入集群（使用步骤 1.2 中获取的调度器地址）
parallax join -s 12D3KooWxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3.2 验证连接

在 Mac 的 Web 界面（http://localhost:3001）中，你应该能看到：
- Mac 节点（本地）
- Azure VM 节点（远程）

两个节点都应该显示为 "Connected" 状态。

## 步骤 4: 配置模型

### 4.1 在 Web 界面配置

1. 访问 http://localhost:3001
2. 选择模型（例如: Qwen/Qwen3-0.6B）
3. 配置节点资源分配
4. 点击 "Continue"

### 4.2 模型会自动分布

Parallax 会自动将模型分片到两个节点：
- Mac 节点运行部分层
- Azure VM 节点运行部分层

## 步骤 5: 测试集群

### 5.1 使用 pop gen 测试

```bash
# 在 Mac 上测试
pop gen "列出当前目录的所有文件"
```

### 5.2 使用 API 测试

```bash
curl http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-0.6B",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 故障排除

### 问题 1: Azure VM 无法连接到 Mac

**解决方案**:
1. 确保 Mac 上的调度器使用 `--host 0.0.0.0`
2. 检查防火墙设置
3. 如果使用公网 IP，确保 Azure VM 可以访问 Mac 的公网 IP

### 问题 2: 调度器地址找不到

**解决方案**:
- 查看调度器启动日志
- 地址通常在启动后几秒钟内显示

### 问题 3: 节点显示为断开

**解决方案**:
1. 检查网络连接
2. 确保两个节点的时间同步
3. 查看节点日志获取详细错误信息

### 问题 4: 模型加载失败

**解决方案**:
1. 确保两个节点都有足够的磁盘空间
2. 检查模型名称是否正确
3. 查看节点日志了解具体错误

## 网络配置说明

### 本地网络（同一局域网）

如果 Mac 和 Azure VM 在同一局域网：
```bash
# Mac 上
parallax run -m MODEL_NAME --host 0.0.0.0

# Azure VM 上
parallax join  # 不需要 -s 参数，会自动发现
```

### 公网（不同网络）

如果 Mac 和 Azure VM 在不同网络：
```bash
# Mac 上（需要公网 IP 或使用 relay）
parallax run -m MODEL_NAME --host 0.0.0.0 -r  # -r 使用公共 relay

# Azure VM 上
parallax join -s SCHEDULER_ADDRESS -r  # -r 使用公共 relay
```

## 性能优化

1. **GPU 加速**: 如果 Azure VM 有 GPU，确保安装了 CUDA 和相应的驱动
2. **网络带宽**: 确保两个节点之间有足够的带宽
3. **模型分片**: Parallax 会自动优化模型分片，但可以在 Web 界面手动调整

## 安全注意事项

1. **SSH 密钥**: 建议使用 SSH 密钥而不是密码
2. **防火墙**: 只开放必要的端口
3. **访问控制**: 考虑使用 VPN 或私有网络

## 下一步

集群设置完成后，你可以：
1. 使用 `pop gen` 命令进行自然语言到命令的转换
2. 通过 API 调用分布式模型
3. 在 Web 界面监控集群状态和性能

