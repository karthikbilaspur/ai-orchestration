
from ..core.models import Fix, ParsedError, Classification, Review

class ReviewerAgent:
    """Validation agent — never trusts Solution Agent blindly."""
    def run(self, parsed: ParsedError, cls: Classification, fix: Fix) -> Review:
        checks=[]
        # 1. Does diff mention the failing file / package / line?
        mentions = bool(parsed.file and parsed.file.split("/")[-1] in fix.diff) or bool(parsed.exception_type and parsed.exception_type.lower() in fix.explanation.lower()) or len(fix.diff)>20
        # 2. Is it minimal? (not a huge refactor)
        minimal = len(fix.diff) < 2000
        # 3. Has verification?
        has_verify = len(fix.verification)>0
        if mentions and minimal and has_verify:
            return Review(verdict="APPROVED", addresses_root_cause=True, is_minimal=True, is_safe=True, feedback="Fix addresses the reported error, is minimal, and includes verification steps.")
        fb=[]
        if not mentions: fb.append("Fix does not reference the failing location / error.")
        if not minimal: fb.append("Fix is too broad — narrow it to the failing line.")
        if not has_verify: fb.append("Add verification steps.")
        return Review(verdict="NEEDS_REVISION", addresses_root_cause=mentions, is_minimal=minimal, is_safe=True, feedback="; ".join(fb), suggested_change="Tighten the diff to the exact failing line and add a reproduction test.")
