# QA: TASK-001

## Attempt 1

## Checks from the acceptance criteria

| Criterion | My test (in `tests/test_qa_task001.py`) | Result | Evidence |
|---|---|---|---|
| AC1 | `test_ac1_registration_assigns_caller_and_handles_description` | PASS | `POST /repositories` returned 201, assigned the caller, preserved a supplied description, and defaulted an omitted description to an empty string. |
| AC2 | `test_ac2_owner_can_list_and_read_immediate_analysis_but_other_user_cannot` | PASS | The new repository appeared in its owner's list and detail, its analysis was immediately available, and another user received 403 for detail and analysis. |
| AC3 | `test_ac3_wrong_inputs_return_400_without_creating_repository` | PASS | Non-object, missing, blank, wrongly typed, and malformed JSON inputs returned 400; repository state and `next_id` were unchanged. |
| AC4 | `test_ac4_unknown_caller_returns_401_without_creating_repository` | PASS | An unknown caller received 401; repository state and `next_id` were unchanged. |
| AC5 | `test_ac5_analysis_failure_returns_500_and_rolls_back_registration` | PASS | A simulated analyzer exception returned 500 and left repositories, analyses, and `next_id` unchanged. |

## Other checks

- Wrong input: AC3 covers malformed JSON plus invalid body and field forms.
- Regression: `test_regression_existing_list_and_analysis_still_work` confirms the existing repository list and seeded analysis remain available.
- Full-suite evidence: `python -m unittest` ran 38 tests in 1.098s and printed `OK` (exit code 0). The traceback in the output is expected evidence from the simulated AC5 analyzer failure, which the API converted to a 500 response.

## Verdict

PASSED

## Failure type

Not applicable.
