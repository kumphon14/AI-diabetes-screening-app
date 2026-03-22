import json
from pathlib import Path
from typing import Any

import requests

API_URL = "http://127.0.0.1:8000/predict"
HEALTH_URL = "http://127.0.0.1:8000/health"
TEST_CASES_FILE = "test_cases.json"
TIMEOUT_SECONDS = 30


def load_test_cases(file_path: str) -> list[dict[str, Any]]:
    """
    รองรับ test_cases.json รูปแบบ:
    {
      "positive_cases": [...],
      "negative_cases": [...]
    }

    และแปลงเป็น list เดียวสำหรับ loop ทดสอบ
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Test cases file not found: {path.resolve()}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(
            "test_cases.json must contain a JSON object with "
            "'positive_cases' and 'negative_cases'."
        )

    positive_cases = data.get("positive_cases", [])
    negative_cases = data.get("negative_cases", [])

    if not isinstance(positive_cases, list) or not isinstance(negative_cases, list):
        raise ValueError("'positive_cases' and 'negative_cases' must both be lists.")

    merged_cases: list[dict[str, Any]] = []

    for case in positive_cases:
        if not isinstance(case, dict):
            continue
        case_copy = case.copy()
        case_copy["_expected_group"] = "positive"
        merged_cases.append(case_copy)

    for case in negative_cases:
        if not isinstance(case, dict):
            continue
        case_copy = case.copy()
        case_copy["_expected_group"] = "negative"
        merged_cases.append(case_copy)

    return merged_cases


def check_api_health() -> bool:
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        if response.status_code != 200:
            return False

        response_json = response.json()
        return response_json.get("status") == "ok"

    except requests.RequestException:
        return False
    except ValueError:
        return False


def build_payload(case: dict[str, Any]) -> dict[str, Any]:
    """
    ลบ field ที่ใช้เพื่อ test ออกก่อนยิง API เช่น:
    - case_id
    - _expected_group
    """
    excluded_keys = {"case_id", "_expected_group"}
    return {k: v for k, v in case.items() if k not in excluded_keys}


def post_case(case_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(API_URL, json=payload, timeout=TIMEOUT_SECONDS)

    try:
        response_json = response.json()
    except ValueError:
        response_json = {"raw_text": response.text}

    return {
        "case_name": case_name,
        "status_code": response.status_code,
        "response": response_json,
    }


def evaluate_prediction(
    expected_group: str,
    response_data: dict[str, Any],
) -> dict[str, Any]:
    """
    เทียบผลคาดหวังแบบง่าย:
    - positive -> predicted_class ควรเป็น 1 หรือ prediction_code = positive
    - negative -> predicted_class ควรเป็น 0 หรือ prediction_code = negative
    """
    predicted_class = response_data.get("predicted_class")
    prediction_code = str(response_data.get("prediction_code", "")).lower()

    actual_group = None
    if predicted_class == 1 or prediction_code == "positive":
        actual_group = "positive"
    elif predicted_class == 0 or prediction_code == "negative":
        actual_group = "negative"

    passed = actual_group == expected_group

    return {
        "expected_group": expected_group,
        "actual_group": actual_group,
        "passed": passed,
    }


def print_result(
    result: dict[str, Any],
    expected_group: str,
) -> dict[str, Any]:
    case_name = result["case_name"]
    status_code = result["status_code"]
    response = result["response"]

    print("\n" + "=" * 80)
    print(f"CASE ID        : {case_name}")
    print(f"EXPECTED GROUP : {expected_group}")
    print(f"HTTP STATUS    : {status_code}")

    if status_code != 200:
        print("RESULT         : FAILED (HTTP ERROR)")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return {
            "case_name": case_name,
            "expected_group": expected_group,
            "actual_group": None,
            "passed": False,
            "status_code": status_code,
        }

    data = response.get("data", {})
    evaluation = evaluate_prediction(expected_group, data)

    print(f"TEST PASSED    : {evaluation['passed']}")
    print(f"ACTUAL GROUP   : {evaluation['actual_group']}")
    print("\n--- Prediction Output ---")
    print(f"prediction_code      : {data.get('prediction_code')}")
    print(f"prediction_label     : {data.get('prediction_label')}")
    print(f"screening_result     : {data.get('screening_result')}")
    print(f"predicted_class      : {data.get('predicted_class')}")
    print(f"threshold            : {data.get('threshold')}")

    print("\n--- Short Interpretation ---")
    print(data.get("short_interpretation"))

    print("\n--- Key Risk Factors ---")
    key_risk_factors = data.get("key_risk_factors", [])
    if key_risk_factors:
        for item in key_risk_factors:
            print(f" - {item}")
    else:
        print(" - None")

    print("\n--- Clinical Flags ---")
    clinical_flags = data.get("clinical_flags", [])
    if clinical_flags:
        for item in clinical_flags:
            print(f" - {item}")
    else:
        print(" - None")

    print("\n--- Recommendations ---")
    recommendations = data.get("recommendations", [])
    if recommendations:
        for item in recommendations:
            print(f" - {item}")
    else:
        print(" - None")

    return {
        "case_name": case_name,
        "expected_group": expected_group,
        "actual_group": evaluation["actual_group"],
        "passed": evaluation["passed"],
        "status_code": status_code,
    }


def print_summary(all_results: list[dict[str, Any]]) -> None:
    print("\n" + "=" * 80)
    print("SUMMARY")

    total_cases = len(all_results)
    http_success_count = sum(1 for r in all_results if r["status_code"] == 200)
    http_fail_count = total_cases - http_success_count

    passed_count = sum(1 for r in all_results if r["passed"])
    failed_count = total_cases - passed_count

    positive_total = sum(1 for r in all_results if r["expected_group"] == "positive")
    negative_total = sum(1 for r in all_results if r["expected_group"] == "negative")

    positive_passed = sum(
        1 for r in all_results
        if r["expected_group"] == "positive" and r["passed"]
    )
    negative_passed = sum(
        1 for r in all_results
        if r["expected_group"] == "negative" and r["passed"]
    )

    print(f"Total cases        : {total_cases}")
    print(f"HTTP success       : {http_success_count}")
    print(f"HTTP failed        : {http_fail_count}")
    print(f"Prediction passed  : {passed_count}")
    print(f"Prediction failed  : {failed_count}")
    print(f"Positive cases     : {positive_passed}/{positive_total}")
    print(f"Negative cases     : {negative_passed}/{negative_total}")

    print("\nFailed Cases:")
    failed_cases = [r for r in all_results if not r["passed"]]
    if not failed_cases:
        print(" - None")
    else:
        for item in failed_cases:
            print(
                f" - {item['case_name']} | expected={item['expected_group']} "
                f"| actual={item['actual_group']} | http={item['status_code']}"
            )


def main() -> None:
    print("Checking API health...")

    if not check_api_health():
        print("API is not reachable.")
        print("Please start it first with: uvicorn api:app --reload")
        return

    print("API is healthy.")

    try:
        test_cases = load_test_cases(TEST_CASES_FILE)
    except Exception as e:
        print(f"Failed to load test cases: {e}")
        return

    if not test_cases:
        print("No test cases found.")
        return

    all_results: list[dict[str, Any]] = []

    for case in test_cases:
        case_name = str(case.get("case_id", "UNKNOWN_CASE"))
        expected_group = str(case.get("_expected_group", "unknown")).lower()
        payload = build_payload(case)

        if not isinstance(payload, dict):
            print(f"Skipping invalid case: {case_name} (payload is not a dict)")
            continue

        try:
            result = post_case(case_name, payload)
            final_result = print_result(result, expected_group)
            all_results.append(final_result)
        except requests.RequestException as e:
            print("\n" + "=" * 80)
            print(f"CASE ID        : {case_name}")
            print(f"EXPECTED GROUP : {expected_group}")
            print("RESULT         : REQUEST FAILED")
            print(f"Error          : {e}")

            all_results.append({
                "case_name": case_name,
                "expected_group": expected_group,
                "actual_group": None,
                "passed": False,
                "status_code": 0,
            })

    print_summary(all_results)


if __name__ == "__main__":
    main()