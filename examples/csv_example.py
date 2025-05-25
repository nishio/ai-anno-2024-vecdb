"""CSVファイルからベクトルデータベースを作成する例。

このスクリプトは、CSVファイルからベクトルデータベースを作成し、
簡単なクエリを実行する方法を示します。ローカルの埋め込みモデルを使用するため、
APIキーは必要ありません。
"""
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.adapters.csv_file import CSVFileAdapter
from src.core.vector_db import FAISSVectorDB


def main():
    """CSVファイルからベクトルデータベースを作成する例を実行します。"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    input_dir = Path("examples/data/csv")
    output_dir = Path("examples/output/vector_db_csv")

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    sample_file = input_dir / "sample.csv"
    
    data = {
        "質問": [
            "ベクトルデータベースとは何ですか？",
            "FAISSとは何ですか？",
            "埋め込みモデルとは何ですか？",
            "テキスト分割はなぜ必要ですか？",
        ],
        "回答": [
            "ベクトルデータベースは、テキストや画像などのデータを数値ベクトルとして保存し、類似度検索を可能にするデータベースです。",
            "FAISSは、Facebookが開発した高速な類似度検索ライブラリで、大規模なベクトルデータセットに対して効率的な検索を提供します。",
            "埋め込みモデルは、テキストや画像などの非構造化データを固定長の数値ベクトルに変換するモデルです。",
            "テキスト分割は、長いテキストを適切なサイズのチャンクに分割することで、埋め込みモデルの性能を向上させ、より関連性の高い検索結果を得るために必要です。",
        ],
        "カテゴリ": [
            "データベース",
            "ライブラリ",
            "モデル",
            "前処理",
        ],
    }
    
    df = pd.DataFrame(data)
    df.to_csv(sample_file, index=False)
    
    logger.info(f"サンプルCSVファイルを {sample_file} に作成しました")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,
    )

    adapter = CSVFileAdapter(
        file_path=sample_file,
        content_columns=["質問", "回答"],
        metadata_columns=["カテゴリ"],
    )

    documents = adapter.get_documents()
    logger.info(f"{len(documents)}個のドキュメントを読み込みました")

    vector_db = FAISSVectorDB(
        embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        use_local_embeddings=True,  # ローカルの埋め込みモデルを使用
        text_splitter=text_splitter,
    )
    vector_db.build_from_documents(documents)

    vector_db.save(output_dir)
    logger.info(f"ベクトルデータベースを {output_dir} に保存しました")

    queries = [
        "ベクトルデータベースの用途は？",
        "FAISSの特徴は？",
        "テキスト分割の目的は？",
    ]

    for query in queries:
        logger.info(f"\nクエリ: {query}")
        results = vector_db.query(query, top_k=1)
        for i, (content, metadata) in enumerate(results):
            logger.info(f"結果 {i+1}:")
            logger.info(f"コンテンツ: {content}")
            logger.info(f"メタデータ: {metadata}")


if __name__ == "__main__":
    main()
