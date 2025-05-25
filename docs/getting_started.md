# はじめに

このドキュメントでは、ai-anno-2024-vecdbの基本的な使い方を説明します。

## インストール

リポジトリをクローンして、開発モードでインストールします。

```bash
git clone https://github.com/nishio/ai-anno-2024-vecdb.git
cd ai-anno-2024-vecdb
pip install -e .
```

## 環境変数の設定

Google Generative AI APIキーを環境変数として設定します。

```bash
export GOOGLE_API_KEY="your-api-key"
```

または、Pythonコード内で設定することもできます。

```python
import os
os.environ["GOOGLE_API_KEY"] = "your-api-key"
```

## 基本的な使い方

### テキストファイルからベクトルデータベースを作成する

```python
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ai_anno_2024_vecdb.adapters.text_file import TextFileAdapter
from ai_anno_2024_vecdb.core.vector_db import FAISSVectorDB

# テキスト分割器の作成
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

# テキストファイルアダプターの作成
adapter = TextFileAdapter(
    directory_path=Path("path/to/text/files"),
    file_extension=".txt",
)

# ドキュメントの取得
documents = adapter.get_documents()

# ベクトルデータベースの作成
vector_db = FAISSVectorDB(
    embedding_model="models/text-embedding-004",
    text_splitter=text_splitter,
)
vector_db.build_from_documents(documents)

# ベクトルデータベースの保存
vector_db.save(Path("path/to/save/vector_db"))

# クエリの実行
results = vector_db.query("あなたの質問", top_k=5)
for content, metadata in results:
    print(f"Content: {content}")
    print(f"Metadata: {metadata}")
```

### CSVファイルからベクトルデータベースを作成する

```python
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ai_anno_2024_vecdb.adapters.csv_file import CSVFileAdapter
from ai_anno_2024_vecdb.core.vector_db import FAISSVectorDB

# テキスト分割器の作成
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

# CSVファイルアダプターの作成
adapter = CSVFileAdapter(
    file_path=Path("path/to/csv/file.csv"),
    content_columns=["質問", "回答"],
    metadata_columns=["カテゴリ"],
)

# ドキュメントの取得
documents = adapter.get_documents()

# ベクトルデータベースの作成
vector_db = FAISSVectorDB(
    embedding_model="models/text-embedding-004",
    text_splitter=text_splitter,
)
vector_db.build_from_documents(documents)

# ベクトルデータベースの保存
vector_db.save(Path("path/to/save/vector_db"))

# クエリの実行
results = vector_db.query("あなたの質問", top_k=5)
for content, metadata in results:
    print(f"Content: {content}")
    print(f"Metadata: {metadata}")
```

## コマンドラインツールの使用

### テキストファイルからベクトルデータベースを作成する

```bash
python -m ai_anno_2024_vecdb.cli.create_vector_db from-text \
    --input-dir path/to/text/files \
    --output-dir path/to/save/vector_db \
    --file-extension .txt \
    --chunk-size 1000 \
    --chunk-overlap 200 \
    --embedding-model models/text-embedding-004
```

### CSVファイルからベクトルデータベースを作成する

```bash
python -m ai_anno_2024_vecdb.cli.create_vector_db from-csv \
    --input-csv path/to/csv/file.csv \
    --output-dir path/to/save/vector_db \
    --content-column 質問 \
    --content-column 回答 \
    --metadata-column カテゴリ \
    --chunk-size 1000 \
    --chunk-overlap 200 \
    --embedding-model models/text-embedding-004
```
