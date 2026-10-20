import argparse, sys
from pathlib import Path
from .core import load_definition, to_mermaid, to_powerbi_relationships, to_turtle

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="fabric-ontology-export", description="Export a Fabric IQ ontology definition.")
    ap.add_argument("definition", help="ontology item definition JSON (envelope with definition.parts)")
    ap.add_argument("--format", choices=["mermaid", "tmdl", "turtle"], default="mermaid")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    onto = load_definition(a.definition)
    text = {"mermaid": to_mermaid, "tmdl": to_powerbi_relationships, "turtle": to_turtle}[a.format](onto)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8"); print(f"wrote {a.out}")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    sys.exit(main())
