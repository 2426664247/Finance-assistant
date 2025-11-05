import os
from pathlib import Path
from typing import Any
from langchain_community.vectorstores import FAISS
from ..core.llm_adapter import VolcanoLLM, VolcanoEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from langchain.tools import BaseTool

class KnowledgeBaseTool(BaseTool):
    name: str = "Financial Knowledge Base"
    description: str = "Use this tool to answer questions about financial knowledge and terminology. The knowledge base contains definitions and explanations of various financial concepts."
    llm: Any = None
    retriever: Any = None

    def __init__(self, llm):
        super().__init__()
        embeddings = VolcanoEmbeddings(
            ark_api_key=os.getenv("ARK_API_KEY")
        )
        kb_path = Path(__file__).resolve().parents[1] / "financial_knowledge_base.csv"
        loader = CSVLoader(file_path=str(kb_path), encoding='utf-8')
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(texts, embeddings)
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        self.llm = llm

    def _run(self, query: str) -> str:
        """简单检索并用 LLM 生成回答。返回纯文本字符串以兼容 LangChain Agent。"""
        docs = self.retriever.get_relevant_documents(query)
        context = "\n\n".join([getattr(d, "page_content", str(d)) for d in docs])
        prompt = (
            "Please answer the question based on the following context. "
            "Your answer must be based on the context information. "
            "If the question is not related to the context, please answer 'Sorry, I don't know'.\n"
            f"Context: {context}\n"
            f"Question: {query}\n"
            "Answer (please be concise and clear):"
        )
        try:
            answer = self.llm.invoke(prompt)
        except Exception:
            # 兼容旧版 LLM 接口
            answer = self.llm._call(prompt)
        return str(answer)