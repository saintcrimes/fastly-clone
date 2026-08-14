from pathlib import Path


def test_path_checking():
    path = Path(__file__).resolve().parent.parent.parent / "src"
    template_path = path / "templates"

    assert template_path.exists(), f"Missing: {template_path}"
    assert template_path.is_dir()
    assert (template_path / "main.html").exists()
