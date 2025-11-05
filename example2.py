import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.tools import BaseTool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
# 工具类
class BookInfoTool(BaseTool):
    name: str = "Book information retrieval"
    description: str = "Use this tool to retrieve basic information about books from the database."

    def _run(self, title: str):
        books_df = pd.read_csv("books.csv", encoding='ISO-8859-1')
        """根据书名检索书籍信息"""
        book_info = books_df[books_df['title'].str.contains(title, case=False, na=False)]
        if not book_info.empty:
            return book_info.to_dict(orient='records')
        return f"No book found with the title: {title}"
# 初始化 LLM
llm = ChatOpenAI(
    openai_api_key="sk-iF8uPxxxxxxxxxcE4A75f",  # 请将其替换为您的 API 密钥
    temperature=0,
    model_name='gpt-3.5-turbo'
)
conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True
)

book_info_tool = [BookInfoTool()]  # 创建工具实例

sys_msg = """
You are designed to assist with retrieving basic information about books based on the provided database. 
"""

# 初始化代理
agent = initialize_agent(
    agent='chat-conversational-react-description',
    tools=book_info_tool,  # 将 BookInfoTool 实例作为工具传入
    llm=llm,
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True,
    memory=conversational_memory,
    early_stopping_method='generate'
)
new_prompt = agent.agent.create_prompt(
    system_message=sys_msg,
    tools=book_info_tool
)
agent.agent.llm_chain.prompt = new_prompt

# 示例查询
response = agent.invoke({"input": "Can you provide author about the book 'Divergent'?"})  # 注意这里是一个字典，包含输入
print(response)
