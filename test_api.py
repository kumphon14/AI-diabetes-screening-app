import json
from pathlib import Path
from typing import Any, Optional

import requests

API_URL = "http://127.0.0.1:8000/predict"
HEALTH_URL = "http://127.0.0.1:8000/health"
TEST_CASES_FILE = "test_cases.json"
TIMEOUT_SECONDS = 30


def load_test_cases(file_path: str) -> list[dict[str, Any]]:
    """
    รองรับ test_cases.json รูปแบบ:
    {
      "clear_positive_cases": [...],
      "clear_negative_cases": [...],
      "borderline_cases": [...],
      "edge_and_special_cases": [...]
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
            "test_cases.json must contain a JSON object with grouped case lists."
        )

    group_mapping = {
        "clear_positive_cases": {
            "expected_group": "positive",
            "evaluation_mode": "strict",
            "display_group": "clear_positive_cases",
        },
        "clear_negative_cases": {
            "expected_group": "negative",
            "evaluation_mode": "strict",
            "display_group": "clear_negative_cases",
        },
        "borderline_cases": {
            "expected_group": "borderline",
            "evaluation_mode": "observe",
            "display_group": "borderline_cases",
        },
        "edge_and_special_cases": {
            "expected_group": "special",
            "evaluation_mode": "observe",
            "display_group": "edge_and_special_cases",
        },
    }

    merged_cases: list[dict[str, Any]] = []

    for group_name, meta in group_mapping.items():
        cases = data.get(group_name, [])
        if not isinstance(cases, list):
            raise ValueError(f"'{group_name}' must be a list.")

        for case in cases:
            if not isinstance(case, dict):
                continue

            case_copy = case.copy()
            case_copy["_expected_group"] = meta["expected_group"]
            case_copy["_evaluation_mode"] = meta["evaluation_mode"]
            case_copy["_display_group"] = meta["display_group"]
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
    ลบ field ที่ใช้เพื่อ test ออกก่อนยิง API
    """
    excluded_keys = {
        "case_id",
        "_expected_group",
        "_evaluation_mode",
        "_display_group",
    }
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


def detect_actual_group(response_data: dict[str, Any]) -> str | None:
    predicted_class = response_data.get("predicted_class")
    prediction_code = str(response_data.get("prediction_code", "")).lower()
    screening_result = str(response_data.get("screening_result", "")).lower()
    prediction_label = str(response_data.get("prediction_label", "")).lower()

    if predicted_class == 1 or prediction_code == "positive":
        return "positive"
    if predicted_class == 0 or prediction_code == "negative":
        return "negative"

    if "likely diabetes" in screening_result or "likely diabetes" in prediction_label:
        return "positive"
    if "unlikely diabetes" in screening_result or "unlikely diabetes" in prediction_label:
        return "negative"

    return None


def to_screening_label(group: str | None) -> str:
    if group == "positive":
        return "Likely Diabetes"
    if group == "negative":
        return "Unlikely Diabetes"
    return "Unknown"


def extract_probability(response_data: dict[str, Any]) -> Optional[float]:
    """
    รองรับหลายชื่อ field เผื่อ API ส่ง probability กลับมาคนละ key
    """
    candidate_keys = [
        "probability",
        "risk_probability",
        "positive_class_probability",
        "diabetes_probability",
        "prediction_probability",
        "score",
    ]

    for key in candidate_keys:
        value = response_data.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue

    return None


def evaluate_prediction(
    expected_group: str,
    response_data: dict[str, Any],
    evaluation_mode: str,
) -> dict[str, Any]:
    """
    strict:
      - positive ต้องได้ positive
      - negative ต้องได้ negative

    observe:
      - borderline / special จะไม่ตัดสิน fail ตรง ๆ
      - ใช้เพื่อดูผลลัพธ์และความสมเหตุสมผลของ explanation
    """
    actual_group = detect_actual_group(response_data)

    if evaluation_mode == "strict":
        passed = actual_group == expected_group
    else:
        passed = True

    return {
        "expected_group": expected_group,
        "actual_group": actual_group,
        "passed": passed,
        "evaluation_mode": evaluation_mode,
    }


