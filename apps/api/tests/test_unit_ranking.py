from searchops.ingestion.pipeline import Chunker, TextCleaner
from searchops.query.understanding import heuristic_extract
from searchops.ranking.fusion import fuse_linear, min_max_normalize
from searchops.evaluation.metrics import mrr, ndcg_at_k, recall_at_k


def test_chunker_overlap():
    text = "abcdefghij" * 80
    chunks = Chunker(size=100, overlap=20).split(text)
    assert len(chunks) > 1
    assert chunks[0].content
    assert chunks[1].index == 1


def test_cleaner_strips():
    assert TextCleaner().clean("  hello \n\n\n world  ") == "hello \n\n world"


def test_fusion_alpha():
    assert fuse_linear(1, 0, 0) == 1
    assert fuse_linear(0, 1, 1) == 1
    assert abs(fuse_linear(1, 1, 0.6) - 1) < 1e-9


def test_minmax():
    assert min_max_normalize([2, 4, 6]) == [0.0, 0.5, 1.0]
    assert min_max_normalize([]) == []


def test_query_parse_laptop():
    extracted = heuristic_extract("laptops under 80000 with 16GB RAM")
    assert extracted.filters["price_max"] == 80000
    assert extracted.filters["ram_gb"] == 16
    assert extracted.filters["category"] == "laptop"


def test_recall_mrr_ndcg():
    relevant = ["a", "b"]
    ranked = ["x", "a", "b"]
    assert recall_at_k(relevant, ranked, 10) == 1.0
    assert recall_at_k(relevant, ranked, 1) == 0.0
    assert mrr(relevant, ranked) == 0.5
    ndcg = ndcg_at_k({"a": 3, "b": 1, "x": 0}, ranked, 10)
    assert 0 < ndcg <= 1
