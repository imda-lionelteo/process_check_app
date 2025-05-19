from typing import Any, Optional, Union

from pydantic import BaseModel


class IndividualResult(BaseModel):
    prompt_id: int
    prompt: str
    predicted_result: dict
    target: str
    evaluated_result: dict
    prompt_additional_info: dict
    state: str


class RunResults(BaseModel):
    individual_results: dict[str, list[IndividualResult]]
    evaluation_summary: dict


class RunMetadata(BaseModel):
    test_name: str
    dataset: Optional[str] = None
    metric: dict
    type: str
    connector: dict
    start_time: str
    end_time: str
    duration: float
    attack_module: Optional[dict] = None


class RunResultEntry(BaseModel):
    metadata: RunMetadata
    results: RunResults


class RunMetaData(BaseModel):
    run_id: str
    test_id: str
    start_time: str
    end_time: str
    duration: float


class Schema1(BaseModel):
    run_metadata: RunMetaData
    run_results: list[RunResultEntry]


def extract_v1_report_info(
    data: dict[str, Any],
) -> dict[str, Union[str, int, list[dict[str, Any]]]]:
    """
    Extracts report information from a Moonshot v1 Result Structure.

    This function processes the provided data to extract the status,
    count of successful, failed, and skipped tests, and gathers evaluation
    summaries and metadata for each test run.

    Args:
        data (dict[str, Any]): The data containing run results and metadata.

    Returns:
        dict[str, Union[str, int, list[dict[str, Any]]]]: A dictionary containing:
            - 'status': The status of the report, either 'completed' or 'incomplete'.
            - 'total_tests': A dictionary with counts of successful, failed, and skipped tests.
            - 'evaluation_summaries_and_metadata': A list of evaluation summaries with metadata.
    """
    # Initialize test counts
    test_success = 0
    test_fail = 0
    test_skip = 0  # Default to 0 as instructed

    # Determine the total number of tests
    total_tests = len(data.get("run_results", []))
    status = "completed" if total_tests > 0 else "incomplete"

    evaluation_summaries_and_metadata = []
    for result in data.get("run_results", []):
        meta_data = result.get("metadata", {})
        test_name = meta_data.get("test_name", "Unnamed Test")
        model_id = meta_data.get("connector", {}).get("model", "Unknown Model")
        summary = result.get("results", {}).get("evaluation_summary", {})
        if summary:
            test_success += 1
        else:
            test_fail += 1
        evaluation_summaries_and_metadata.append(
            {
                "test_name": test_name,
                "id": test_name,
                "model_id": model_id,
                "summary": summary,
            }
        )

    return {
        "status": status,
        "total_tests": {
            "test_success": test_success,
            "test_fail": test_fail,
            "test_skip": test_skip,
        },
        "evaluation_summaries_and_metadata": evaluation_summaries_and_metadata,
    }
