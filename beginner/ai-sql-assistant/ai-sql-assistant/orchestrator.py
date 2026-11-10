"""Orchestrator: chains all 5 agents + logging."""
import logging, pathlib
from agents.query_understanding import parse_question
from agents.sql_generator import generate_sql
from agents.sql_validator import validate_sql, ValidationError
from agents.database_agent import execute_readonly
from agents.explanation_agent import explain

logging.basicConfig(filename="logs/run.log", level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

def run(question: str) -> dict:
    logger.info(f"QUESTION: {question}")
    intent = parse_question(question)
    logger.info(f"INTENT: {intent}")
    sql, params = generate_sql(intent)
    logger.info(f"SQL: {sql} | PARAMS: {params}")
    try:
        validate_sql(sql, params)
    except ValidationError as e:
        logger.error(f"VALIDATION FAILED: {e}")
        return {"question": question, "sql": sql, "error": str(e), "explanation": f"Blocked unsafe query: {e}"}
    result = execute_readonly(sql, params)
    logger.info(f"ROWS: {result['row_count']}")
    explanation = explain(question, sql, result)
    return {"question": question, "intent": intent.intent_type, "sql": sql, "params": params, "result": result, "explanation": explanation}
