"""YouTubeトランスクリプトアダプターモジュール。

このモジュールは、YouTubeビデオからトランスクリプト（字幕）を取得し、
ドキュメントとして処理するためのアダプターを提供します。
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd
from langchain.schema.document import Document
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from pytube import YouTube

logger = logging.getLogger(__name__)


class YouTubeAdapter:
    """YouTubeビデオからトランスクリプトを取得するアダプター。"""

    def __init__(
        self,
        language_code: str = "ja",
        metadata_extractor: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        """YouTubeアダプターを初期化します。

        Args:
            language_code: 取得するトランスクリプトの言語コード。
            metadata_extractor: メタデータ抽出関数。
        """
        self.language_code = language_code
        self.metadata_extractor = metadata_extractor or (lambda video_id, metadata: metadata)
        self.formatter = TextFormatter()

    def _extract_video_id(self, url: str) -> str:
        """YouTubeのURLからビデオIDを抽出します。

        Args:
            url: YouTubeビデオのURL。

        Returns:
            ビデオID。
        """
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # 標準的なYouTube URL
            r"(?:embed\/)([0-9A-Za-z_-]{11})",  # 埋め込みURL
            r"(?:shorts\/)([0-9A-Za-z_-]{11})",  # ショート動画URL
            r"^([0-9A-Za-z_-]{11})$",  # ビデオIDのみ
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        logger.warning(f"ビデオIDを抽出できませんでした: {url}")
        return url  # 抽出できない場合は入力をそのまま返す

    def _get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """YouTubeビデオのメタデータを取得します。

        Args:
            video_id: YouTubeビデオID。

        Returns:
            ビデオのメタデータ。
        """
        try:
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            metadata = {
                "title": yt.title,
                "author": yt.author,
                "publish_date": yt.publish_date.isoformat() if yt.publish_date else None,
                "length": yt.length,
                "views": yt.views,
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
            return metadata
        except Exception as e:
            logger.warning(f"メタデータの取得に失敗しました: {video_id}, エラー: {e}")
            return {"video_id": video_id, "url": f"https://www.youtube.com/watch?v={video_id}"}

    def get_transcript(self, video_id: str) -> Optional[str]:
        """YouTubeビデオのトランスクリプトを取得します。

        Args:
            video_id: YouTubeビデオID。

        Returns:
            トランスクリプトのテキスト。取得できない場合はNone。
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=[self.language_code]
            )
            return self.formatter.format_transcript(transcript)
        except Exception as e:
            logger.warning(f"トランスクリプトの取得に失敗しました: {video_id}, エラー: {e}")
            return None

    def get_documents_from_url(self, url: str) -> List[Document]:
        """YouTubeのURLからドキュメントを取得します。

        Args:
            url: YouTubeビデオのURL。

        Returns:
            ドキュメントのリスト。
        """
        video_id = self._extract_video_id(url)
        logger.info(f"ビデオID: {video_id} のトランスクリプトを取得します")

        transcript = self.get_transcript(video_id)
        if not transcript:
            logger.warning(f"トランスクリプトが見つかりませんでした: {video_id}")
            return []

        metadata = self._get_video_metadata(video_id)
        metadata = self.metadata_extractor(video_id, metadata)

        logger.info(f"ビデオ: {metadata.get('title', video_id)} のトランスクリプトを取得しました")
        return [Document(page_content=transcript, metadata=metadata)]

    def get_documents_from_urls(self, urls: List[str]) -> List[Document]:
        """複数のYouTubeビデオURLからドキュメントを取得します。

        Args:
            urls: YouTubeビデオURLのリスト。

        Returns:
            ドキュメントのリスト。
        """
        documents = []
        for url in urls:
            docs = self.get_documents_from_url(url)
            documents.extend(docs)
        return documents


