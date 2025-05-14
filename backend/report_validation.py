import json
from typing import Any, Dict

from backend.schema.ms_v1_schema import Schema1, extract_v1_report_info
from backend.schema.ms_v06_schema import Schema2, extract_06_report_info
from pydantic import ValidationError


# Validation function
def validate_json(data: Dict[str, Any]) -> bool:
    try:
        # Try to validate against Schema 1
        Schema1(**data)
        return True
    except ValidationError:
        try:
            # Try to validate against Schema 2
            Schema2(**data)
            return True
        except ValidationError:
            # If both validations fail, return False
            return False


def get_report_info(filepath: str) -> Dict[str, Any]:
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
        # Try to validate against Schema 1
        Schema1(**data)
        return extract_v1_report_info(data)
    except ValidationError:
        try:
            # Try to validate against Schema 2
            Schema2(**data)
            return extract_06_report_info(data)
        except ValidationError:
            # If both validations fail, raise an error
            raise ValueError("Data does not match any known schema.")
    except FileNotFoundError:
        return {}
