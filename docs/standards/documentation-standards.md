# Documentation Standards

- Status: accepted
- Canonical for: documentation structure, authority, metadata, and updates

## Metadata

Substantive canonical documents identify:

- status,
- canonical responsibility,
- related ADRs or documents when relevant,
- verification or known gaps when relevant,
- supersession when applicable.

Accepted status values are `proposed`, `accepted`, `current`, `superseded`, `deprecated`, and `rejected`. `Current` is appropriate for registers whose contents change without representing one decision.

## Source Discipline

- Link to canonical sources rather than copying large rule sets.
- Keep exact schemas in executable contract files.
- Keep external-source wording bounded and record review dates in the source register.
- Keep context packs concise and derived.
- Keep implementation history in commits, issues, releases, or roadmaps rather than reusable architecture documents.

## Update Discipline

When behavior changes, update the owning canonical document, affected ADR, executable contract, context pack, and verification evidence in the same change. Update only sources made stale by the change.

## Link and Structure Checks

Documentation verification should eventually validate relative links, required metadata, context catalog paths, pack size, ADR status/supersession, and referenced repository commands. Until that check exists, gaps remain explicit in assurance documentation.