class YouTubePlaylistAdapter:
    """YouTubeプレイリストからトランスクリプトを取得するアダプター。"""

    def __init__(
        self,
        language_code: str = "ja",
        metadata_extractor: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        """YouTubeプレイリストアダプターを初期化します。

        Args:
            language_code: 取得するトランスクリプトの言語コード。
            metadata_extractor: メタデータ抽出関数。
        """
        self.language_code = language_code
        self.youtube_adapter = YouTubeAdapter(language_code, metadata_extractor)

    def _extract_playlist_id(self, url: str) -> str:
        """YouTubeのURLからプレイリストIDを抽出します。

        Args:
            url: YouTubeプレイリストのURL。

        Returns:
            プレイリストID。
        """
        pattern = r"(?:list=)([0-9A-Za-z_-]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        logger.warning(f"プレイリストIDを抽出できませんでした: {url}")
        return url

    def _get_playlist_videos(self, playlist_id: str) -> List[str]:
        """プレイリスト内のビデオIDリストを取得します。

        Args:
            playlist_id: YouTubeプレイリストID。

        Returns:
            ビデオIDのリスト。
        """
        try:
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            playlist = YouTube(playlist_url)
            return []  # Placeholder - actual implementation would return video IDs
        except Exception as e:
            logger.warning(f"プレイリストの取得に失敗しました: {playlist_id}, エラー: {e}")
            return []

    def get_documents_from_playlist(self, playlist_url: str) -> List[Document]:
        """YouTubeプレイリストからドキュメントを取得します。

        Args:
            playlist_url: YouTubeプレイリストのURL。

        Returns:
            ドキュメントのリスト。
        """
        playlist_id = self._extract_playlist_id(playlist_url)
        logger.info(f"プレイリストID: {playlist_id} のビデオを取得します")

        video_ids = self._get_playlist_videos(playlist_id)
        if not video_ids:
            logger.warning(f"プレイリスト内のビデオが見つかりませんでした: {playlist_id}")
            return []

        documents = []
        for video_id in video_ids:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            docs = self.youtube_adapter.get_documents_from_url(video_url)
            documents.extend(docs)

        logger.info(f"プレイリスト: {playlist_id} から {len(documents)} 個のドキュメントを取得しました")
        return documents


class YouTubeCSVAdapter:
    """CSVファイルからYouTubeビデオのリストを読み込み、トランスクリプトを取得するアダプター。"""

    def __init__(
        self,
        url_column: str,
        metadata_columns: Optional[List[str]] = None,
        language_code: str = "ja",
        metadata_extractor: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        """YouTubeCSVアダプターを初期化します。

        Args:
            url_column: YouTubeビデオURLが含まれる列名。
            metadata_columns: CSVファイルからメタデータとして抽出する列名のリスト。
            language_code: 取得するトランスクリプトの言語コード。
            metadata_extractor: メタデータ抽出関数。
        """
        self.url_column = url_column
        self.metadata_columns = metadata_columns or []
        self.youtube_adapter = YouTubeAdapter(language_code, metadata_extractor)

    def get_documents_from_csv(self, csv_path: Union[str, Path]) -> List[Document]:
        """CSVファイルからYouTubeビデオのトランスクリプトを取得します。

        Args:
            csv_path: CSVファイルのパス。

        Returns:
            ドキュメントのリスト。
        """
        csv_path = Path(csv_path)
        logger.info(f"CSVファイルを読み込み中: {csv_path}")

        try:
            df = pd.read_csv(csv_path)
            if self.url_column not in df.columns:
                logger.error(f"指定された列 '{self.url_column}' がCSVファイルに存在しません")
                return []

            documents = []
            for i, row in df.iterrows():
                url = row[self.url_column]
                if not url or pd.isna(url):
                    continue

                csv_metadata = {}
                for col in self.metadata_columns:
                    if col in df.columns and not pd.isna(row[col]):
                        csv_metadata[col] = row[col]

                def custom_metadata_extractor(video_id, metadata):
                    metadata.update(csv_metadata)
                    metadata["source"] = str(csv_path)
                    metadata["row"] = i
                    return metadata

                original_extractor = self.youtube_adapter.metadata_extractor
                self.youtube_adapter.metadata_extractor = custom_metadata_extractor

                docs = self.youtube_adapter.get_documents_from_url(url)
                documents.extend(docs)

                self.youtube_adapter.metadata_extractor = original_extractor

            logger.info(f"{csv_path} から {len(documents)} 個のドキュメントを読み込みました")
            return documents

        except Exception as e:
            logger.error(f"CSVファイルの読み込みに失敗しました: {csv_path}, エラー: {e}")
            return []
