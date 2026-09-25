from pathlib import Path

from searchops.ingestion.loaders import loader_for


def test_loaders(tmp_path: Path):
    txt = tmp_path / "a.txt"
    txt.write_text("hello txt", encoding="utf-8")
    md = tmp_path / "b.md"
    md.write_text("# Title\nbody", encoding="utf-8")
    js = tmp_path / "c.json"
    js.write_text('[{"title":"J","content":"json doc","category":"x"}]', encoding="utf-8")
    csv = tmp_path / "d.csv"
    csv.write_text("title,content\nC,csv row\n", encoding="utf-8")
    assert loader_for(txt).load(txt)[0].content == "hello txt"
    assert loader_for(md).load(md)[0].title == "Title"
    assert loader_for(js).load(js)[0].metadata["category"] == "x"
    assert "csv" in loader_for(csv).load(csv)[0].content.lower() or loader_for(csv).load(csv)[0].title == "C"


def test_unsupported(tmp_path: Path):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF")
    try:
        loader_for(pdf)
        assert False, "expected error"
    except ValueError:
        pass
