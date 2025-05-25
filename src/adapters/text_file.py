"""テキストファイルアダプター。

このモジュールは、テキストファイルからドキュメントを読み込むためのアダプターを提供します。
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from langchain.schema.document import Document

logger = logging.getLogger(__name__)


class TextFileAdapter:
    """テキストファイルからドキュメントを読み込むアダプター。"""

    def __init__(
        self,
        directory_path: Union[str, Path],
        file_extension: str = ".txt",
        encoding: str = "utf-8",
        metadata_extractor: Optional[callable] = None,  # type: ignore
    ):
        """テキストファイルアダプターを初期化します。

        Args:
            directory_path: テキストファイルが含まれるディレクトリのパス。
            file_extension: 処理するファイルの拡張子。
            encoding: ファイルの文字エンコーディング。
            metadata_extractor: ファイルの内容からメタデータを抽出する関数。
        """
        self.directory_path = Path(directory_path)
        self.file_extension = file_extension
        self.encoding = encoding
        self.metadata_extractor = metadata_extractor

    def get_documents(self) -> List[Document]:
        """テキストファイルからドキュメントを取得します。

        Returns:
            ドキュメントのリスト。
        """
        if not self.directory_path.exists():
            logger.warning(f"ディレクトリ {self.directory_path} が存在しません")
            return []

        documents = []
        for file_path in self.directory_path.glob(f"*{self.file_extension}"):
            try:
                logger.info(f"ファイルを読み込み中: {file_path}")
                with open(file_path, "r", encoding=self.encoding) as f:
                    content = f.read()
                
                metadata = self._extract_metadata(content, file_path)
                document = Document(page_content=content, metadata=metadata)
                documents.append(document)
            except Exception as e:
                logger.error(f"ファイル {file_path} の読み込み中にエラーが発生しました: {e}")
        
        logger.info(f"{self.directory_path} から {len(documents)} 個のドキュメントを読み込みました")
        return documents

    def _extract_metadata(self, content: str, file_path: Path) -> Dict:
        """ファイルの内容からメタデータを抽出します。

        Args:
            content: ファイルの内容。
            file_path: ファイルのパス。

        Returns:
            メタデータの辞書。
        """
        metadata = {
            "source": str(file_path),
            "filename": file_path.name,
        }
        
        if self.metadata_extractor:
            try:
                extracted_metadata = self.metadata_extractor(content, file_path)
                metadata.update(extracted_metadata)
            except Exception as e:
                logger.error(f"{file_path} からのメタデータ抽出中にエラーが発生しました: {e}")
        
        return metadata


class TextDirectoryAdapter:
    """複数のディレクトリからテキストを読み込むアダプター。"""

    def __init__(
        self,
        directory_paths: List[Union[str, Path]],
        file_extension: str = ".txt",
        encoding: str = "utf-8",
        metadata_extractor: Optional[callable] = None,  # type: ignore
    ):
        """テキストディレクトリアダプターを初期化します。

        Args:
            directory_paths: テキストファイルが含まれるディレクトリのパスのリスト。
            file_extension: 処理するファイルの拡張子。
            encoding: ファイルの文字エンコーディング。
            metadata_extractor: ファイルの内容からメタデータを抽出する関数。
        """
        self.adapters = [
            TextFileAdapter(
                directory_path=path,
                file_extension=file_extension,
                encoding=encoding,
                metadata_extractor=metadata_extractor,
            )
            for path in directory_paths
        ]

    def get_documents(self) -> List[Document]:
        """すべてのディレクトリからドキュメントを取得します。

        Returns:
            ドキュメントのリスト。
        """
        all_documents = []
        for adapter in self.adapters:
            documents = adapter.get_documents()
            all_documents.extend(documents)
        
        logger.info(f"すべてのディレクトリから {len(all_documents)} 個のドキュメントを読み込みました")
        return all_documents
