from src.core.models import Claim
from src.agents.fact_checker import FactCheckerAgent
def test_supported():
    c = FactCheckerAgent().check(Claim(text="Intermittent fasting may help with weight loss", evidence="Studies suggest intermittent fasting may help with weight loss by reducing calorie intake"))
    assert c.verdict=="SUPPORTED"
def test_unsupported():
    c = FactCheckerAgent().check(Claim(text="Fasting cures all diseases", evidence="No matching document paragraph."))
    assert c.verdict in ("UNSUPPORTED","CONTRADICTED")
