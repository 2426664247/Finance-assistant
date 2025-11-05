import os
from langchain.chat_models import ChatOpenAI  # 导入 ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import PromptTemplate
from langchain.document_loaders import CSVLoader
# 设置 OpenAI API 密钥
os.environ["OPENAI_API_KEY"] = 'sk-iF8uxxxxxxxxxxxE4A75f'
# 使用 OpenAI LLM
llm = ChatOpenAI(  # 使用 ChatOpenAI
    model_name="gpt-3.5-turbo", 
    temperature=0,  # 根据需要调整温度
)
# 加载 CSV 文档
loader = CSVLoader("books.csv")
doc = loader.load()
# 将文档分割成可管理的块
text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=400)
docs = text_splitter.split_documents(doc)
# 创建嵌入
embeddings = OpenAIEmbeddings()
docsearch = FAISS.from_documents(docs, embeddings)
# 定义提示模板
prompt_template = """请根据以下内容回答问题。你的回答必须基于上下文信息，若问题与上下文不相关，请回答“对不起，我不知道”。
上下文: {context}
问题: {question}
回答（请简洁明了）：
"""
PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
# 初始化问答系统
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=docsearch.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": PROMPT}
)
# 示例查询
query = "请告诉我George Orwell这个作者有哪些作品。"
# 执行查询
result = qa.run(query)
print(result)
