from financial_agent.core.agent import create_financial_agent
from financial_agent.core.llm_adapter import VolcanoLLM
from financial_agent.tools.financial_data_tool import FinancialDataTool
# from financial_agent.tools.knowledge_base_tool import KnowledgeBaseTool

def main():
    """主函数"""
    print("正在初始化金融智能体...")
    
    # 1. 初始化LLM
    llm = VolcanoLLM()
    
    # 2. 初始化工具
    tools = [
        FinancialDataTool(),
        # KnowledgeBaseTool() # 暂时禁用知识库工具
    ]
    
    # 3. 创建智能体
    agent = create_financial_agent(llm)
    
    print("智能体初始化完成！")
    
    # 4. 示例交互
    queries = [
        "查询一下 AAPL 最近一个月的股价",
        "请解释一下什么是KDJ指标？"
    ]
    
    for user_query in queries:
        print(f"\n用户提问: {user_query}")
        try:
            response = agent.invoke({"input": user_query})
            print(f"智能体回答: {response['output']}")
        except Exception as e:
            print(f"执行过程中发生错误: {e}")

if __name__ == "__main__":
    main()