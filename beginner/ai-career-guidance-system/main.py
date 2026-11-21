import json
import logging

from career_guidance.workflow import CareerGuidanceWorkflow, configure_logging


def print_report(report):
    print("\n" + "=" * 62)
    print("YOUR AI CAREER GUIDANCE REPORT")
    print("=" * 62)
    print("\nSKILL GAP ANALYSIS")
    print(report.skill_analysis.summary)
    print("\nStrengths:")
    for item in report.skill_analysis.strengths:
        print(f"  - {item}")
    print("\nSkills to develop:")
    for item in report.skill_analysis.skill_gaps:
        print(f"  - {item}")
    print("\nCAREER RECOMMENDATIONS")
    for index, match in enumerate(report.career_recommendations, 1):
        print(f"\n{index}. {match.career} — match score: {match.score}/100")
        for reason in match.rationale:
            print(f"   • {reason}")
    print("\n30-DAY LEARNING ROADMAP")
    for item in report.roadmap:
        print(f"\n{item['period']}: {item['focus']}")
        print(f"  Task: {item['task']}")
        print(f"  Activity: {item['activity']}")
        print(f"  Suggested time: {item['hours_per_day']} hour(s)/day")
    print("\nReport saved to career_report.json; activity logged in log.txt.")


def main():
    configure_logging()
    try:
        workflow = CareerGuidanceWorkflow()
        report = workflow.run()
        print_report(report)
        workflow.save_report(report)
    except (KeyboardInterrupt, EOFError):
        print("\nInterview cancelled.")
        logging.warning("Interview cancelled by user")
    except Exception:
        logging.exception("Unexpected application error")
        raise


if __name__ == "__main__":
    main()
