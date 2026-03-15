# Mini Project 3 - 使用指南

## 🎉 项目完成状态

✅ **所有技术实现已完成！** 

- 三个架构（Baseline, Single Agent, Multi-Agent）
- 完整的多智能体系统（6个组件）
- LLM-as-judge 评估系统
- 自动化评估运行器

## 🚀 快速开始

### 1. 确保环境准备就绪

```bash
# 安装依赖
pip install -r requirements.txt

# 检查 .env 文件
# 确保包含：
# OPENAI_API_KEY=your_key_here
# ALPHAVANTAGE_API_KEY=your_key_here
```

### 2. 运行完整评估

```bash
# 方式 1: 使用 gpt-4o-mini（推荐先运行）
python run_evaluation.py

# 方式 2: 使用 gpt-4o（较慢但更准确）
python run_evaluation.py large
```

**运行时间**：
- gpt-4o-mini: ~15-20分钟
- gpt-4o: ~20-30分钟

**输出文件**：
- `results_gpt4o_mini.xlsx`
- `results_gpt4o.xlsx`

### 3. 查看结果

Excel 文件包含两个工作表：

1. **Results Sheet**：每个问题的详细结果
   - 三个架构的答案
   - 评分（0-3）
   - 评估器的reasoning
   - 虚构数据检测
   - 工具使用情况

2. **Summary Sheet**：汇总统计
   - 各难度级别的准确率
   - 平均执行时间
   - 虚构数据计数

## 📊 已测试的功能

### ✅ 架构测试
```bash
# 测试所有三个架构
python quick_test.py
```

### ✅ 评估器校准
```bash
# 验证评估器的评分标准
python test_evaluator.py
```

### ✅ 快速评估测试
```bash
# 3个问题的快速测试
python test_eval_quick.py
```

## 📁 关键文件

### 架构入口
```python
from agents.baseline_agent import run_baseline
from agents.single_agent import run_single_agent  
from agents.multi_agent_runner import run_multi_agent
```

### 评估系统
```python
from evaluation.evaluator import run_evaluator
from evaluation.runner import run_full_evaluation
```

## 🎯 多智能体架构说明

**架构类型**: Orchestrator + Specialists + Critic

**工作流程**:
1. **Orchestrator** 分析问题，决定激活哪些专家
2. **Specialists** 执行各自领域的任务
   - Market Specialist: 价格和市场数据
   - Fundamentals Specialist: 基本面指标
   - Sentiment Specialist: 新闻情绪
3. **Critic** 验证每个专家的答案，评估置信度
4. **Synthesizer** 合成最终答案

**优势**:
- ✅ 专业化分工，减少工具混淆
- ✅ 内置验证机制
- ✅ 置信度评分（0-100%）
- ✅ 可追踪的推理过程

## 📝 下一步：完成反思问题

运行评估后，你需要完成作业的反思问题部分：

### Q0 (5分) - Baseline vs Single Agent
- 对比性能
- 分析是否需要agentic实现
- **需引用具体问题ID和分数**

### Q1 (5分) - Multi-Agent必要性
- 哪个难度级别MA表现最好
- 提供2个具体案例（MA优于SA，SA优于/等于MA）
- **需引用问题ID和分数**

### Q2 (5分) - 评估器可靠性
- 找3个评分不合理的案例
- 分析评估器的偏见
- 如何改进prompt

### Q3 (5分) - 准确率分析
- 填写各架构在各难度的准确率表格
- 分析breakdown模式
- 哪类问题最适合agentic方法

### Q4 (5分) - gpt-4o vs gpt-4o-mini
- Multi-Agent在两个模型的表现对比
- 置信度和critic问题数量的变化
- 成本效益分析

### Q5 (5分) - 架构设计决策
- 为什么选择Orchestrator+Specialists+Critic
- 尝试了什么方案但没成功
- 工具如何分配给专家
- 验证机制如何工作
- 是否减少了虚构数据（用数据说明）

## 💡 提示

### 引用格式示例
```
Q08 (medium, sector_price):
- Single Agent: 2/3, tools: [get_tickers_by_sector, get_price_performance]
- Multi Agent: 3/3, confidence: 95%, specialists: [Market]
- Multi-Agent胜出原因：专注的Market Specialist避免了工具混淆
```

### Excel数据分析
```python
import pandas as pd

# 读取结果
df = pd.read_excel('results_gpt4o_mini.xlsx', sheet_name='Results')

# 找出Single Agent表现好的问题
sa_better = df[df['SA Score /3'] > df['MA Score /3']]
print(sa_better[['Question ID', 'Question', 'SA Score /3', 'MA Score /3']])
```

## 🎓 提交清单

- [ ] `results_gpt4o_mini.xlsx` - gpt-4o-mini评估结果
- [ ] `results_gpt4o.xlsx` - gpt-4o评估结果  
- [ ] 反思问题Q0-Q5（可以在notebook或单独文档中）
- [ ] 多智能体架构设计说明（已包含在代码注释中）

## ⏰ 预计完成时间

- 运行评估：30-60分钟（两个模型）
- 分析结果：30-45分钟
- 完成反思：1-2小时

**总计：2-4小时即可完成整个项目！**

## 🆘 常见问题

### Q: 评估卡住了怎么办？
A: 按 Ctrl+C 取消。进度已自动保存到Excel，可以从中断处继续。

### Q: API限流错误？
A: 增加 `delay_sec` 参数（默认3秒）。

### Q: 某些股票显示 "possibly delisted"？
A: 这是正常的，yfinance对某些股票无数据。agents会处理这种情况。

### Q: Multi-Agent比Single Agent慢很多？
A: 正常。MA需要调用Orchestrator、多个Specialists和Critic，API调用更多。

## 📞 技术支持

如果遇到问题：
1. 检查 `.env` 文件的API keys是否正确
2. 确认所有依赖已安装（`pip install -r requirements.txt`）
3. 查看 `COMPLETION_STATUS.md` 了解当前状态
4. 运行 `test_evaluator.py` 验证评估器工作正常
