"""
Project 14 — AI Document Processing Pipeline
Usage:
  python main.py <file.txt|file.pdf> [--output out.json] [--pretty]
"""
import argparse, json, sys, pathlib
from pipeline import DocumentPipeline
def main():
    p = argparse.ArgumentParser(description="AI Document Processing Pipeline")
    p.add_argument("file", help="Path to .txt or .pdf document")
    p.add_argument("--output", "-o", help="Write JSON to file")
    p.add_argument("--pretty", action="store_true", help="Pretty print")
    args = p.parse_args()
    path = pathlib.Path(args.file)
    if not path.exists():
        print(f"File not found: {path}"); sys.exit(1)
    pipeline = DocumentPipeline()
    result = pipeline.run(str(path))
    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.output).write_text(out, encoding="utf-8")
        print(f"Saved to {args.output}")
    print(out)
    if not result.get("is_valid"):
        print(f"\nValidation: {result.get('validation_errors')}")
    else:
        print("\nValidation passed")
if __name__ == "__main__":
    main()
