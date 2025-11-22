# Test Cases for pop gen

## Test Case 1: Simple file listing
**Input**: "列出当前目录的所有文件"
**Expected**: `ls -la` or `ls -l`

## Test Case 2: Complex command with options
**Input**: "查找所有 .py 文件并统计行数"
**Expected**: `find . -name "*.py" -exec wc -l {} +` or `find . -name "*.py" | xargs wc -l`

## Test Case 3: Multi-command pipeline
**Input**: "显示当前目录下最大的 5 个文件"
**Expected**: `du -h . | sort -rh | head -5` or similar

## Test Case 4: Git operation
**Input**: "查看 git 状态并显示最近 3 次提交"
**Expected**: `git status && git log -3`

## Test Case 5: System information
**Input**: "显示系统内存使用情况和磁盘空间"
**Expected**: `free -h && df -h` (Linux) or `vm_stat && df -h` (macOS)

## Test Case 6: Dangerous command (should have warning)
**Input**: "删除所有 .tmp 文件"
**Expected**: `# WARNING: This will delete files\nfind . -name "*.tmp" -delete` or `# WARNING: This will delete files\nrm -f *.tmp`

## Test Case 7: Complex find with multiple conditions
**Input**: "查找所有大于 100MB 的 Python 文件"
**Expected**: `find . -name "*.py" -size +100M` or `find . -type f -name "*.py" -size +100M`

## Test Case 8: Process management
**Input**: "查找所有占用 CPU 超过 50% 的进程"
**Expected**: `ps aux | awk '$3 > 50.0 {print}'` or similar

## Test Case 9: Network command
**Input**: "检查 localhost:3000 端口是否开放"
**Expected**: `curl -I http://localhost:3000` or `nc -zv localhost 3000`

## Test Case 10: Environment variable
**Input**: "设置环境变量 PATH 并显示当前工作目录"
**Expected**: `export PATH=$PATH:/new/path && pwd`


