"""Configurações globais para o projeto."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final


PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DIR: Path = DATA_DIR / "raw"
PROCESSED_DIR: Path = DATA_DIR / "processed"

B2W_RAW_PATH: Path = RAW_DIR / "b2w_reviews.csv"
OCTAPRICE_RAW_DIR: Path = RAW_DIR / "octaprice"
ALL_REVIEWS_PATH: Path = PROCESSED_DIR / "all_reviews.parquet"
SAMPLE_REVIEWS_PATH: Path = PROCESSED_DIR / "sample.parquet"

for directory in (RAW_DIR, PROCESSED_DIR):
    directory.mkdir(parents=True, exist_ok=True)


MIN_REVIEW_LENGTH: Final[int] = 10
MIN_REVIEW_WORDS: Final[int] = 3
SAMPLE_SIZE_DEV: Final[int] = 50_000
RANDOM_STATE: Final[int] = 42
PARQUET_COMPRESSION: Final[str] = "snappy"

STANDARD_COLUMNS: Final[list[str]] = ["review", "score", "product_name", "source"]
PROCESSED_DATASET_PATHS: Final[dict[str, Path]] = {
    "b2w": PROCESSED_DIR / "b2w_reviews.parquet",
    "olist": PROCESSED_DIR / "olist_reviews.parquet",
    "buscape": PROCESSED_DIR / "buscape_reviews.parquet",
    "octaprice": PROCESSED_DIR / "octaprice_reviews.parquet",
}


@dataclass(frozen=True)
class ColumnSpec:
    review: tuple[str, ...]
    score: tuple[str, ...]
    product_name: tuple[str, ...] = ()
    review_parts: tuple[str, ...] = ()


DATASET_SPECS: Final[dict[str, ColumnSpec]] = {
    "b2w": ColumnSpec(
        review=("review_text",),
        score=("overall_rating",),
        product_name=("product_name",),
    ),
    "olist": ColumnSpec(
        review=("review_comment_message",),
        score=("review_score",),
        review_parts=("review_comment_title", "review_comment_message"),
    ),
    "buscape": ColumnSpec(
        review=("review_text", "review", "text", "comentario", "comment", "content"),
        score=("rating", "score", "stars", "nota", "overall_rating", "polarity"),
        product_name=("product_name", "produto", "product", "title"),
    ),
    "octaprice": ColumnSpec(
        review=(
            "review",
            "reviews",
            "review_text",
            "top_reviews",
            "comments",
            "content",
        ),
        score=("score", "rating", "stars", "review_score"),
        product_name=("product_name", "name", "title", "product_title"),
    ),
}
