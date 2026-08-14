from pathlib import Path

path = Path(__file__).resolve().parent.parent / "templates"

print(f"PATH: {path}")
print(f"EXISITING: {path.exists()}")