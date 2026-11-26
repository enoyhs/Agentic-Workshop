# Requirements: TASK-001

## The request in one sentence

A registry user can register a repository and retrieve its first analysis as soon as registration succeeds.

## Acceptance criteria

- **AC1.** When a known user submits a nonblank string `name` and `url` to `POST /repositories`, the registry returns `201` with the repository details and assigns ownership to the caller. A supplied string `description` is saved. Omitting it yields an empty description.
- **AC2.** After registration succeeds, the owner can see the repository in their list and immediately retrieve its analysis without requesting a scan. A different user cannot see the repository in their list or retrieve its details or analysis.
- **AC3.** Malformed JSON, a body that is not a JSON object, a missing or blank required field, or a field of the wrong type returns `400` and creates no repository.
- **AC4.** An unknown caller receives `401` and creates no repository.
- **AC5.** If the initial analysis fails, registration fails and the repository does not appear in the owner's list.

## Assumptions

None recorded.

## Open questions

None for this handoff.

## Decisions

- Product Owner, 2026-11-26. Limit TASK-001 to S1-A only. This supersedes the earlier scope that included both cards.
- Product Owner, 2026-11-26. Use the proposal in `task.md` as the approved brief for repository registration and immediate analysis only.

## Out of scope

- S1-B.
- The duplicate-URL rejection follow-up.

## Product Owner decision

**ACCEPTED.** The delivered S1-A feature lets owners register repositories and retrieve their first analysis immediately, and QA verified all five acceptance criteria.
