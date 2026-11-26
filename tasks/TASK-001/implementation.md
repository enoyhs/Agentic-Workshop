# Implementation: TASK-001

## What I built

Real implementation of `POST /repositories` (S1-A registration with immediate analysis), following `architecture.md`.

- `service.register_repository()` checks the caller (`401`), then validates the body (`400`): it must be a JSON object with nonblank string `name` and `url`, and an optional string `description` that defaults to `""`.
- It builds the repository with `store.next_id` and one `now_utc()` value for `registered_at`, `last_scanned_at` and the analysis `scanned_at`. It runs `analyzer.analyze()` **before** writing anything, then saves the repository and analysis and advances `next_id`.
- If the analyzer raises, nothing is saved and `next_id` is unchanged. The existing `500` handler returns the error.
- The route returns `201` with the same fields as `GET /repositories/{id}`. Owner checks for list, detail and analysis are unchanged, so other users get `403`.

## Files changed

- `app/service.py`: added `register_repository()` and the `_required_text()` helper.
- `app/server.py`: added the `POST /repositories` route.
- `tests/test_api.py`: tests for AC1–AC4 (success, description default, list/detail/analysis visibility, other user blocked, invalid bodies, malformed JSON, unknown user).
- `tests/test_service.py`: tests for AC5 (analyzer failure leaves the store untouched) and ID assignment.

## Tests

`python -m unittest`: 32 tests ran, all OK.

## Known limits

- No duplicate-URL check (`409`). The Product Owner put it out of scope.
- No URL format check. Any nonblank string is accepted, because no decision has been made on Git-host URLs.
- The analyzer is still the pretend, URL-derived one. Data is in memory and resets on restart.
- I didn't update `docs/api.md`. The new endpoint isn't listed there yet.

## Attempts

- Attempt 1: first implementation of S1-A registration per the design.
