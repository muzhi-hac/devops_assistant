# 自动化测试结果

## 运行测试

```bash
# 运行所有测试
python3 tests/run_automated_tests.py

# 显示详细信息
python3 tests/run_automated_tests.py --verbose
```

## 测试报告

测试运行器会自动：
1. 从 `docs/TEST_CASES.md` 读取测试用例
2. 执行每个测试用例
3. 提取生成的命令
4. 与期望结果对比
5. 生成测试报告

## 测试结果格式

```
Parallax OpsPilot - Automated Test Runner

Running 10 test cases...

Running Test Case 1: Simple file listing... ✓ PASS
Running Test Case 2: Complex command with options... ✓ PASS
...

============================================================
Test Results
============================================================

Total Tests: 10
Passed: 10
Failed: 0
Pass Rate: 100.0%
```

## 对比逻辑

测试运行器使用智能对比算法：

1. **精确匹配**: 完全相同的命令
2. **子串匹配**: 期望命令是实际命令的子串
3. **部分匹配**: 至少 70% 的关键词匹配
4. **命令匹配**: 主命令（第一个词）相同

这样可以处理：
- 命令参数顺序不同
- 额外的选项
- 注释和警告信息

## 更新测试结果

每次运行测试后，结果会显示在终端。可以将输出保存到文件：

```bash
python3 tests/run_automated_tests.py --verbose > test_results.txt
```

