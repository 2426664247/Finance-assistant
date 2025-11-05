import os
from langchain.vectorstores import FAISS
from ..core.llm_adapter import VolcanoLLM, VolcanoEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import CSVLoader
from langchain.tools import BaseTool
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class KnowledgeBaseTool(BaseTool):
    name: str = "Financial Knowledge Base"
    description: str = "Use this tool to answer questions about financial knowledge and terminology. The knowledge base contains definitions and explanations of various financial concepts."
    qa_chain: RetrievalQA = None

    def __init__(self, llm):
        super().__init__()
        embeddings = VolcanoEmbeddings(
            ark_api_key=os.getenv("ARK_API_KEY")
        )
        loader = CSVLoader(file_path="D:\\a大三\\人工智能\\大作业\\项目\\financial_agent\\financial_knowledge_base.csv", encoding='utf-8')
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(texts, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        prompt_template = """Please answer the question based on the following context. Your answer must be based on the context information. If the question is not related to the context, please answer 'Sorry, I don't know'.
        Context: {context}
        Question: {question}
        Answer (please be concise and clear):
        """
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT}
        )

    def _run(self, query: str) -> dict:
        """Executes the QA chain to answer a query."""
        result = self.qa_chain.invoke({"query": query})
        return {"output": result.get("result", "")}