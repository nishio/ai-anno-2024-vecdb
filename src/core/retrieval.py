"""検索機能を提供するモジュール。

このモジュールは、ベクトルデータベースからの検索機能を提供します。
BM25検索、ベクトル検索、ハイブリッド検索などの機能を含みます。
"""
from __future__ import annotations

import functools
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain.schema.document import Document
from langchain.text_splitter import CharacterTextSplitter, TextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)


class Retriever:
    """検索機能の基底クラス。"""

    def get_relevant_documents(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any]]]:
        """クエリに関連するドキュメントを取得します。

        Args:
            query: クエリテキスト。
            top_k: 返す結果の数。

        Returns:
            ドキュメントの内容とメタデータのタプルのリスト。
        """
        raise NotImplementedError("サブクラスで実装する必要があります")


class FAISSRetriever(Retriever):
    """FAISSベースの検索機能。"""

    def __init__(
        self,
        vector_db_path: Union[str, Path],
        embedding_model: str = "models/text-embedding-004",
    ):
        """FAISSベースの検索機能を初期化します。

        Args:
            vector_db_path: ベクトルデータベースのパス。
            embedding_model: 埋め込みモデルの名前。
        """
        self.vector_db_path = Path(vector_db_path)
        self.embedding_model = embedding_model
        self.embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
        self.vector_store = None
        self._load_vector_store()

    def _load_vector_store(self) -> None:
        """ベクトルストアを読み込みます。"""
        logger.info(f"{self.vector_db_path}からベクトルストアを読み込みます")
        self.vector_store = FAISS.load_local(
            str(self.vector_db_path),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info("ベクトルストアが読み込まれました")

    def get_relevant_documents(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any]]]:
        """クエリに関連するドキュメントを取得します。

        Args:
            query: クエリテキスト。
            top_k: 返す結果の数。

        Returns:
            ドキュメントの内容とメタデータのタプルのリスト。
        """
        logger.info(f"クエリ: {query}, top_k: {top_k}")
        retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})
        docs = retriever.get_relevant_documents(query)
        logger.info(f"{len(docs)}個の関連ドキュメントが見つかりました")
        return [(doc.page_content, doc.metadata) for doc in docs]


class BM25Processor:
    """BM25検索のためのテキスト処理機能。"""

    def __init__(self, preprocess_func=None):
        """BM25検索のためのテキスト処理機能を初期化します。

        Args:
            preprocess_func: テキスト前処理関数。
        """
        self.preprocess_func = preprocess_func or (lambda x: x)

    def preprocess(self, text: str) -> str:
        """テキストを前処理します。

        Args:
            text: 前処理するテキスト。

        Returns:
            前処理されたテキスト。
        """
        return self.preprocess_func(text)


class BM25Retriever(Retriever):
    """BM25ベースの検索機能。"""

    def __init__(
        self,
        documents: List[Document],
        processor: Optional[BM25Processor] = None,
    ):
        """BM25ベースの検索機能を初期化します。

        Args:
            documents: 検索対象のドキュメントリスト。
            processor: テキスト処理機能。
        """
        self.processor = processor or BM25Processor()
        self.retriever = self._create_bm25_retriever(documents)

    def _create_bm25_retriever(self, documents: List[Document]) -> BM25Retriever:
        """BM25検索機能を作成します。

        Args:
            documents: 検索対象のドキュメントリスト。

        Returns:
            BM25検索機能。
        """
        logger.info(f"{len(documents)}個のドキュメントからBM25検索機能を作成します")
        return BM25Retriever.from_documents(documents, preprocess_func=self.processor.preprocess)

    def get_relevant_documents(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any]]]:
        """クエリに関連するドキュメントを取得します。

        Args:
            query: クエリテキスト。
            top_k: 返す結果の数。

        Returns:
            ドキュメントの内容とメタデータのタプルのリスト。
        """
        logger.info(f"クエリ: {query}, top_k: {top_k}")
        self.retriever.k = top_k
        docs = self.retriever.get_relevant_documents(query)
        logger.info(f"{len(docs)}個の関連ドキュメントが見つかりました")
        return [(doc.page_content, doc.metadata) for doc in docs]


class HybridRetriever(Retriever):
    """ハイブリッド検索機能。"""

    def __init__(
        self,
        vector_retriever: FAISSRetriever,
        bm25_retriever: BM25Retriever,
        weights: List[float] = None,
    ):
        """ハイブリッド検索機能を初期化します。

        Args:
            vector_retriever: ベクトル検索機能。
            bm25_retriever: BM25検索機能。
            weights: 各検索機能の重み。
        """
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.weights = weights or [0.5, 0.5]
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever.retriever, vector_retriever.vector_store.as_retriever()],
            weights=self.weights,
        )

    def get_relevant_documents(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any]]]:
        """クエリに関連するドキュメントを取得します。

        Args:
            query: クエリテキスト。
            top_k: 返す結果の数。

        Returns:
            ドキュメントの内容とメタデータのタプルのリスト。
        """
        logger.info(f"ハイブリッド検索: クエリ: {query}, top_k: {top_k}")
        docs = self.ensemble_retriever.get_relevant_documents(query)
        logger.info(f"{len(docs)}個の関連ドキュメントが見つかりました")
        top_docs = docs[:top_k]
        return [(doc.page_content, doc.metadata) for doc in top_docs]


def create_bm25_retriever_from_csv(
    csv_path: Union[str, Path],
    content_column: str,
    metadata_columns: List[str] = None,
    text_splitter: Optional[TextSplitter] = None,
    processor: Optional[BM25Processor] = None,
) -> BM25Retriever:
    """CSVファイルからBM25検索機能を作成します。

    Args:
        csv_path: CSVファイルのパス。
        content_column: コンテンツ列の名前。
        metadata_columns: メタデータ列の名前リスト。
        text_splitter: テキスト分割器。
        processor: テキスト処理機能。

    Returns:
        BM25検索機能。
    """
    logger.info(f"{csv_path}からBM25検索機能を作成します")
    
    df = pd.read_csv(csv_path)
    
    docs = []
    for i, row in df.iterrows():
        content = row[content_column]
        metadata = {"row": i}
        if metadata_columns:
            for col in metadata_columns:
                if col in row:
                    metadata[col] = row[col]
        
        doc = Document(page_content=content, metadata=metadata)
        docs.append(doc)
    
    if text_splitter:
        logger.info(f"{text_splitter.__class__.__name__}でドキュメントを分割します")
        docs = text_splitter.split_documents(docs)
        logger.info(f"{len(docs)}個のチャンクに分割されました")
    
    return BM25Retriever(documents=docs, processor=processor)
