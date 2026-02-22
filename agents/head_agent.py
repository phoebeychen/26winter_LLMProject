# Head Agent - 控制器代理
# 负责协调所有子代理，实现模块化的决策逻辑
# Model: gpt-4.1-nano

import os
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings

# 导入所有子代理
from agents.obnoxious_agent import Obnoxious_Agent
from agents.context_rewriter_agent import Context_Rewriter_Agent
from agents.query_agent import Query_Agent
from agents.relevant_agent import Relevant_Documents_Agent
from agents.answering_agent import Answering_Agent


class Head_Agent:
    """
    Head_Agent 是多代理系统的控制器
    
    职责：
    1. 初始化和管理所有子代理
    2. 根据查询类型决定调用哪些代理
    3. 按正确顺序编排代理工作流
    4. 管理多轮对话历史
    5. 返回最终响应给用户
    
    工作流程：
    用户查询 → Context重写(多轮) → Obnoxious检查 → Query检索 
    → Relevant验证 → Answering生成答案 → 返回
    """
    
    def __init__(self, openai_key, pinecone_key, pinecone_index_name) -> None:
        """
        初始化 Head_Agent
        
        参数:
            openai_key: OpenAI API密钥
            pinecone_key: Pinecone API密钥
            pinecone_index_name: Pinecone索引名称
        """
        # 保存配置
        self.openai_key = openai_key
        self.pinecone_key = pinecone_key
        self.pinecone_index_name = pinecone_index_name
        
        # 初始化OpenAI客户端
        self.client = OpenAI(api_key=openai_key)
        
        # 初始化embeddings（用于Query_Agent）
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=openai_key
        )
        
        # 对话历史管理
        self.conversation_history = []
        
        # 子代理容器（初始为None）
        self.obnoxious_agent = None
        self.context_rewriter_agent = None
        self.query_agent = None
        self.relevant_agent = None
        self.answering_agent = None
        
        # 初始化所有子代理
        self.setup_sub_agents()
    
    def setup_sub_agents(self):
        """
        初始化并配置每个子代理实例
        体现模块化设计 - 每个代理独立初始化
        """
        self.obnoxious_agent = Obnoxious_Agent(
            openai_client=self.client
        )
    
        self.context_rewriter_agent = Context_Rewriter_Agent(
            openai_client=self.client
        )
        
        self.query_agent = Query_Agent(
            pinecone_index=self.pinecone_index_name,
            openai_client=self.client,
            embeddings=self.embeddings
        )
        
        self.relevant_agent = Relevant_Documents_Agent(
            openai_client=self.client
        )
        
        self.answering_agent = Answering_Agent(
            openai_client=self.client
        )
        
        print("Initialized agents finished")
    
    def process_query(self, user_query: str, use_history: bool = True) -> dict:
        """
        处理用户查询的主要方法
        
        参数:
            user_query: 用户输入的查询字符串
            use_history: 是否使用对话历史（多轮对话）
            
        返回:
            字典包含:
            - response: 最终响应文本
            - agent_path: 使用的代理路径（用于调试和评估）
            - status: 成功/失败状态
        """
        agent_path = [] #记录chatbot执行过程中经过了哪些代理
        
        try:
            # ===== 步骤 1: 多轮对话上下文重写（如果需要） =====
            # 先标准化输入，解决代词引用和语义不完整问题
            processed_query = user_query
            if use_history and len(self.conversation_history) > 0:
                agent_path.append("Context_Rewriter_Agent")
                processed_query = self.context_rewriter_agent.rephrase(
                    user_history=self.conversation_history,
                    latest_query=user_query
                )
            
            # ===== 步骤 2: 检查是否无礼/冒犯 =====
            # 基于完整语义进行判断
            agent_path.append("Obnoxious_Agent")
            is_obnoxious = self.obnoxious_agent.check_query(processed_query)
            
            if is_obnoxious:
                response = "I'm sorry, but I can't respond to that type of query. Please ask respectfully."
                agent_path.append("REJECTED_OBNOXIOUS")
                return {
                    "response": response,
                    "agent_path": " → ".join(agent_path),
                    "status": "rejected_obnoxious"
                }
            
            # ===== 步骤 3: 从Pinecone检索相关文档 =====
            agent_path.append("Query_Agent")
            retrieved_docs = self.query_agent.query_vector_store(
                query=processed_query,
                k=5
            )
            
            # ===== 步骤 4: 验证文档相关性 =====
            agent_path.append("Relevant_Documents_Agent")
            
            # 调用 Relevant Agent 检查文档相关性
            relevance_result = self.relevant_agent.get_relevance(
                query=processed_query,
                docs=retrieved_docs
            )
            
            # relevance_result 是布尔值：True表示相关，False表示不相关
            if not relevance_result:  # 如果文档不相关
                response = "This query is not relevant to the context of this book. I would be happy to answer questions based on the book's content."
                agent_path.append("REJECTED_IRRELEVANT")
                return {
                    "response": response,
                    "agent_path": " → ".join(agent_path),
                    "status": "rejected_irrelevant"
                }
            
            # ===== 步骤 5: 生成最终答案 =====
            agent_path.append("Answering_Agent")
            final_response = self.answering_agent.generate_response(
                query=processed_query,
                docs=retrieved_docs,
                conv_history=self.conversation_history if use_history else None,
                k=5
            )
            
            # ===== 更新对话历史 =====
            if use_history:
                self.conversation_history.append({
                    "role": "user",
                    "content": user_query
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })
            
            return {
                "response": final_response,
                "agent_path": " → ".join(agent_path),
                "status": "success"
            }
        
        except Exception as e:
            return {
                "response": f"An error occurred: {str(e)}",
                "agent_path": " → ".join(agent_path) + " → ERROR",
                "status": "error"
            }
    
    def reset_conversation(self):
        """
        重置对话历史
        
        用于开始新的对话或清除上下文
        """
        self.conversation_history = []
        print("💬 对话历史已重置")
    
    def get_conversation_history(self):
        """
        获取当前对话历史
        
        返回:
            对话历史列表
        """
        return self.conversation_history
    
    def main_loop(self):
        """
        命令行交互主循环（用于测试）
        
        提供简单的命令行界面来测试chatbot
        """
        print("=" * 60)
        print("  Multi-Agent Chatbot - Command Line Interface")
        print("=" * 60)
        print("Commands:")
        print("  - Type your question to get an answer")
        print("  - Type 'reset' to clear conversation history")
        print("  - Type 'history' to view conversation")
        print("  - Type 'quit' or 'exit' to exit")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # 命令处理
                if user_input.lower() in ['quit', 'exit']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'reset':
                    self.reset_conversation()
                    continue
                
                if user_input.lower() == 'history':
                    print("\n📜 Conversation History:")
                    for msg in self.conversation_history:
                        print(f"  {msg['role']}: {msg['content'][:100]}...")
                    continue
                
                # 处理查询
                print("\n🤖 Processing...")
                result = self.process_query(user_input)
                
                print(f"\n🤖 Assistant: {result['response']}")
                print(f"\n📊 Agent Path: {result['agent_path']}")
                print(f"📈 Status: {result['status']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")


# 测试代码
if __name__ == "__main__":
    # 从环境变量加载API密钥
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    if not openai_key or not pinecone_key:
        print("❌ 请设置 OPENAI_API_KEY 和 PINECONE_API_KEY 环境变量")
        exit(1)
    
    # 创建 Head Agent
    head_agent = Head_Agent(
        openai_key=openai_key,
        pinecone_key=pinecone_key,
        pinecone_index_name="machine-learning-textbook"
    )
    
    # 运行主循环
    head_agent.main_loop()
