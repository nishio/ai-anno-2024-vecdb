"""ベクトルデータベース作成のためのCLIツール。

このモジュールは、様々なデータソースからベクトルデータベースを作成するための
コマンドラインインターフェースを提供します。
"""
import logging
import os
from pathlib import Path
from typing import List, Optional

import click
from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter

from ai_anno_2024_vecdb.adapters.csv_file import CSVFileAdapter
from ai_anno_2024_vecdb.adapters.text_file import TextFileAdapter
from ai_anno_2024_vecdb.core.vector_db import FAISSVectorDB, VectorDBBuilder

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """ベクトルデータベース作成のためのCLIツール。"""
    pass


@cli.command()
@click.option(
    "--input-dir",
    "-i",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="テキストファイルが含まれるディレクトリのパス",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="ベクトルデータベースを保存するディレクトリのパス",
)
@click.option(
    "--file-extension",
    "-e",
    type=str,
    default=".txt",
    help="処理するファイルの拡張子",
)
@click.option(
    "--chunk-size",
    "-c",
    type=int,
    default=1000,
    help="テキストチャンクのサイズ",
)
@click.option(
    "--chunk-overlap",
    "-v",
    type=int,
    default=200,
    help="テキストチャンクのオーバーラップ",
)
@click.option(
    "--embedding-model",
    "-m",
    type=str,
    default="models/text-embedding-004",
    help="埋め込みモデルの名前",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="デバッグログを有効にする",
)
def from_text(
    input_dir: Path,
    output_dir: Path,
    file_extension: str,
    chunk_size: int,
    chunk_overlap: int,
    embedding_model: str,
    debug: bool,
) -> None:
    """テキストファイルからベクトルデータベースを作成します。"""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    adapter = TextFileAdapter(
        directory_path=input_dir,
        file_extension=file_extension,
    )
    
    documents = adapter.get_documents()
    logger.info(f"{len(documents)}個のドキュメントを読み込みました")
    
    vector_db = FAISSVectorDB(
        embedding_model=embedding_model,
        text_splitter=text_splitter,
    )
    vector_db.build_from_documents(documents)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    vector_db.save(output_dir)
    logger.info(f"ベクトルデータベースを{output_dir}に保存しました")
    
    test_query = "テスト"
    results = vector_db.query(test_query, top_k=1)
    if results:
        content, metadata = results[0]
        logger.info(f"テストクエリ: {test_query}")
        logger.info(f"最も関連性の高いドキュメント: {content[:100]}...")
        logger.info(f"メタデータ: {metadata}")


@cli.command()
@click.option(
    "--input-csv",
    "-i",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help="CSVファイルのパス",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="ベクトルデータベースを保存するディレクトリのパス",
)
@click.option(
    "--content-column",
    "-c",
    type=str,
    required=True,
    help="コンテンツ列の名前",
)
@click.option(
    "--metadata-columns",
    "-m",
    type=str,
    multiple=True,
    help="メタデータ列の名前",
)
@click.option(
    "--chunk-size",
    type=int,
    default=1000,
    help="テキストチャンクのサイズ",
)
@click.option(
    "--chunk-overlap",
    type=int,
    default=200,
    help="テキストチャンクのオーバーラップ",
)
@click.option(
    "--embedding-model",
    type=str,
    default="models/text-embedding-004",
    help="埋め込みモデルの名前",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="デバッグログを有効にする",
)
def from_csv(
    input_csv: Path,
    output_dir: Path,
    content_column: str,
    metadata_columns: List[str],
    chunk_size: int,
    chunk_overlap: int,
    embedding_model: str,
    debug: bool,
) -> None:
    """CSVファイルからベクトルデータベースを作成します。"""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    adapter = CSVFileAdapter(
        file_path=input_csv,
        content_columns=[content_column],
        metadata_columns=list(metadata_columns) if metadata_columns else None,
    )
    
    documents = adapter.get_documents()
    logger.info(f"{len(documents)}個のドキュメントを読み込みました")
    
    vector_db = FAISSVectorDB(
        embedding_model=embedding_model,
        text_splitter=text_splitter,
    )
    vector_db.build_from_documents(documents)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    vector_db.save(output_dir)
    logger.info(f"ベクトルデータベースを{output_dir}に保存しました")
    
    test_query = "テスト"
    results = vector_db.query(test_query, top_k=1)
    if results:
        content, metadata = results[0]
        logger.info(f"テストクエリ: {test_query}")
        logger.info(f"最も関連性の高いドキュメント: {content[:100]}...")
        logger.info(f"メタデータ: {metadata}")


if __name__ == "__main__":
    cli()
