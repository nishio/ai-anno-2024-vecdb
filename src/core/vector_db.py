"""ベクトルデータベース操作の中核機能。

このモジュールは、FAISSベクトルデータベースの作成、保存、読み込み、クエリなどの
基本的な操作を提供します。
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from langchain.schema.document import Document
from langchain.text_splitter import TextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import VectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)


class VectorDB(ABC):
    """ベクトルデータベースの抽象基底クラス。"""

    @abstractmethod
    def save(self, path: Union[str, Path]) -> None:
        """ベクトルデータベースをディスクに保存します。

        Args:
            path: ベクトルデータベースを保存するパス。
        """
        pass

    @abstractmethod
    def load(self, path: Union[str, Path]) -> None:
        """ディスクからベクトルデータベースを読み込みます。

        Args:
            path: ベクトルデータベースを読み込むパス。
        """
        pass

    @abstractmethod
    def query(self, query_text: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any]]]:
        """ベクトルデータベースに対してクエリを実行します。

        Args:
            query_text: クエリテキスト。
            top_k: 返す結果の数。

        Returns:
            ドキュメントの内容とメタデータのタプルのリスト。
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """ベクトルデータベースにドキュメントを追加します。

        Args:
            documents: 追加するドキュメントのリスト。
        """
        pass


class FAISSVectorDB(VectorDB):
    """FAISSベースのベクトルデータベース実装。"""

    def __init__(
        self, 
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        use_local_embeddings: bool = True,
        text_splitter: Optional[TextSplitter] = None
    ):
        """FAISSベクトルデータベースを初期化します。

        Args:
            embedding_model: 埋め込みモデルの名前。
                ローカルモデルの場合は、HuggingFaceのモデル名を指定します。
                APIモデルの場合は、Google AIのモデル名を指定します。
            use_local_embeddings: ローカルの埋め込みモデルを使用するかどうか。
                Trueの場合、HuggingFaceのモデルを使用します。
                Falseの場合、Google AIのモデルを使用します（APIキーが必要）。
            text_splitter: テキスト分割器。
        """
        self.embedding_model = embedding_model
        self.use_local_embeddings = use_local_embeddings
        
        if use_local_embeddings:
            logger.info(f"ローカルの埋め込みモデルを使用します: {embedding_model}")
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        else:
            logger.info(f"Google AIの埋め込みモデルを使用します: {embedding_model}")
            self.embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
            
        self.vector_store: Optional[VectorStore] = None
        self.text_splitter = text_splitter

    def build_from_documents(self, documents: List[Document]) -> None:
        """ドキュメントからベクトルデータベースを構築します。

        Args:
            documents: ベクトルデータベースを構築するためのドキュメントのリスト。
        """
        logger.info(f"{len(documents)}個のドキュメントからベクトルデータベースを構築します")
        
        if self.text_splitter:
            logger.info(f"{self.text_splitter.__class__.__name__}でドキュメントを分割します")
            documents = self.text_splitter.split_documents(documents)
            logger.info(f"{len(documents)}個のチャンクに分割されました")

        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        logger.info("ベクトルデータベースが正常に構築されました")

    def save(self, path: Union[str, Path]) -> None:
        """ベクトルデータベースをディスクに保存します。

        Args:
            path: ベクトルデータベースを保存するパス。
        """
        if not self.vector_store:
            raise ValueError("ベクトルストアが初期化されていません。先にbuild_from_documentsを呼び出してください。")
        
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ベクトルデータベースを{path}に保存します")
        self.vector_store.save_local(str(path))
        logger.info(f"ベクトルデータベースが{path}に保存されました")

    def load(self, path: Union[str, Path]) -> None:
        """ディスクからベクトルデータベースを読み込みます。

        Args:
            path: ベクトルデータベースを読み込むパス。
        """
        logger.info(f"{path}からベクトルデータベースを読み込みます")
        self.vector_store = FAISS.load_local(
            str(path),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info(f"{path}からベクトルデータベースが読み込まれました")

    def query(self, query_text: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any]]]:
        """ベクトルデータベースに対してクエリを実行します。

        Args:
            query_text: クエリテキスト。
            top_k: 返す結果の数。

        Returns:
            ドキュメントの内容とメタデータのタプルのリスト。
        """
        if not self.vector_store:
            raise ValueError("ベクトルストアが初期化されていません。先にbuild_from_documentsまたはloadを呼び出してください。")
        
        logger.info(f"ベクトルデータベースに対してクエリを実行します: {query_text}")
        retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})
        docs = retriever.get_relevant_documents(query_text)
        
        logger.info(f"{len(docs)}個の関連ドキュメントが見つかりました")
        return [(doc.page_content, doc.metadata) for doc in docs]

    def add_documents(self, documents: List[Document]) -> None:
        """ベクトルデータベースにドキュメントを追加します。

        Args:
            documents: 追加するドキュメントのリスト。
        """
        if not self.vector_store:
            self.build_from_documents(documents)
            return
        
        if self.text_splitter:
            documents = self.text_splitter.split_documents(documents)
        
        logger.info(f"{len(documents)}個のドキュメントをベクトルデータベースに追加します")
        self.vector_store.add_documents(documents)
        logger.info(f"{len(documents)}個のドキュメントがベクトルデータベースに追加されました")


class VectorDBBuilder:
    """ベクトルデータベースのビルダー。"""

    def __init__(
        self, 
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        use_local_embeddings: bool = True,
        text_splitter: Optional[TextSplitter] = None
    ):
        """ベクトルデータベースビルダーを初期化します。

        Args:
            embedding_model: 埋め込みモデルの名前。
                ローカルモデルの場合は、HuggingFaceのモデル名を指定します。
                APIモデルの場合は、Google AIのモデル名を指定します。
            use_local_embeddings: ローカルの埋め込みモデルを使用するかどうか。
                Trueの場合、HuggingFaceのモデルを使用します。
                Falseの場合、Google AIのモデルを使用します（APIキーが必要）。
            text_splitter: テキスト分割器。
        """
        self.embedding_model = embedding_model
        self.use_local_embeddings = use_local_embeddings
        self.text_splitter = text_splitter

    def build(self, documents: List[Document]) -> VectorDB:
        """ドキュメントからベクトルデータベースを構築します。

        Args:
            documents: ベクトルデータベースを構築するためのドキュメントのリスト。

        Returns:
            ベクトルデータベース。
        """
        vector_db = FAISSVectorDB(
            embedding_model=self.embedding_model,
            use_local_embeddings=self.use_local_embeddings,
            text_splitter=self.text_splitter
        )
        vector_db.build_from_documents(documents)
        return vector_db

    def load(self, path: Union[str, Path]) -> VectorDB:
        """ディスクからベクトルデータベースを読み込みます。

        Args:
            path: ベクトルデータベースを読み込むパス。

        Returns:
            ベクトルデータベース。
        """
        vector_db = FAISSVectorDB(
            embedding_model=self.embedding_model,
            use_local_embeddings=self.use_local_embeddings
        )
        vector_db.load(path)
        return vector_db
