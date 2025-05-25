"""CSVファイルアダプター。

このモジュールは、CSVファイルからドキュメントを読み込むためのアダプターを提供します。
"""
from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
from langchain.schema.document import Document

logger = logging.getLogger(__name__)


class CSVFileAdapter:
    """CSVファイルからドキュメントを読み込むアダプター。"""

    def __init__(
        self,
        file_path: Union[str, Path],
        content_columns: List[str],
        metadata_columns: Optional[List[str]] = None,
        encoding: str = "utf-8",
        delimiter: str = ",",
    ):
        """CSVファイルアダプターを初期化します。

        Args:
            file_path: CSVファイルのパス。
            content_columns: コンテンツとして使用する列名のリスト。
            metadata_columns: メタデータとして使用する列名のリスト。
            encoding: ファイルの文字エンコーディング。
            delimiter: CSVの区切り文字。
        """
        self.file_path = Path(file_path)
        self.content_columns = content_columns
        self.metadata_columns = metadata_columns or []
        self.encoding = encoding
        self.delimiter = delimiter

    def get_documents(self) -> List[Document]:
        """CSVファイルからドキュメントを取得します。

        Returns:
            ドキュメントのリスト。
        """
        if not self.file_path.exists():
            logger.warning(f"ファイル {self.file_path} が存在しません")
            return []

        documents = []
        try:
            logger.info(f"CSVファイルを読み込み中: {self.file_path}")
            df = pd.read_csv(self.file_path, encoding=self.encoding, delimiter=self.delimiter)
            
            for i, row in df.iterrows():
                content_parts = []
                for column in self.content_columns:
                    if column in row:
                        content_parts.append(f"{column}: {row[column]}")
                
                content = "\n".join(content_parts)
                
                metadata = {
                    "source": str(self.file_path),
                    "row": i,
                }
                
                for column in self.metadata_columns:
                    if column in row:
                        metadata[column] = row[column]
                
                document = Document(page_content=content, metadata=metadata)
                documents.append(document)
        except Exception as e:
            logger.error(f"CSVファイル {self.file_path} の読み込み中にエラーが発生しました: {e}")
        
        logger.info(f"{self.file_path} から {len(documents)} 個のドキュメントを読み込みました")
        return documents


class CSVDirectoryAdapter:
    """複数のCSVファイルからドキュメントを読み込むアダプター。"""

    def __init__(
        self,
        directory_path: Union[str, Path],
        content_columns: List[str],
        metadata_columns: Optional[List[str]] = None,
        encoding: str = "utf-8",
        delimiter: str = ",",
        file_extension: str = ".csv",
    ):
        """CSVディレクトリアダプターを初期化します。

        Args:
            directory_path: CSVファイルが含まれるディレクトリのパス。
            content_columns: コンテンツとして使用する列名のリスト。
            metadata_columns: メタデータとして使用する列名のリスト。
            encoding: ファイルの文字エンコーディング。
            delimiter: CSVの区切り文字。
            file_extension: 処理するファイルの拡張子。
        """
        self.directory_path = Path(directory_path)
        self.content_columns = content_columns
        self.metadata_columns = metadata_columns
        self.encoding = encoding
        self.delimiter = delimiter
        self.file_extension = file_extension

    def get_documents(self) -> List[Document]:
        """すべてのCSVファイルからドキュメントを取得します。

        Returns:
            ドキュメントのリスト。
        """
        if not self.directory_path.exists():
            logger.warning(f"ディレクトリ {self.directory_path} が存在しません")
            return []

        all_documents = []
        for file_path in self.directory_path.glob(f"*{self.file_extension}"):
            adapter = CSVFileAdapter(
                file_path=file_path,
                content_columns=self.content_columns,
                metadata_columns=self.metadata_columns,
                encoding=self.encoding,
                delimiter=self.delimiter,
            )
            documents = adapter.get_documents()
            all_documents.extend(documents)
        
        logger.info(f"{self.directory_path} のすべてのCSVファイルから {len(all_documents)} 個のドキュメントを読み込みました")
        return all_documents


def load_qa_dataset_from_csv(
    file_path: Union[str, Path],
    question_column: str,
    answer_column: str,
    metadata_columns: Optional[List[str]] = None,
    embed_answer: bool = True,
) -> List[Document]:
    """Q&AデータセットをCSVファイルから読み込みます。

    Args:
        file_path: CSVファイルのパス。
        question_column: 質問列の名前。
        answer_column: 回答列の名前。
        metadata_columns: メタデータ列の名前のリスト。
        embed_answer: 回答もページコンテンツに含めるかどうか。

    Returns:
        ドキュメントのリスト。
    """
    logger.info(f"Q&Aデータセットを {file_path} から読み込みます")
    
    file_path = Path(file_path)
    if not file_path.exists():
        logger.warning(f"ファイル {file_path} が存在しません")
        return []
    
    documents = []
    try:
        df = pd.read_csv(file_path)
        
        for i, row in df.iterrows():
            if question_column not in row or answer_column not in row:
                continue
                
            question = row[question_column]
            answer = row[answer_column]
            
            if not question or not answer:
                continue
                
            if embed_answer:
                page_content = f"question: {question}\nanswer: {answer}"
            else:
                page_content = question
                
            metadata = {
                "source": str(file_path),
                "row": i,
                "question": question,
                "answer": answer,
            }
            
            if metadata_columns:
                for column in metadata_columns:
                    if column in row:
                        metadata[column] = row[column]
                        
            document = Document(page_content=page_content, metadata=metadata)
            documents.append(document)
    except Exception as e:
        logger.error(f"CSVファイル {file_path} の読み込み中にエラーが発生しました: {e}")
    
    logger.info(f"{file_path} から {len(documents)} 個のQ&Aドキュメントを読み込みました")
    return documents
