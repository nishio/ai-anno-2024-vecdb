# データソースアダプター

このドキュメントでは、ai-anno-2024-vecdbで利用可能なデータソースアダプターについて説明します。

## アダプターとは

アダプターは、様々なデータソース（テキストファイル、CSVファイル、PDFファイル、YouTubeの文字起こしなど）からドキュメントを読み込み、ベクトルデータベースの作成に使用できる形式に変換する役割を担います。

各アダプターは、`get_documents()` メソッドを実装しており、このメソッドは `langchain.schema.document.Document` オブジェクトのリストを返します。

## 利用可能なアダプター

### テキストファイルアダプター

`TextFileAdapter` は、テキストファイルからドキュメントを読み込むためのアダプターです。

```python
from pathlib import Path
from ai_anno_2024_vecdb.adapters.text_file import TextFileAdapter

adapter = TextFileAdapter(
    directory_path=Path("path/to/text/files"),
    file_extension=".txt",
    encoding="utf-8",
)

documents = adapter.get_documents()
```

#### パラメータ

- `directory_path`: テキストファイルが含まれるディレクトリのパス。
- `file_extension`: 処理するファイルの拡張子。デフォルトは `.txt`。
- `encoding`: ファイルの文字エンコーディング。デフォルトは `utf-8`。
- `metadata_extractor`: ファイルの内容からメタデータを抽出する関数。デフォルトは `None`。

### CSVファイルアダプター

`CSVFileAdapter` は、CSVファイルからドキュメントを読み込むためのアダプターです。

```python
from pathlib import Path
from ai_anno_2024_vecdb.adapters.csv_file import CSVFileAdapter

adapter = CSVFileAdapter(
    file_path=Path("path/to/csv/file.csv"),
    content_columns=["質問", "回答"],
    metadata_columns=["カテゴリ"],
    encoding="utf-8",
    delimiter=",",
)

documents = adapter.get_documents()
```

#### パラメータ

- `file_path`: CSVファイルのパス。
- `content_columns`: コンテンツとして使用する列名のリスト。
- `metadata_columns`: メタデータとして使用する列名のリスト。デフォルトは `None`。
- `encoding`: ファイルの文字エンコーディング。デフォルトは `utf-8`。
- `delimiter`: CSVの区切り文字。デフォルトは `,`。

### Q&Aデータセットアダプター

`load_qa_dataset_from_csv` 関数は、Q&AデータセットをCSVファイルから読み込むためのユーティリティ関数です。

```python
from pathlib import Path
from ai_anno_2024_vecdb.adapters.csv_file import load_qa_dataset_from_csv

documents = load_qa_dataset_from_csv(
    file_path=Path("path/to/qa/dataset.csv"),
    question_column="質問",
    answer_column="回答",
    metadata_columns=["カテゴリ"],
    embed_answer=True,
)
```

#### パラメータ

- `file_path`: CSVファイルのパス。
- `question_column`: 質問列の名前。
- `answer_column`: 回答列の名前。
- `metadata_columns`: メタデータ列の名前のリスト。デフォルトは `None`。
- `embed_answer`: 回答もページコンテンツに含めるかどうか。デフォルトは `True`。

## 独自のアダプターを作成する

独自のアダプターを作成するには、`get_documents()` メソッドを実装したクラスを作成します。このメソッドは、`langchain.schema.document.Document` オブジェクトのリストを返す必要があります。

```python
from typing import List
from pathlib import Path
from langchain.schema.document import Document

class MyCustomAdapter:
    def __init__(self, custom_param):
        self.custom_param = custom_param
        
    def get_documents(self) -> List[Document]:
        # データソースからドキュメントを読み込む処理
        documents = []
        
        # ドキュメントの作成
        document = Document(
            page_content="ドキュメントの内容",
            metadata={"source": "データソース", "custom_field": "カスタムフィールド"},
        )
        documents.append(document)
        
        return documents
```

## 次のステップ

- [YouTubeの文字起こしアダプター](youtube_adapter.md)の実装（予定）
- [PDFファイルアダプター](pdf_adapter.md)の実装（予定）
