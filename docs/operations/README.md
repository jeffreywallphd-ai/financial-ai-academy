# Operations Documentation

- Status: partially accepted
- Canonical for: operations-document routing

## Accepted Design Boundaries

- [Community Backup and Restore](community-backup-and-restore.md) defines the user-invoked, maintenance-mode backup, empty-target restore, and no-RPO/RTO support-claim boundary. Its tooling and controlled qualification remain gaps.

Operational documents will cover:

- local installation and data location,
- configuration and secret resolution,
- backup, restore, and portable export,
- schema and contract migrations,
- provider outages, quotas, and degraded behavior,
- model disable/rollback,
- cloud deployment qualification,
- incident response and recovery objectives.

Operations claims require executable or controlled-environment evidence. An accepted workflow design is not evidence that commands, platform support, or recovery guarantees exist.
