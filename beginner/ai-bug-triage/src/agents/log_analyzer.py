
import re
from ..core.models import ParsedError, StackFrame

EXC_RE = re.compile(r"(?P<type>[A-Z][A-Za-z0-9_.]*?(?:Error|Exception|Error|Warning|Failed|NotFound|Timeout))[:\s]+(?P<msg>.+)", re.M)
FILE_RE = re.compile(r"""File\s+"(?P<file>[^"]+)",\s+line\s+(?P<line>\d+)(?:,\s+in\s+(?P<func>\S+))?""")
JS_RE = re.compile(r"at\s+(?P<func>[^\s]+)\s+\((?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+)\)")

class LogAnalyzer:
    """Extracts relevant error details — no LLM needed, deterministic."""
    def run(self, raw: str) -> ParsedError:
        raw = raw.strip()
        exc, msg = None, raw.splitlines()[-1] if raw else ""
        m = EXC_RE.search(raw)
        if m:
            exc, msg = m.group("type"), m.group("msg").strip()
        # Python traceback
        frames=[]
        for fm in FILE_RE.finditer(raw):
            frames.append(StackFrame(file=fm.group("file"), line=int(fm.group("line")), function=fm.group("func")))
        for jm in JS_RE.finditer(raw):
            frames.append(StackFrame(file=jm.group("file"), line=int(jm.group("line")), function=jm.group("func")))
        file = frames[0].file if frames else None
        line = frames[0].line if frames else None
        lang = "python" if "Traceback" in raw or "File \"" in raw else "javascript" if " at " in raw and ".js" in raw else "unknown"
        if "ModuleNotFoundError" in raw or "No module named" in raw or "Cannot find module" in raw or "ERR_MODULE_NOT_FOUND" in raw:
            lang = lang
        return ParsedError(raw=raw, exception_type=exc, message=msg, file=file, line=line, frames=frames, language_hint=lang)
