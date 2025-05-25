# PR説明: ベクトルデータベース標準化ツールキットの実装

このPRでは、ベクトルデータベース作成のための標準化されたツールキットを実装しました。VTuber機能から分離され、様々なデータソースに対応できるモジュラーな設計になっています。

## 主な変更点

### コア機能
- `FAISSVectorDB` クラスの実装 - ベクトルデータベースの作成、保存、読み込み、クエリ機能
- 検索機能の実装 - FAISS検索、BM25検索、ハイブリッド検索
- テキスト分割と埋め込み生成の標準化

### データソースアダプター
- テキストファイルアダプター - テキストファイルからドキュメントを読み込む
- CSVファイルアダプター - CSVファイルからドキュメントを読み込む
- Q&Aデータセットアダプター - Q&AデータセットをCSVファイルから読み込む

### CLIツール
- テキストファイルからベクトルデータベースを作成するコマンド
- CSVファイルからベクトルデータベースを作成するコマンド

### ドキュメントと例
- 使用方法のドキュメント
- アダプターのドキュメント
- テキストファイルとCSVファイルの使用例

## 実装の詳細

### ベクトルデータベース操作
ベクトルデータベースの操作は `FAISSVectorDB` クラスで実装されています。このクラスは以下の機能を提供します：

- ドキュメントからベクトルデータベースを構築する
- ベクトルデータベースを保存する
- ベクトルデータベースを読み込む
- クエリを実行して関連するドキュメントを取得する

```python
from ai_anno_2024_vecdb.core.vector_db import FAISSVectorDB

# ベクトルデータベースの作成
vector_db = FAISSVectorDB(
    embedding_model="models/text-embedding-004",
    text_splitter=text_splitter,
)
vector_db.build_from_documents(documents)

# ベクトルデータベースの保存
vector_db.save(output_dir)

# クエリの実行
results = vector_db.query("あなたの質問", top_k=5)
```

### 検索機能
検索機能は `retrieval.py` モジュールで実装されています。このモジュールは以下の検索機能を提供します：

- FAISS検索 - ベクトル類似度に基づく検索
- BM25検索 - キーワードに基づく検索
- ハイブリッド検索 - FAISS検索とBM25検索を組み合わせた検索

```python
from ai_anno_2024_vecdb.core.retrieval import FAISSRetriever, BM25Retriever, HybridRetriever

# FAISS検索
faiss_retriever = FAISSRetriever(vector_db_path="path/to/vector_db")
results = faiss_retriever.get_relevant_documents("あなたの質問", top_k=5)

# BM25検索
bm25_retriever = BM25Retriever(documents=documents)
results = bm25_retriever.get_relevant_documents("あなたの質問", top_k=5)

# ハイブリッド検索
hybrid_retriever = HybridRetriever(
    vector_retriever=faiss_retriever,
    bm25_retriever=bm25_retriever,
    weights=[0.5, 0.5],
)
results = hybrid_retriever.get_relevant_documents("あなたの質問", top_k=5)
```

### データソースアダプター
データソースアダプターは `adapters` パッケージで実装されています。このパッケージは以下のアダプターを提供します：

- テキストファイルアダプター - テキストファイルからドキュメントを読み込む
- CSVファイルアダプター - CSVファイルからドキュメントを読み込む
- Q&Aデータセットアダプター - Q&AデータセットをCSVファイルから読み込む

```python
from ai_anno_2024_vecdb.adapters.text_file import TextFileAdapter
from ai_anno_2024_vecdb.adapters.csv_file import CSVFileAdapter, load_qa_dataset_from_csv

# テキストファイルアダプター
text_adapter = TextFileAdapter(directory_path="path/to/text/files")
documents = text_adapter.get_documents()

# CSVファイルアダプター
csv_adapter = CSVFileAdapter(
    file_path="path/to/csv/file.csv",
    content_columns=["質問", "回答"],
    metadata_columns=["カテゴリ"],
)
documents = csv_adapter.get_documents()

# Q&Aデータセットアダプター
qa_documents = load_qa_dataset_from_csv(
    file_path="path/to/qa/dataset.csv",
    question_column="質問",
    answer_column="回答",
    metadata_columns=["カテゴリ"],
)
```

### CLIツール
CLIツールは `cli` パッケージで実装されています。このパッケージは以下のコマンドを提供します：

- `from-text` - テキストファイルからベクトルデータベースを作成する
- `from-csv` - CSVファイルからベクトルデータベースを作成する

```bash
# テキストファイルからベクトルデータベースを作成する
python -m ai_anno_2024_vecdb.cli.create_vector_db from-text \
    --input-dir path/to/text/files \
    --output-dir path/to/save/vector_db \
    --file-extension .txt \
    --chunk-size 1000 \
    --chunk-overlap 200 \
    --embedding-model models/text-embedding-004

# CSVファイルからベクトルデータベースを作成する
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

## 次のステップ
- YouTubeの文字起こしデータに対応するアダプターの実装
- PDFファイルに対応するアダプターの実装
- テスト機能の強化
