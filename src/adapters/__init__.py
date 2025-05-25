"""データソースアダプターパッケージ。

このパッケージは、様々なデータソースからドキュメントを読み込むためのアダプターを提供します。
"""

from .text_file import TextFileAdapter, TextDirectoryAdapter
from .csv_file import CSVFileAdapter, CSVDirectoryAdapter, load_qa_dataset_from_csv

__all__ = [
    "TextFileAdapter",
    "TextDirectoryAdapter",
    "CSVFileAdapter",
    "CSVDirectoryAdapter",
    "load_qa_dataset_from_csv",
]
