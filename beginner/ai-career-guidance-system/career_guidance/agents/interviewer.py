from career_guidance.models import LearnerProfile


class InterviewerAgent:
    """Collects and validates the learner's six required inputs."""

    INTEREST_OPTIONS = {"ai", "software development", "data science", "cybersecurity"}
    TARGET_OPTIONS = {"internship", "job", "freelancing", "research"}
    PREFERENCE_OPTIONS = {"theoretical", "hands-on projects", "balanced"}

    def __init__(self, input_fn=input, output_fn=print):
        self.input = input_fn
        self.output = output_fn

    def _ask_nonempty(self, prompt: str) -> str:
        while True:
            value = self.input(prompt).strip()
            if value:
                return value
            self.output("Please enter a value.")

    def _ask_choice(self, prompt: str, choices: set[str]) -> str:
        allowed = ", ".join(sorted(choices))
        while True:
            value = self._ask_nonempty(f"{prompt} ({allowed}): ").lower()
            if value in choices:
                return value
            self.output(f"Choose one of: {allowed}.")

    def _ask_hours(self) -> float:
        while True:
            raw = self._ask_nonempty("How many hours can you learn daily? ")
            try:
                hours = float(raw)
                if 0.25 <= hours <= 16:
                    return hours
            except ValueError:
                pass
            self.output("Enter a number between 0.25 and 16.")

    def collect(self) -> LearnerProfile:
        self.output("\n=== AI Career Guidance Interview ===")
        education = self._ask_nonempty("1. Current educational background: ")
        raw_languages = self._ask_nonempty(
            "2. Programming languages you know (comma-separated; type 'none' if none): "
        )
        languages = [] if raw_languages.lower() == "none" else [
            x.strip().lower() for x in raw_languages.split(",") if x.strip()
        ]
        raw_interests = self._ask_nonempty(
            "3. Areas of interest (comma-separated: AI, software development, "
            "data science, cybersecurity): "
        )
        interests = [x.strip().lower() for x in raw_interests.split(",") if x.strip()]
        valid = self.INTEREST_OPTIONS
        while not interests or any(x not in valid for x in interests):
            self.output("Use one or more of: " + ", ".join(sorted(valid)))
            raw_interests = self._ask_nonempty("Enter your interests again: ")
            interests = [x.strip().lower() for x in raw_interests.split(",") if x.strip()]
        daily_hours = self._ask_hours()
        preference = self._ask_choice("5. Learning preference", self.PREFERENCE_OPTIONS)
        target = self._ask_choice("6. Target", self.TARGET_OPTIONS)
        return LearnerProfile(
            education=education,
            languages=languages,
            interests=interests,
            daily_hours=daily_hours,
            learning_preference=preference,
            target=target,
        )