def print_result(
    result: dict[str, Any],
    expected_group: str,
    evaluation_mode: str,
    display_group: str,
) -> dict[str, Any]:
    case_name = result["case_name"]
    status_code = result["status_code"]
    response = result["response"]

    print("\n" + "=" * 100)
    print(f"CASE ID              : {case_name}")
    print(f"CASE GROUP           : {display_group}")
    print(f"EXPECTED GROUP       : {expected_group}")
    print(f"EXPECTED SCREENING   : {to_screening_label(expected_group)}")
    print(f"EVALUATION MODE      : {evaluation_mode}")
    print(f"HTTP STATUS          : {status_code}")

    if status_code != 200:
        print("RESULT               : FAILED (HTTP ERROR)")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return {
            "case_name": case_name,
            "display_group": display_group,
            "expected_group": expected_group,
            "expected_screening_label": to_screening_label(expected_group),
            "actual_group": None,
            "actual_screening_label": "Unknown",
            "passed": False,
            "status_code": status_code,
            "evaluation_mode": evaluation_mode,
            "threshold": None,
            "probability": None,
        }

    data = response.get("data", {})
    evaluation = evaluate_prediction(expected_group, data, evaluation_mode)

    threshold = data.get("threshold")
    probability = extract_probability(data)
    actual_screening_label = to_screening_label(evaluation["actual_group"])

    if evaluation_mode == "strict":
        print(f"TEST PASSED          : {evaluation['passed']}")
    else:
        print("TEST PASSED          : OBSERVE ONLY")

    print(f"ACTUAL GROUP         : {evaluation['actual_group']}")
    print(f"SCREENING RESULT     : {actual_screening_label}")
    print(f"THRESHOLD USED       : {threshold}")

    if probability is not None:
        print(f"PREDICTED PROBABILITY: {probability:.4f}")
    else:
        print("PREDICTED PROBABILITY: N/A")

    print("\n--- Prediction Output ---")
    print(f"prediction_code      : {data.get('prediction_code')}")
    print(f"prediction_label     : {data.get('prediction_label')}")
    print(f"screening_result     : {data.get('screening_result')}")
    print(f"predicted_class      : {data.get('predicted_class')}")

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
        "display_group": display_group,
        "expected_group": expected_group,
        "expected_screening_label": to_screening_label(expected_group),
        "actual_group": evaluation["actual_group"],
        "actual_screening_label": actual_screening_label,
        "passed": evaluation["passed"],
        "status_code": status_code,
        "evaluation_mode": evaluation_mode,
        "threshold": threshold,
        "probability": probability,
    }


