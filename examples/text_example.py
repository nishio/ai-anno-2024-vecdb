"""テキストファイルからベクトルデータベースを作成する例。

このスクリプトは、テキストファイルからベクトルデータベースを作成し、
簡単なクエリを実行する方法を示します。ローカルの埋め込みモデルを使用するため、
APIキーは必要ありません。
"""
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.adapters.text_file import TextFileAdapter
from src.core.vector_db import FAISSVectorDB


def main():
    """テキストファイルからベクトルデータベースを作成する例を実行します。"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    input_dir = Path("examples/data/text")
    output_dir = Path("examples/output/vector_db")

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    sample_file = input_dir / "sample.txt"
    with open(sample_file, "w") as f:
        f.write(
            "これはサンプルテキストファイルです。\n"
            "ベクトルデータベースを作成するためのテストデータとして使用します。\n"
            "このファイルは、テキストファイルアダプターのテストに使用されます。\n"
            "ベクトルデータベースは、テキストデータから作成され、検索に使用されます。\n"
        )

    logger.info(f"サンプルテキストファイルを {sample_file} に作成しました")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
    )

    adapter = TextFileAdapter(
        directory_path=input_dir,
        file_extension=".txt",
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
        "ベクトルデータベースとは何ですか？",
        "テキストファイルアダプターの役割は？",
        "このサンプルの目的は？",
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
