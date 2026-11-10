"""CLI: python -m src.main --topic "..." --audience "..." --tone "..." """
import argparse, sys
from .models import TopicRequest
from .orchestrator import Orchestrator

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="AI Content Creation & Review Studio")
    p.add_argument("--topic", required=True, help="Topic to write about")
    p.add_argument("--audience", default="general readers")
    p.add_argument("--tone", default="helpful, clear")
    p.add_argument("--format", default="blog", choices=["blog","linkedin","newsletter","twitter-thread"])
    p.add_argument("--length", default="medium", choices=["short","medium","long"])
    p.add_argument("--threshold", type=int, default=80)
    p.add_argument("--max-loops", type=int, default=3)
    p.add_argument("--output", default=None, help="Save final markdown to this file")
    p.add_argument("--interactive", action="store_true")
    p.add_argument("--no-seo", action="store_true")
    return p.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)
    req = TopicRequest(topic=args.topic, audience=args.audience, tone=args.tone, format=args.format, length=args.length, threshold=args.threshold, max_loops=args.max_loops)
    orch = Orchestrator(use_seo=not args.no_seo)
    final = orch.run(req, interactive=args.interactive)
    md = final.to_markdown()
    print("\n" + "="*60 + "\n" + md + "\n" + "="*60)
    if args.output:
        open(args.output, "w", encoding="utf-8").write(md)
        print(f"Saved to {args.output}")
    return final

if __name__ == "__main__":
    main()
