import os
from typing import Any, List, Optional, Mapping, Iterator
from dotenv import load_dotenv

from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema.output import GenerationChunk

# 加载 .env 文件中的环境变量
load_dotenv("financial_agent/configs/.env")

try:
    from volcenginesdkarkruntime import Ark
except ImportError:
    raise ImportError(
        "Could not import volcenginesdkarkruntime python package. "
        "Please install it with `pip install 'volcengine-python-sdk[ark]'`."
    )

class VolcanoLLM(LLM):
    """
    封装火山引擎方舟大模型的 LangChain LLM 适配器。
    用户需要提供 ARK_API_KEY 和 ARK_MODEL_ID 环境变量。
    """
    api_key: str = None
    model_id: str = None
    base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    streaming: bool = False

    def __init__(self, streaming: bool = False, **kwargs: Any):
        super().__init__(**kwargs)
        self.streaming = streaming
        self.api_key = os.getenv("ARK_API_KEY")
        self.model_id = os.getenv("ARK_MODEL_ID")
        if not self.api_key or not self.model_id:
            raise ValueError("ARK_API_KEY 和 ARK_MODEL_ID 环境变量未设置，请在 .env 文件中配置。")

    @property
    def _llm_type(self) -> str:
        """返回LLM的类型"""
        return "volcano_ark"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        同步调用模型。
        """
        client = Ark(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        try:
            completion = client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                **kwargs
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"调用火山方舟模型时出错: {e}")

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """流式调用模型。"""
        client = Ark(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        try:
            stream = client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                **kwargs
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield GenerationChunk(text=content)
                    if run_manager:
                        run_manager.on_llm_new_token(content)
        except Exception as e:
            raise RuntimeError(f"调用火山方舟流式模型时出错: {e}")

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """获取用于识别此LLM的参数。"""
        return {"model_id": self.model_id}


class VolcanoEmbeddings(Embeddings):
    """
    封装火山引擎方舟 Embedding 模型的 LangChain 适配器。
    """
    def __init__(self, model: str = None, ark_api_key: str = None):
        self.client = Ark(
            api_key=ark_api_key or os.getenv("ARK_API_KEY"),
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )
        self.model = os.getenv("ARK_EMBEDDING_MODEL_ID")
        if not self.model:
            raise ValueError("ARK_EMBEDDING_MODEL_ID 环境变量未设置，请在 .env 文件中配置。")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入一批文档"""
        try:
            embeddings = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in embeddings.data]
        except Exception as e:
            raise RuntimeError(f"调用火山方舟 Embedding 模型时出错: {e}")

    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        embeddings = self.embed_documents([text])
        return embeddings[0]