# Shortcut - runs all 3 test files. Run: python test_pipeline.py  OR  python -m pytest tests/
import subprocess, sys
if __name__ == "__main__":
    for f in ["tests/test_pipeline.py","tests/test_classifier_extractor.py","tests/test_validator_summarizer_reader.py"]:
        print(f"\n=== {f} ===")
        subprocess.check_call([sys.executable, f])
    print("\nAll 3 test files passed!")
