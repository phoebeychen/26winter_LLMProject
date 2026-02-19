# 评估管道 - LLM作为评判者
# 用于评估chatbot的表现

import json
from typing import List, Dict, Any


class LLM_Judge:
    """
    'LLM-as-a-Judge'评估chatbot的表现
    
    这个类负责：
    1. 根据不同类别构造评判prompt
    2. 调用LLM进行评分
    3. 解析评分结果（0或1）
    """
    
    def __init__(self, openai_client) -> None:
        """
        初始化评判者
        
        参数:
            openai_client: OpenAI客户端实例
        """
        self.client = openai_client

    def construct_judge_prompt(self, user_input, bot_response, category):
        """
        为评判LLM构造prompt
        
        参数:
            user_input: 用户输入
            bot_response: chatbot的响应
            category: 测试类别（obnoxious, irrelevant等）
            
        返回:
            构造好的评判prompt字符串
        """
        # TODO: 创建一个prompt，包含：
        # 1. 用户输入
        # 2. Chatbot的响应
        # 3. 该类别的具体评判标准
        
        # 例如，对于Hybrid类别：
        # "评判标准：Chatbot应该只回答相关部分，忽略不相关部分"
        
        # 对于Obnoxious类别：
        # "评判标准：Chatbot应该礼貌地拒绝回答，不应该提供实质性答案"
        
        # 提示：可以使用字典存储不同类别的标准
        # criteria = {
        #     "obnoxious": "应该礼貌拒绝，不提供实质性答案",
        #     "irrelevant": "应该说明问题与书本内容无关",
        #     "relevant": "应该基于书本内容准确回答",
        #     ...
        # }
        
        pass

    def evaluate_interaction(self, user_input, bot_response, agent_used, category) -> int:
        """
        将交互发送给评判LLM，解析二元分数（0或1）
        
        参数:
            user_input: 用户输入
            bot_response: chatbot响应
            agent_used: 使用的agent（可选，用于诊断）
            category: 测试类别
            
        返回:
            1 (成功) 或 0 (失败)
        """
        # TODO: 使用construct_judge_prompt构造prompt
        # TODO: 调用OpenAI API
        # TODO: 解析输出，返回1（成功）或0（失败）
        
        # 提示：可以要求LLM以特定格式输出，例如：
        # "请输出PASS或FAIL，然后给出简短理由"
        # 然后解析响应中的PASS/FAIL
        
        pass


class EvaluationPipeline:
    """
    运行chatbot对测试数据集的评估，并汇总分数
    
    这个类负责：
    1. 运行单轮测试
    2. 运行多轮对话测试
    3. 汇总和计算指标
    """
    
    def __init__(self, head_agent, judge: LLM_Judge) -> None:
        """
        初始化评估管道
        
        参数:
            head_agent: Part-3中实现的Head_Agent
            judge: LLM_Judge实例
        """
        self.chatbot = head_agent  # 这是你在Part-3中实现的Head_Agent
        self.judge = judge
        self.results = {
            "obnoxious": [],
            "irrelevant": [],
            "relevant": [],
            "small_talk": [],
            "hybrid": [],
            "multi_turn": []
        }

    def run_single_turn_test(self, category: str, test_cases: List[str]):
        """
        运行单轮类别测试（Obnoxious, Irrelevant等）
        
        参数:
            category: 测试类别
            test_cases: 测试用例列表
        """
        # TODO: 遍历test_cases
        # TODO: 将查询发送给self.chatbot
        # TODO: 捕获响应和内部使用的agent路径
        # TODO: 将数据传递给self.judge.evaluate_interaction
        # TODO: 存储结果
        
        # 示例流程：
        # for test_case in test_cases:
        #     query = test_case if isinstance(test_case, str) else test_case["query"]
        #     
        #     # 调用chatbot
        #     bot_response = self.chatbot.process_query(query)
        #     
        #     # 评判
        #     score = self.judge.evaluate_interaction(
        #         user_input=query,
        #         bot_response=bot_response,
        #         agent_used=None,  # 如果能获取agent信息更好
        #         category=category
        #     )
        #     
        #     # 存储结果
        #     self.results[category].append({
        #         "query": query,
        #         "response": bot_response,
        #         "score": score
        #     })
        
        pass

    def run_multi_turn_test(self, test_cases: List[List[str]]):
        """
        运行多轮对话测试
        
        参数:
            test_cases: 多轮对话列表，每个对话是一个查询列表
        """
        # TODO: 遍历对话流
        # TODO: 为chatbot维护上下文/历史
        # TODO: 评判最终响应或流程一致性
        
        # 提示：多轮对话需要：
        # 1. 维护对话历史
        # 2. 可能需要评判每一轮或只评判最后一轮
        # 3. 检查上下文是否被正确理解和使用
        
        pass

    def calculate_metrics(self):
        """
        汇总分数并打印最终报告
        """
        # TODO: 计算每个类别的得分总和
        # TODO: 计算总体准确率
        
        # 示例输出格式：
        # print("=" * 50)
        # print("评估报告")
        # print("=" * 50)
        # 
        # total_tests = 0
        # total_passed = 0
        # 
        # for category, results in self.results.items():
        #     if results:
        #         passed = sum(r["score"] for r in results)
        #         total = len(results)
        #         accuracy = passed / total * 100
        #         
        #         print(f"\n{category.upper()}:")
        #         print(f"  通过: {passed}/{total} ({accuracy:.1f}%)")
        #         
        #         total_tests += total
        #         total_passed += passed
        # 
        # overall_accuracy = total_passed / total_tests * 100 if total_tests > 0 else 0
        # print(f"\n总体准确率: {total_passed}/{total_tests} ({overall_accuracy:.1f}%)")
        
        pass


# 示例使用
if __name__ == "__main__":
    import os
    from openai import OpenAI
    # from agents.head_agent import Head_Agent  # 需要从你的Part-3导入
    
    # 1. 初始化客户端
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 2. 初始化系统组件
    # head_agent = Head_Agent(...)  # 从Part-3导入并初始化
    judge = LLM_Judge(client)
    # pipeline = EvaluationPipeline(head_agent, judge)
    
    # 3. 加载测试数据
    from generate_dataset import TestDatasetGenerator
    generator = TestDatasetGenerator(client)
    data = generator.load_dataset("test_set.json")
    
    # 4. 运行评估
    # pipeline.run_single_turn_test("obnoxious", data["obnoxious"])
    # pipeline.run_single_turn_test("irrelevant", data["irrelevant"])
    # pipeline.run_single_turn_test("relevant", data["relevant"])
    # pipeline.run_single_turn_test("small_talk", data["small_talk"])
    # pipeline.run_single_turn_test("hybrid", data["hybrid"])
    # pipeline.run_multi_turn_test(data["multi_turn"])
    
    # 5. 计算并打印指标
    # pipeline.calculate_metrics()
    
    print("评估流程配置完成！")
