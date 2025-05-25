"""データソースアダプターパッケージ。

このパッケージは、様々なデータソースからドキュメントを読み込むためのアダプターを提供します。
"""

from .text_file import TextFileAdapter, TextDirectoryAdapter
from .csv_file import CSVFileAdapter, CSVDirectoryAdapter, load_qa_dataset_from_csv
from .youtube import YouTubeAdapter, YouTubePlaylistAdapter, YouTubeCSVAdapter

__all__ = [
    "TextFileAdapter",
    "TextDirectoryAdapter",
    "CSVFileAdapter",
    "CSVDirectoryAdapter",
    "load_qa_dataset_from_csv",
    "YouTubeAdapter",
    "YouTubePlaylistAdapter",
    "YouTubeCSVAdapter",
]
