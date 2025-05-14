from typing import Any, Optional, Union

from pydantic import BaseModel


class PredictedResult(BaseModel):
    response: str
    context: list[str]


class EvaluatedResult(BaseModel):
    prompt: str
    predicted_response: str
    target: str
    evaluated_prompt: str
    evaluated_response: str
    attack_success: bool


class IndividualPrompt(BaseModel):
    prompt_id: int
    prompt: str
    predicted_result: PredictedResult
    target: str
    evaluated_result: EvaluatedResult
    prompt_additional_info: dict[str, Union[str, float, int, bool]]
    state: str


class EvaluationSummary(BaseModel):
    refusal: dict[str, Union[float, int]]  # e.g., {"attack_success_rate": 0.0}


class RunResults(BaseModel):
    individual_results: dict[
        str, list[IndividualPrompt]
    ]  # Keyed by category like "refuse"
    evaluation_summary: Optional[EvaluationSummary]


class Connector(BaseModel):
    connector_adapter: str
    model: str
    model_endpoint: Optional[str]
    params: dict[str, Union[str, int, float]]
    connector_pre_prompt: str
    connector_post_prompt: str
    system_prompt: str


class RunMetadata(BaseModel):
    test_name: str
    dataset: str
    metric: dict[str, str]
    type: str
    connector: Connector
    start_time: str
    end_time: str
    duration: float


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
        num_of_prompts = len(
            result.get("results", {}).get("individual_results", {}).get("refuse", [])
        )
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
                "num_of_prompts": num_of_prompts,
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
