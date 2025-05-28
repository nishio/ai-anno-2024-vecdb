# はじめに

このドキュメントでは、ai-anno-2024-vecdbの基本的な使い方を説明します。ローカルの埋め込みモデルを使用するため、APIキーは必要ありません。

## インストール

リポジトリをクローンして、開発モードでインストールします。

```bash
git clone https://github.com/nishio/ai-anno-2024-vecdb.git
cd ai-anno-2024-vecdb
pip install -e .
```

## 依存関係のインストール

必要なパッケージをインストールします。

```bash
# 基本的な依存関係
pip install sentence-transformers langchain langchain-community faiss-cpu

# YouTubeトランスクリプト取得のための追加パッケージ（必要な場合）
pip install youtube-transcript-api pytube
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

# ベクトルデータベースの作成（ローカルの埋め込みモデルを使用）
vector_db = FAISSVectorDB(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    use_local_embeddings=True,  # ローカルの埋め込みモデルを使用
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

# ベクトルデータベースの作成（ローカルの埋め込みモデルを使用）
vector_db = FAISSVectorDB(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    use_local_embeddings=True,  # ローカルの埋め込みモデルを使用
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
    --embedding-model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 \
    --use-local-embeddings
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
    --embedding-model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 \
    --use-local-embeddings
```

## YouTubeトランスクリプトの使用

YouTubeビデオのトランスクリプト（字幕）からベクトルデータベースを作成することもできます。詳細は[YouTubeトランスクリプトアダプター](youtube_adapter.md)のドキュメントを参照してください。

### YouTubeビデオからベクトルデータベースを作成する

```python
from pathlib import Path
from src.adapters import YouTubeAdapter
from src.core import VectorDBBuilder

# YouTubeアダプターの初期化（日本語トランスクリプトを取得）
youtube_adapter = YouTubeAdapter(language_code="ja")

# YouTubeビデオからドキュメントを取得
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # サンプルURL
documents = youtube_adapter.get_documents_from_url(youtube_url)

# ベクトルデータベースビルダーの初期化（ローカルの埋め込みモデルを使用）
builder = VectorDBBuilder(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    use_local_embeddings=True,
)

# ベクトルデータベースの構築
vector_db = builder.build_vector_db(documents)

# ベクトルデータベースの保存
vector_db.save(Path("path/to/save/vector_db"))

# クエリの実行
results = vector_db.query("あなたの質問", top_k=5)
for content, metadata in results:
    print(f"Content: {content}")
    print(f"Metadata: {metadata}")
```

### 複数のYouTubeビデオからベクトルデータベースを作成する

```python
from pathlib import Path
from src.adapters import YouTubeAdapter
from src.core import VectorDBBuilder

# YouTubeアダプターの初期化
youtube_adapter = YouTubeAdapter(language_code="ja")

# 複数のYouTubeビデオからドキュメントを取得
youtube_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # サンプルURL1
    "https://www.youtube.com/watch?v=9bZkp7q19f0",  # サンプルURL2
]
documents = youtube_adapter.get_documents_from_urls(youtube_urls)

# ベクトルデータベースの構築
builder = VectorDBBuilder(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    use_local_embeddings=True,
)
vector_db = builder.build_vector_db(documents)
```
