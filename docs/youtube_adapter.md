# YouTubeトランスクリプトアダプター

このドキュメントでは、YouTubeビデオのトランスクリプト（字幕）を取得し、ベクトルデータベースを作成するためのアダプターの使用方法について説明します。

## 概要

YouTubeトランスクリプトアダプターは、YouTubeビデオの字幕データを取得し、それをドキュメントとして処理するための機能を提供します。これにより、YouTubeコンテンツに基づいたベクトルデータベースを作成し、検索や分析を行うことができます。

## 主な機能

- 単一のYouTubeビデオからトランスクリプトを取得
- 複数のYouTubeビデオからトランスクリプトを取得
- YouTubeプレイリストからトランスクリプトを取得
- CSVファイルに記載されたYouTubeビデオURLからトランスクリプトを取得

## 必要なパッケージ

YouTubeトランスクリプトアダプターを使用するには、以下のパッケージをインストールする必要があります：

```bash
pip install youtube-transcript-api pytube
```

## 基本的な使い方

### 単一のYouTubeビデオからトランスクリプトを取得

```python
from src.adapters import YouTubeAdapter
from src.core import VectorDBBuilder

# YouTubeアダプターの初期化（日本語トランスクリプトを取得）
youtube_adapter = YouTubeAdapter(language_code="ja")

# YouTubeビデオからドキュメントを取得
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # サンプルURL
documents = youtube_adapter.get_documents_from_url(youtube_url)

# ベクトルデータベースの構築（ローカルの埋め込みモデルを使用）
builder = VectorDBBuilder(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    use_local_embeddings=True,
)
vector_db = builder.build_vector_db(documents)

# ベクトルデータベースの保存
vector_db.save("path/to/output_dir")
```

### 複数のYouTubeビデオからトランスクリプトを取得

```python
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

### CSVファイルからYouTubeビデオのトランスクリプトを取得

```python
from src.adapters import YouTubeCSVAdapter
from src.core import VectorDBBuilder

# YouTubeCSVアダプターの初期化
youtube_csv_adapter = YouTubeCSVAdapter(
    url_column="video_url",  # YouTubeビデオURLが含まれる列名
    metadata_columns=["title", "category"],  # メタデータとして抽出する列名
    language_code="ja",
)

# CSVファイルからドキュメントを取得
documents = youtube_csv_adapter.get_documents_from_csv("path/to/youtube_videos.csv")

# ベクトルデータベースの構築
builder = VectorDBBuilder(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    use_local_embeddings=True,
)
vector_db = builder.build_vector_db(documents)
```

## 詳細設定

### 言語の指定

デフォルトでは日本語（`ja`）のトランスクリプトを取得しますが、他の言語を指定することもできます：

```python
# 英語のトランスクリプトを取得
youtube_adapter = YouTubeAdapter(language_code="en")

# フランス語のトランスクリプトを取得
youtube_adapter = YouTubeAdapter(language_code="fr")
```

### カスタムメタデータ抽出

メタデータ抽出関数を指定して、ビデオIDとデフォルトのメタデータから追加のメタデータを生成できます：

```python
def custom_metadata_extractor(video_id, metadata):
    # 追加のメタデータを生成
    metadata["custom_field"] = f"custom-{video_id}"
    return metadata

youtube_adapter = YouTubeAdapter(
    language_code="ja",
    metadata_extractor=custom_metadata_extractor,
)
```

## 注意事項

- YouTubeのトランスクリプトは、ビデオの作成者が提供している場合にのみ取得できます。
- 一部のビデオでは、指定した言語のトランスクリプトが利用できない場合があります。
- YouTubeのAPIポリシーに従って使用してください。大量のリクエストを短時間に行うと、一時的にブロックされる可能性があります。
