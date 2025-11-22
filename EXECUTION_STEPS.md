# Parallax 集群设置 - 执行步骤

## ✅ 已完成的步骤

### 步骤 1: Mac 上启动调度器 ✅
调度器已在后台运行，PID: 72658
- 模型: Qwen/Qwen3-0.6B
- 端口: 3001 (Web界面), 3000 (API)
- 日志文件: `parallax_scheduler.log`

查看调度器状态:
```bash
tail -f parallax_scheduler.log
```

访问 Web 界面:
```
http://localhost:3001
```

## 📋 待执行的步骤

### 步骤 2: 获取调度器地址

调度器地址通常在启动后几秒钟内显示。可以通过以下方式获取：

**方法 1: 查看日志**
```bash
tail -f parallax_scheduler.log | grep -i "scheduler\|address\|peer"
```

**方法 2: 访问 Web 界面**
1. 打开浏览器访问 `http://localhost:3001`
2. 在界面上查找 "Scheduler Address" 或类似信息
3. 地址格式类似: `12D3KooWxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**方法 3: 检查 API**
```bash
curl http://localhost:3001/api/status 2>/dev/null | grep -i address
```

### 步骤 3: 在 Azure VM 上安装 Parallax

运行安装脚本（需要 SSH 密码）:
```bash
./install_parallax_azure.sh
```

或者手动执行:
```bash
ssh muzhi777@4.211.203.33

# 在 Azure VM 上执行
git clone https://github.com/GradientHQ/parallax.git ~/parallax
cd ~/parallax
python3.11 -m venv ./venv  # 或 python3.12
source ./venv/bin/activate
pip install -e '.[gpu]'  # 如果有 GPU，否则用 pip install -e .
```

### 步骤 4: 将 Azure VM 加入集群

获取调度器地址后，运行:
```bash
./join_azure_to_cluster.sh <SCHEDULER_ADDRESS>
```

例如:
```bash
./join_azure_to_cluster.sh 12D3KooWxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

或者手动执行:
```bash
ssh muzhi777@4.211.203.33
cd ~/parallax
source venv/bin/activate
parallax join -s <SCHEDULER_ADDRESS>
```

### 步骤 5: 验证集群

1. **在 Mac 上访问 Web 界面**
   ```
   http://localhost:3001
   ```

2. **检查节点状态**
   - 应该看到两个节点：Mac (本地) 和 Azure VM (远程)
   - 两个节点都应该显示为 "Connected" 状态

3. **测试 API**
   ```bash
   curl http://localhost:3000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model": "Qwen/Qwen3-0.6B", "messages": [{"role": "user", "content": "Hello"}]}'
   ```

4. **使用 pop gen 测试**
   ```bash
   pop gen "列出当前目录的所有文件"
   ```

## 🔧 故障排除

### 问题 1: 找不到调度器地址

**解决方案**:
- 等待更长时间（调度器可能需要 30-60 秒完全启动）
- 检查日志: `tail -100 parallax_scheduler.log`
- 访问 Web 界面查看

### 问题 2: SSH 连接失败

**解决方案**:
- 确保 SSH 密钥已配置，或准备好密码
- 测试连接: `ssh muzhi777@4.211.203.33`
- 如果使用密码，脚本会提示输入

### 问题 3: Azure VM 无法加入集群

**解决方案**:
- 确保 Mac 上的调度器使用 `--host 0.0.0.0`
- 检查防火墙设置
- 如果 Mac 在 NAT 后，可能需要使用公共 relay:
  ```bash
  # Mac 上
  parallax run -m MODEL --host 0.0.0.0 -r
  
  # Azure VM 上
  parallax join -s ADDRESS -r
  ```

### 问题 4: 节点显示为断开

**解决方案**:
- 检查网络连接
- 确保两个节点的时间同步
- 查看节点日志获取详细错误

## 📝 当前状态

- ✅ Mac 调度器已启动
- ⏳ 等待获取调度器地址
- ⏳ 需要在 Azure VM 上安装 Parallax
- ⏳ 需要将 Azure VM 加入集群

## 🚀 快速命令参考

```bash
# 查看调度器日志
tail -f parallax_scheduler.log

# 停止调度器
pkill -f "parallax run"

# 重启调度器
./start_scheduler.sh Qwen/Qwen3-0.6B

# 安装 Parallax 到 Azure VM
./install_parallax_azure.sh

# 加入集群（需要先获取地址）
./join_azure_to_cluster.sh <ADDRESS>
```

