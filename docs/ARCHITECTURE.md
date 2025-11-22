# 架构文档

## 系统架构

Parallax OpsPilot 采用模块化设计，主要组件如下：

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                         │
│                    (CLI: pop command)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Command Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │   gen    │  │ configure │  │  version │                │
│  └──────────┘  └──────────┘  └──────────┘                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Client     │  │   Config     │  │   Utils      │    │
│  │  (Parallax)  │  │  Manager     │  │  (System)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Parallax Inference Layer                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Distributed Model Serving                    │  │
│  │  ┌──────────┐              ┌──────────┐            │  │
│  │  │   Mac    │◄────────────►│  Azure   │            │  │
│  │  │ Scheduler│              │   VM     │            │  │
│  │  └──────────┘              └──────────┘            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块

### 1. `src/main.py` - CLI 入口点

**职责**:
- 定义 Typer CLI 应用
- 处理用户命令（gen, configure, version）
- 流式输出管理
- 命令后处理和用户交互

**关键函数**:
- `gen()`: 命令生成主函数
- `configure()`: 配置管理
- `_strip_markdown_code_blocks()`: 命令清理

### 2. `src/client.py` - Parallax 客户端

**职责**:
- 封装 OpenAI SDK 客户端
- 处理流式 API 调用
- 错误处理和重试逻辑

**关键类**:
- `ParallaxClient`: 主客户端类
- `ParallaxConnectionError`: 自定义异常

### 3. `src/config.py` - 配置管理

**职责**:
- 配置文件加载和保存
- 配置验证
- 默认值管理

**关键类**:
- `AppConfig`: Pydantic 配置模型
- `ConfigManager`: 配置管理器

### 4. `src/prompts.py` - 提示词管理

**职责**:
- 定义 LLM 系统提示词
- 确保输出格式一致性

### 5. `src/utils.py` - 工具函数

**职责**:
- 系统信息检测（OS, Shell）
- 辅助函数

## 数据流

### 命令生成流程

```
1. User Input: "列出所有文件"
   │
   ▼
2. get_system_info() → "macOS 24.6.0 /bin/zsh"
   │
   ▼
3. ParallaxClient.generate_command_stream()
   │
   ├─ System Prompt: GEN_COMMAND_SYSTEM_PROMPT
   ├─ User Message: "Environment: macOS 24.6.0 /bin/zsh\nUser request: 列出所有文件"
   └─ Model: Qwen/Qwen3-0.6B
   │
   ▼
4. Stream Response (实时输出)
   │
   ├─ Filter reasoning tags (<think>...</think>)
   ├─ Accumulate chunks
   └─ Display in real-time
   │
   ▼
5. Post-processing
   │
   ├─ Remove markdown code blocks
   ├─ Extract actual command
   └─ Clean explanation text
   │
   ▼
6. User Interaction
   │
   ├─ Display in Panel
   ├─ Prompt: [E]xecute, [C]opy, [A]bort
   └─ Execute/Copy/Abort
```

## 安全机制

1. **命令验证**: 提取后验证命令格式
2. **危险检测**: 识别危险命令并添加警告
3. **人工确认**: 执行前必须用户确认
4. **本地处理**: 所有数据在本地处理

## 扩展性

### 添加新命令

1. 在 `src/main.py` 中添加新的 `@app.command()` 函数
2. 如需新的客户端方法，在 `src/client.py` 中添加
3. 更新文档和测试用例

### 支持新模型

1. 更新 `src/config.py` 中的默认模型
2. 确保 Parallax 支持该模型
3. 测试命令生成质量

## 性能优化

1. **流式输出**: 实时显示，减少等待时间
2. **缓存配置**: 配置加载后缓存
3. **连接复用**: 客户端实例复用
4. **分布式推理**: 跨设备共享 GPU 资源


