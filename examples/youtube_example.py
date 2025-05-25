#!/usr/bin/env python
"""YouTubeトランスクリプトからベクトルデータベースを作成するサンプル。

このスクリプトは、YouTubeビデオのトランスクリプト（字幕）を取得し、
ローカルの埋め込みモデルを使用してベクトルデータベースを作成する方法を示します。
"""
import logging
import os
from pathlib import Path

from ai_anno_2024_vecdb.adapters import YouTubeAdapter
from ai_anno_2024_vecdb.core import FAISSVectorDB, VectorDBBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """メイン関数。"""
    output_dir = Path("examples/output/vector_db_youtube")
    os.makedirs(output_dir, exist_ok=True)

    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # サンプルURL

    youtube_adapter = YouTubeAdapter(language_code="ja")

    logger.info(f"YouTubeビデオからトランスクリプトを取得します: {youtube_url}")
    documents = youtube_adapter.get_documents_from_url(youtube_url)
    
    if not documents:
        logger.warning("トランスクリプトが取得できませんでした。別のビデオを試してください。")
        return
    
    logger.info(f"{len(documents)}個のドキュメントを読み込みました")

    builder = VectorDBBuilder(
        embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        use_local_embeddings=True,
    )

    vector_db = builder.build_vector_db(documents)
    
    vector_db.save(output_dir)
    logger.info(f"ベクトルデータベースを {output_dir} に保存しました")

    query_examples = [
        "この動画の内容は？",
        "主要なトピックは何ですか？",
        "話者は誰ですか？",
    ]

    for query in query_examples:
        logger.info(f"\nクエリ: {query}")
        results = vector_db.query(query, top_k=1)
        
        for i, (content, metadata) in enumerate(results, 1):
            logger.info(f"結果 {i}:")
            logger.info(f"コンテンツ: {content[:200]}...")  # 長いトランスクリプトは一部だけ表示
            logger.info(f"メタデータ: {metadata}")


def multiple_videos_example():
    """複数のYouTube動画からベクトルデータベースを作成する例。"""
    output_dir = Path("examples/output/vector_db_youtube_multiple")
    os.makedirs(output_dir, exist_ok=True)

    youtube_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # サンプルURL1
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # サンプルURL2
    ]

    youtube_adapter = YouTubeAdapter(language_code="ja")

    logger.info(f"{len(youtube_urls)}個のYouTubeビデオからトランスクリプトを取得します")
    documents = youtube_adapter.get_documents_from_urls(youtube_urls)
    
    if not documents:
        logger.warning("トランスクリプトが取得できませんでした。別のビデオを試してください。")
        return
    
    logger.info(f"{len(documents)}個のドキュメントを読み込みました")

    builder = VectorDBBuilder(
        embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        use_local_embeddings=True,
    )

    vector_db = builder.build_vector_db(documents)
    
    vector_db.save(output_dir)
    logger.info(f"ベクトルデータベースを {output_dir} に保存しました")

    query = "これらの動画の共通点は？"
    logger.info(f"\nクエリ: {query}")
    results = vector_db.query(query, top_k=2)
    
    for i, (content, metadata) in enumerate(results, 1):
        logger.info(f"結果 {i}:")
        logger.info(f"コンテンツ: {content[:200]}...")  # 長いトランスクリプトは一部だけ表示
        logger.info(f"メタデータ: {metadata}")


if __name__ == "__main__":
    main()
