# Multi-Agent Financial Analysis System

## ✅ 已完成的组件

### 1. Baseline Agent (`agents/baseline_agent.py`)
- 无工具调用的基础 LLM
- 仅依赖训练知识回答问题

### 2. Single Agent (`agents/single_agent.py`)
- 单个 LLM 可访问全部 7 个工具
- 能够执行多步骤推理和工具链式调用

### 3. Multi-Agent System (Orchestrator + Specialists + Critic)

#### 架构组件：
- **Orchestrator** (`agents/multi-agent/orchestrator.py`)
  - 分析问题并决定激活哪些专家
  - 为每个专家创建具体的子任务

- **Market Specialist** (`agents/multi-agent/market_specialist.py`)
  - 处理股票价格、市场状态、涨跌幅数据
  - 工具：价格数据、市场状态、热门股票、行业股票列表

- **Fundamentals Specialist** (`agents/multi-agent/fundamentals_specialist.py`)
  - 处理公司基本面数据（P/E比率、EPS、市值等）
  - 工具：公司概览、数据库查询、行业筛选

- **Sentiment Specialist** (`agents/multi-agent/sentiment_specialist.py`)
  - 处理新闻情绪分析
  - 工具：新闻情绪、数据库查询

- **Critic** (`agents/multi-agent/critic.py`)
  - 验证专家答案是否与原始工具数据一致
  - 检测虚构数据、错误排名等问题
  - 为每个答案提供置信度评分

- **Synthesizer** (`agents/multi-agent/synthesizer.py`)
  - 将多个专家的答案合成为一个连贯的最终答案
  - 解决矛盾、组织信息层次

## 📊 使用方法

### 运行单个系统测试：

```python
from multi_agent_system import run_multi_agent

# 简单测试
result = run_multi_agent("What is Apple's P/E ratio?")

# 结果包含：
# - final_answer: 最终答案（字符串）
# - agent_results: 专家结果列表（List[AgentResult]）
# - elapsed_sec: 执行时间（浮点数）
# - architecture: 架构名称（字符串）
```

### 运行综合测试：

```bash
# 测试多智能体系统
python test_multi_agent.py

# 综合测试（多种问题类型）
python test_multi_comprehensive.py

# 测试 Baseline 和 Single Agent
python quick_test.py
```

## 🔑 关键特性
### Multi-Agent 架构
## Multi-Agent 架构

**Orchestrator + Specialists + Critic** 架构：

```
用户问题
    ↓
Orchestrator (分析问题，决定激活哪些专家)
    ↓
┌───────────┬───────────┬───────────┐
│  Market   │Fundamentals│ Sentiment │ (并行/顺序执行)
│ Specialist│ Specialist │ Specialist│
└─────┬─────┴─────┬─────┴─────┬─────┘
      └───────────┴───────────┘
                  ↓
             Critic (验证每个专家的答案)
                  ↓
            Synthesizer (合成最终答案)
                  ↓
              最终答案
```


### Multi-Agent 系统优势：
1. **专业化分工**：每个专家只处理特定领域的问题
2. **更少的工具混淆**：专家只看到相关工具，减少错误选择
3. **内置验证**：Critic 自动检测虚构数据和错误
4. **并行能力**：可以同时激活多个专家（当前是顺序执行，但架构支持并行）
5. **透明度高**：可以追踪每个专家的工具调用和推理过程

### 置信度评分：
- Critic 为每个专家答案提供 0-100% 的置信度
- 低置信度表示可能存在虚构数据或逻辑问题
- 帮助评估器判断答案质量

## 📁 项目结构

```
MiniProject_3/
├── agents/                        # 所有智能体实现
│   ├── baseline_agent.py          # Baseline (无工具)
│   ├── single_agent.py            # Single Agent (7个工具)
│   ├── multi_agent_runner.py      # Multi-Agent 主入口 ⭐
│   ├── infra.py                   # AgentResult 和 run_specialist_agent
│   └── multi-agent/               # Multi-Agent 组件
│       ├── orchestrator.py        # 任务分配器
│       ├── market_specialist.py   # 市场数据专家
│       ├── fundamentals_specialist.py  # 基本面专家
│       ├── sentiment_specialist.py     # 情绪分析专家
│       ├── critic.py              # 答案验证器
│       └── synthesizer.py         # 答案合成器
├── config.py                      # 配置和 API 客户端
├── tools.py                       # 7个工具函数
├── schemas.py                     # 工具的 JSON schemas
├── benchmark_questions.py         # 15个基准问题
├── test_all_architectures.py     # 测试所有架构
├── quick_test.py                  # 快速测试
└── mp3_assignment.ipynb           # 原始作业笔记本

```

## 🎯 下一步

1. **实现 Evaluator** (`evaluation/evaluator.py`)
   - LLM-as-judge 评分系统
   - 检测虚构数据
   - 0-3 评分标准

2. **运行完整评估**
   - 对 15 个基准问题运行三个架构
   - 使用 gpt-4o-mini 和 gpt-4o
   - 生成 Excel 结果文件

3. **完成反思问题**
   - Q0-Q5 的详细分析
   - 引用具体问题 ID 和分数
   - 架构设计决策的说明

## 🚀 性能特点

**当前测试结果**：
- 简单问题（1个专家）：~6秒
- 跨域问题（3个专家）：~15-20秒
- 置信度评分：通常 90-100%
- Orchestrator 准确激活相关专家