def print_screening_confusion(strict_results: list[dict[str, Any]]) -> None:
    tp = sum(
        1 for r in strict_results
        if r["expected_group"] == "positive" and r["actual_group"] == "positive"
    )
    tn = sum(
        1 for r in strict_results
        if r["expected_group"] == "negative" and r["actual_group"] == "negative"
    )
    fp = sum(
        1 for r in strict_results
        if r["expected_group"] == "negative" and r["actual_group"] == "positive"
    )
    fn = sum(
        1 for r in strict_results
        if r["expected_group"] == "positive" and r["actual_group"] == "negative"
    )

    total = len(strict_results)
    correct = tp + tn
    incorrect = fp + fn
    accuracy = (correct / total * 100) if total > 0 else 0.0

    print("\nScreening Confusion Summary:")
    print(f" - True Positive  (Likely Diabetes predicted correctly)   : {tp}")
    print(f" - True Negative  (Unlikely Diabetes predicted correctly) : {tn}")
    print(f" - False Positive (Predicted Likely but actually negative): {fp}")
    print(f" - False Negative (Predicted Unlikely but actually positive): {fn}")

    print("\nScreening Performance:")
    print(f" - Correct predictions   : {correct}")
    print(f" - Incorrect predictions : {incorrect}")
    print(f" - Accuracy              : {accuracy:.2f}%")

    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    specificity = (tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    print("\nAdditional Metrics for Research Analysis:")
    print(f" - Precision   : {precision:.4f}")
    print(f" - Recall      : {recall:.4f}")
    print(f" - Specificity : {specificity:.4f}")
    print(f" - F1-score    : {f1:.4f}")


def print_threshold_summary(all_results: list[dict[str, Any]]) -> None:
    thresholds = [r["threshold"] for r in all_results if r["threshold"] is not None]

    print("\nThreshold Summary:")
    if not thresholds:
        print(" - No threshold returned by API")
        return

    unique_thresholds = sorted(set(thresholds))
    print(f" - Threshold values found : {unique_thresholds}")

    if len(unique_thresholds) == 1:
        print(f" - Operational threshold  : {unique_thresholds[0]}")
    else:
        print(" - Note: multiple threshold values were returned across cases")


def print_probability_summary(all_results: list[dict[str, Any]]) -> None:
    probability_results = [r for r in all_results if r["probability"] is not None]

    print("\nProbability Summary:")
    if not probability_results:
        print(" - Probability was not returned by API")
        return

    probs = [r["probability"] for r in probability_results]
    avg_prob = sum(probs) / len(probs)
    min_prob = min(probs)
    max_prob = max(probs)

    positive_probs = [r["probability"] for r in probability_results if r["actual_group"] == "positive"]
    negative_probs = [r["probability"] for r in probability_results if r["actual_group"] == "negative"]

    print(f" - Cases with probability output : {len(probability_results)}")
    print(f" - Average probability           : {avg_prob:.4f}")
    print(f" - Min probability               : {min_prob:.4f}")
    print(f" - Max probability               : {max_prob:.4f}")

    if positive_probs:
        print(f" - Avg probability (Likely Diabetes)   : {sum(positive_probs)/len(positive_probs):.4f}")
    if negative_probs:
        print(f" - Avg probability (Unlikely Diabetes) : {sum(negative_probs)/len(negative_probs):.4f}")


def print_case_level_screening_summary(all_results: list[dict[str, Any]]) -> None:
    print("\nCase-level Screening Summary:")
    for r in all_results:
        print(
            f" - {r['case_name']}: "
            f"expected={r['expected_screening_label']}, "
            f"predicted={r['actual_screening_label']}, "
            f"threshold={r['threshold']}, "
            f"passed={r['passed']}"
        )


def print_summary(all_results: list[dict[str, Any]]) -> None:
    print("\n" + "=" * 100)
    print("FINAL SUMMARY")

    total_cases = len(all_results)
    http_success_count = sum(1 for r in all_results if r["status_code"] == 200)
    http_fail_count = total_cases - http_success_count

    strict_results = [r for r in all_results if r["evaluation_mode"] == "strict"]
    observe_results = [r for r in all_results if r["evaluation_mode"] == "observe"]

    strict_passed = sum(1 for r in strict_results if r["passed"])
    strict_failed = len(strict_results) - strict_passed

    print(f"Total cases              : {total_cases}")
    print(f"HTTP success             : {http_success_count}")
    print(f"HTTP failed              : {http_fail_count}")
    print(f"Strict evaluation cases  : {len(strict_results)}")
    print(f"Strict passed            : {strict_passed}")
    print(f"Strict failed            : {strict_failed}")
    print(f"Observe-only cases       : {len(observe_results)}")

    group_names = [
        "clear_positive_cases",
        "clear_negative_cases",
        "borderline_cases",
        "edge_and_special_cases",
    ]

    print("\nGroup Breakdown:")
    for group_name in group_names:
        group_cases = [r for r in all_results if r["display_group"] == group_name]
        if not group_cases:
            print(f" - {group_name}: 0")
            continue

        if group_name in {"clear_positive_cases", "clear_negative_cases"}:
            passed = sum(1 for r in group_cases if r["passed"])
            print(f" - {group_name}: {passed}/{len(group_cases)} passed")
        else:
            print(f" - {group_name}: {len(group_cases)} observed")

    failed_cases = [r for r in strict_results if not r["passed"]]

    print("\nStrict Failed Cases:")
    if not failed_cases:
        print(" - None")
    else:
        for item in failed_cases:
            print(
                f" - {item['case_name']} | "
                f"expected={item['expected_screening_label']} | "
                f"predicted={item['actual_screening_label']} | "
                f"http={item['status_code']}"
            )

    print_case_level_screening_summary(all_results)
    print_screening_confusion(strict_results)
    print_threshold_summary(all_results)
    print_probability_summary(all_results)


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
        evaluation_mode = str(case.get("_evaluation_mode", "strict")).lower()
        display_group = str(case.get("_display_group", "unknown_group"))
        payload = build_payload(case)

        if not isinstance(payload, dict):
            print(f"Skipping invalid case: {case_name} (payload is not a dict)")
            continue

        try:
            result = post_case(case_name, payload)
            final_result = print_result(
                result=result,
                expected_group=expected_group,
                evaluation_mode=evaluation_mode,
                display_group=display_group,
            )
            all_results.append(final_result)

        except requests.RequestException as e:
            print("\n" + "=" * 100)
            print(f"CASE ID              : {case_name}")
            print(f"CASE GROUP           : {display_group}")
            print(f"EXPECTED GROUP       : {expected_group}")
            print(f"EXPECTED SCREENING   : {to_screening_label(expected_group)}")
            print(f"EVALUATION MODE      : {evaluation_mode}")
            print("RESULT               : REQUEST FAILED")
            print(f"Error                : {e}")

            all_results.append({
                "case_name": case_name,
                "display_group": display_group,
                "expected_group": expected_group,
                "expected_screening_label": to_screening_label(expected_group),
                "actual_group": None,
                "actual_screening_label": "Unknown",
                "passed": False if evaluation_mode == "strict" else True,
                "status_code": 0,
                "evaluation_mode": evaluation_mode,
                "threshold": None,
                "probability": None,
            })

    print_summary(all_results)


if __name__ == "__main__":
    main()