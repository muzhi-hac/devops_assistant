# 快速启动指南

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

