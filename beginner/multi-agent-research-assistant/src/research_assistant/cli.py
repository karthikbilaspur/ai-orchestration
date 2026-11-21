import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from .agents import ResearchAgents
from .config import get_settings
from .graph import create_graph
from .models import ResearchRequest


def configure_logging(level: str):
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Multi-agent research assistant")
    parser.add_argument("--question", help="Research question")
    parser.add_argument("--audience", default="general reader")
    parser.add_argument("--depth", choices=["concise", "standard", "deep"], default="standard")
    parser.add_argument("--source-file", help="Text file containing source material")
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.log_level)

    question = args.question or input("What would you like to research? ").strip()
    source_text = None
    if args.source_file:
        source_text = Path(args.source_file).read_text(encoding="utf-8")
    elif not settings.tavily_api_key:
        print("\nNo TAVILY_API_KEY found. Paste source material below.")
        print("Finish input with a line containing only END.")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        source_text = "\n".join(lines)

    request = ResearchRequest(
        question=question,
        audience=args.audience,
        depth=args.depth,
        source_text=source_text,
    )

    agents = ResearchAgents(settings)
    app = create_graph(agents)
    result = app.invoke({"request": request})
    report = result["report_markdown"]

    Path("reports").mkdir(exist_ok=True)
    output_path = Path("reports/research_report.md")
    output_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {output_path.resolve()}\n")
    print(report)


if __name__ == "__main__":
    main()
