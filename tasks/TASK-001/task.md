# TASK-001

<!-- Product Owner: type the wish card from Business below, word for word. Don't add, fix or explain anything; that's what requirements.md is for. Then commit and push. That push starts your team's clock. -->

## Request from Business

_S1-A_
_S1-B_

## S1-A architecture proposal · Register a repository

Add `POST /repositories` to the existing registry. Create the repository and run the workshop’s analyzer synchronously so the caller can retrieve the analysis as soon as registration returns `201`. [S1-A card](../../facilitator/cards/S1-A.md)

### Approach

- Add a thin route in `app/server.py` that passes `req.store`, `req.user`, and `req.body` to a registration function in `app/service.py`. Reuse `require_user()` and set `owner` from the caller identity. [Server](../../app/server.py#L56) · [Service](../../app/service.py#L39)
- Build the repository with `Store.next_id` and use one `now_utc()` value for `registered_at`, `last_scanned_at`, and the analysis timestamp. Run `analyzer.analyze()` before writing to either dictionary, then save both records and advance `next_id`. An analyzer failure leaves the store untouched. The analyzer derives results locally from the URL, and registrations reset with the in-memory store. [Store](../../app/store.py#L57) · [Analyzer](../../app/analyzer.py#L18)

### API contract

| Result | Behavior |
|---|---|
| `201 Created` | Accept a JSON object with nonblank string `name` and `url` and an optional string `description`, defaulting to `""`. Return the same repository fields as `GET /repositories/{id}`. The owner can immediately call `GET /repositories/{id}/analysis`. |
| `400 Bad Request` | Reject malformed JSON, a non-object body, or missing, blank, or wrongly typed required fields. |
| `401 Unauthorized` | Reject an unknown caller using the existing identity rules. |
| `409 Conflict` | For the Business follow-up, reject duplicate URLs across all owners, including seeded repositories. Check before allocating an ID or analyzing, and return a generic error without exposing owner details. |

**Product decision still open.** I suggest exact URL comparison after trimming surrounding whitespace. Business should confirm whether registration requires a Git-host URL and whether variants such as a `.git` suffix or trailing slash count as the same URL. [S1-A card](../../facilitator/cards/S1-A.md#L20)
