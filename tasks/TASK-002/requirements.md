# Requirements: TASK-002

## The request in one sentence

Let owners remove and recover their own repositories and update their descriptions.

## Acceptance criteria

- **AC1.** An owner can remove their repository. It disappears from the active list, and its details, analysis, scan and description edit are unavailable while it is removed. Another user cannot remove it, and the attempt leaves it unchanged.
- **AC2.** The owner can list their removed repositories that are still eligible for recovery. Another user's removed repositories never appear in that list. A repository is eligible for seven days from removal and is absent from the recovery list once seven days have elapsed.
- **AC3.** The owner can restore an eligible repository. It returns to the active list with its original ID, details and saved analysis, and leaves the recovery list. An expired repository or one belonging to another user cannot be restored.
- **AC4.** An owner can update their active repository with a text description of 1 to 200 characters, inclusive. The saved description is returned when they retrieve the repository, and its other details and analysis are unchanged.
- **AC5.** A missing, non-text, empty or over-200-character description is rejected and leaves the saved description unchanged.
- **AC6.** A user cannot edit a repository owned by someone else, and the saved description is unchanged.

## Assumptions

None recorded.

## Open questions

None for the Architect handoff.

## Decisions

- Product Owner, 2026-11-26. Include S1-B and S1-C in TASK-002.
- Product Owner, 2026-11-26. Owners can list and restore their removed repositories for seven days. Restoration includes the saved analysis.
- Product Owner, 2026-11-26. Description edits require nonempty text of at most 200 characters.

## Out of scope

- Changes to repository registration from S1-A.

## Product Owner decision

Pending acceptance review.
