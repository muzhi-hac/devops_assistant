# 测试说明

## 运行自动化测试

### 方法 1: 使用测试运行器（推荐）

```bash
# 运行所有测试
python3 tests/test_runner.py

# 显示详细信息
python3 tests/test_runner.py --verbose
```

### 方法 2: 使用 shell 脚本

```bash
./tests/run_tests.sh
```

### 方法 3: 使用 pytest

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_config.py
pytest tests/test_utils.py
pytest tests/test_client.py
```

## 测试结构

- `test_runner.py` - 自动化测试运行器，从 TEST_CASES.md 读取测试用例并执行
- `test_config.py` - 配置管理单元测试
- `test_utils.py` - 工具函数单元测试
- `test_client.py` - Parallax 客户端单元测试
- `test_main.py` - CLI 主模块测试

## 测试用例来源

测试用例定义在 `docs/TEST_CASES.md` 中，测试运行器会自动读取并执行。

## 前置要求

1. **安装项目**:
   ```bash
   pip install -e .
   ```

2. **启动 Parallax 服务器**:
   ```bash
   parallax run -m Qwen/Qwen3-0.6B --host 0.0.0.0
   ```

3. **确保 pop 命令可用**:
   ```bash
   which pop
   # 如果不可用，确保 ~/.local/bin 在 PATH 中
   export PATH="$HOME/.local/bin:$PATH"
   ```

## 测试输出

测试运行器会显示：
- 每个测试用例的执行状态（✓ PASS / ✗ FAIL）
- 测试摘要（总数、通过数、失败数、通过率）
- 详细结果表（如果使用 --verbose 或测试失败）

## 示例输出

```
Parallax OpsPilot - Automated Test Runner

Running 10 test cases...

Running Test Case 1: Simple file listing... ✓ PASS
Running Test Case 2: Complex command with options... ✓ PASS
...

============================================================
Test Results
============================================================

╭─ Summary ────────────────────────────────────────────────╮
│ Total Tests: 10                                            │
│ Passed: 10                                                 │
│ Failed: 0                                                  │
│ Pass Rate: 100.0%                                          │
╰────────────────────────────────────────────────────────────╯
```

