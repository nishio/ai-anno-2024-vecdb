# ai-anno-2024-vecdb

ベクトルデータベース作成のための標準化されたツールキット。様々なデータソースからベクトルDBを作成し、質問応答システムを構築するためのモジュラーなフレームワークを提供します。

## 概要

このプロジェクトは、異なるデータソース（テキスト、PDF、YouTube動画など）からベクトルデータベースを作成するプロセスを標準化することを目的としています。これにより、RAG（Retrieval-Augmented Generation）システムの構築が容易になります。

## 特徴

- **モジュラー設計**: データソースアダプター、埋め込みモデル、ベクトルストアを柔軟に組み合わせ可能
- **シンプルなAPI**: 複雑な実装を隠蔽し、簡単に使えるインターフェースを提供
- **拡張性**: 新しいデータソースや埋め込みモデルを簡単に追加可能
- **ローカル実行**: ローカル環境で実行可能で、APIキーの管理も簡単

## インストール

```bash
pip install -e .
```

## 使用方法

### テキストデータからベクトルDBを作成

```python
from ai_anno_2024_vecdb import VectorDBBuilder
from ai_anno_2024_vecdb.adapters import TextFileAdapter

# テキストファイルアダプターを作成
adapter = TextFileAdapter("path/to/text/files")

# ドキュメントを取得
documents = adapter.get_documents()

# ベクトルDBを構築
builder = VectorDBBuilder()
vector_db = builder.build(documents)

# 質問に対する回答を取得
results = vector_db.query("あなたの質問")
for content, metadata in results:
    print(f"Content: {content}")
    print(f"Metadata: {metadata}")
```

## プロジェクト構造

```
ai-anno-2024-vecdb/
├── src/
│   ├── adapters/       # データソースアダプター
│   ├── core/           # コア機能（ベクトルDB、埋め込みなど）
│   ├── cli/            # コマンドラインインターフェース
│   └── utils/          # ユーティリティ関数
├── docs/               # ドキュメント
├── examples/           # 使用例
└── tests/              # テスト
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
