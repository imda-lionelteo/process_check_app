from typing import Any, Optional, Union

from pydantic import BaseModel


class RecipeDetail(BaseModel):
    model_id: str
    dataset_id: str
    prompt_template_id: str
    data: list[dict]
    metrics: list[dict]


class Recipe(BaseModel):
    id: str
    details: list[RecipeDetail]


class EvaluationSummary(BaseModel):
    model_id: str
    num_of_prompts: int
    avg_grade_value: float
    grade: str


class Cookbook(BaseModel):
    id: str
    recipes: list[Recipe]
    overall_evaluation_summary: list[dict]


class OverallEvaluationSummary(BaseModel):
    model_id: str
    overall_grade: str


class Results(BaseModel):
    cookbooks: list[Cookbook]
    grading_scale: dict
    overall_evaluation_summary: list[OverallEvaluationSummary]
    total_num_of_prompts: int


class MetaData(BaseModel):
    id: Optional[str] = None
    status: str
    cookbooks: list[str]
    endpoints: list[str]


class Schema2(BaseModel):
    metadata: MetaData
    results: dict[str, list[Cookbook]]


def extract_06_report_info(
    report_json: dict[str, Any],
) -> dict[str, Union[int, str, list[dict[str, Any]]]]:
    """
    Extracts report information from Moonshot v0.6 Result structure.

    This function processes the provided report JSON to extract the status,
    count of successful, failed, and skipped tests, and gathers unique evaluation
    summaries for each recipe in the cookbooks.

    Args:
        report_json (dict[str, Any]): The JSON data containing report information.

    Returns:
        dict[str, Union[int, str, list[dict[str, Any]]]]: A dictionary containing:
            - 'status': The status of the report.
            - 'total_tests': A dictionary with counts of successful, failed, and skipped tests.
            - 'evaluation_summaries_and_metadata': A list of evaluation summaries with metadata.
    """
    # Extract status from metadata
    status = report_json.get("metadata", {}).get("status", "Unknown")

    # Initialize test counts
    test_success = 0
    test_fail = 0
    test_skip = 0  # Default to 0 as instructed

    cookbooks = report_json.get("results", {}).get("cookbooks", [])
    # Gather unique evaluation summaries (optional field)
    evaluation_summaries = []
    seen_test_names = set()

    for cookbook in cookbooks:
        recipes = cookbook.get("recipes", [])
        for recipe in recipes:
            test_name = recipe.get("id", "Unnamed Recipe")
            if test_name in seen_test_names:
                continue  # Skip if we've already processed this test name

            summaries = recipe.get("evaluation_summary")
            if summaries:
                test_success += 1
                summary = summaries[
                    0
                ]  # Assuming you want the first summary for each test
                summary_with_id = {
                    "test_name": test_name,
                    "id": recipe.get("id"),
                    "summary": {
                        "avg_grade_value": round(
                            summary.get("avg_grade_value", 0.0), 2
                        ),
                        "grade": summary.get("grade", "N/A"),
                    },
                }
                evaluation_summaries.append(summary_with_id)
                seen_test_names.add(test_name)  # Mark this test name as seen
            else:
                test_fail += 1

    return {
        "status": status,
        "total_tests": {
            "test_success": test_success,
            "test_fail": test_fail,
            "test_skip": test_skip,
        },
        "evaluation_summaries_and_metadata": evaluation_summaries,
    }
