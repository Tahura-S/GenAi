from pathlib import Path
import yaml


def parse_markdown(file_path: Path):
    """
    Parse a markdown policy document with YAML front matter.

    Returns:
        tuple: (metadata, content)
    """
    text = file_path.read_text(encoding="utf-8")

    parts = text.split("---")

    if len(parts) < 3:
        raise ValueError(f"Invalid markdown format: {file_path}")

    yaml_text = parts[1].strip()
    content = parts[2].strip()

    metadata = yaml.safe_load(yaml_text)

    return metadata, content