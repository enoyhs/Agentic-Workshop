# TASK-001 architecture

## Approach

- Add a thin `POST /repositories` handler in `app/server.py`. Pass the parsed body and caller to a registration function in `app/service.py`.
- Reuse `require_user()` and validate the body before changing the store. Set `owner` from the caller, take the ID from `Store.next_id`, and use one `now_utc()` value for registration and the initial scan.
- Run `analyzer.analyze()` synchronously before writing to the store. On success, save the repository and analysis under the same ID, then advance `next_id`. If analysis raises, the repository, analysis, and ID counter remain as they were.

## Parts that change

- Add the route in `app/server.py` and the registration logic in `app/service.py`. Cover the new behavior in `tests/test_api.py` and use a service test to exercise analyzer failure.

## Interface

- Accept a JSON object with nonblank string `name` and `url` and an optional string `description` that defaults to `""`.
- Return `201` with the existing repository detail shape. The owner can immediately see it in `GET /repositories` and fetch its detail and analysis. Existing owner checks apply to both reads.
- Return `400` for invalid payloads and `401` for an unknown caller. The existing `500` response handles analyzer failures.

## Risks and limits

- The current analyzer derives results locally from the URL. The in-memory store resets on restart.
- The [approved requirements](requirements.md) cover S1-A registration and immediate analysis. The Product Owner deferred the duplicate-URL follow-up.
