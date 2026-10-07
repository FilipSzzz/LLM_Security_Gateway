import json
import logging

from app.core.logging_config import request_id_var, setup_logging


def test_json_logs_carry_request_id(capsys):
    setup_logging("INFO", json_logs=True)
    request_id_var.set("abc123")
    logging.getLogger("t").info("hello")
    entry = json.loads(capsys.readouterr().out.strip())
    assert entry["message"] == "hello"
    assert entry["request_id"] == "abc123"
