import logging
from support_system.workflow import CustomerSupportWorkflow, collect_case, configure_logging


def print_report(report):
    print("\\n" + "=" * 60)
    print("CUSTOMER SUPPORT CASE SUMMARY")
    print("=" * 60)
    print(f"Category: {report.classification.category} ({report.classification.confidence} confidence)")
    print(f"Priority: {report.priority.level.upper()} | Score: {report.priority.score}")
    print(f"Reason: {report.priority.reason}")
    print("\\nSUGGESTED RESOLUTION")
    print(report.resolution.summary)
    for number, step in enumerate(report.resolution.steps, 1):
        print(f"{number}. {step}")
    print("\\nESCALATION DECISION")
    print(f"Required: {'YES' if report.escalation.required else 'NO'}")
    print(f"Queue: {report.escalation.handoff_queue}")
    print(f"Reason: {report.escalation.reason}")
    print("\\nSaved report: support_case_report.json")
    print("Activity log: log.txt")
    if report.escalation.required:
        print("A human handoff is recommended. This demo does not contact an agent automatically.")


def main():
    configure_logging()
    try:
        case = collect_case()
        if not case.issue:
            print("Issue description cannot be empty.")
            return
        report = CustomerSupportWorkflow().run(case)
        print_report(report)
        CustomerSupportWorkflow.save_report(report)
    except (KeyboardInterrupt, EOFError):
        print("\\nSupport intake cancelled.")
        logging.warning("Support intake cancelled")
    except Exception:
        logging.exception("Unexpected support workflow error")
        raise


if __name__ == "__main__":
    main()
