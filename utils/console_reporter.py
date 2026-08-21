def print_test_header(test_name: str) -> None:
    print(f"\n{'=' * 72}\n TEST: {test_name}\n{'=' * 72}", flush=True)


def print_test_step(step_number: int, description: str) -> None:
    print(f"[STEP {step_number}] {description}", flush=True)


def mask_secret(value: str) -> str:
    return "*" * 8 if value else "(empty)"


def print_test_result(test_name: str, passed: bool) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"[RESULT] {status}: {test_name}\n{'=' * 72}", flush=True)