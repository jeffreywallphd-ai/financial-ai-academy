# Content Module

Content owns immutable lesson-package admission, publication metadata, source
provenance, safe typed lesson bodies, and private object-storage references.

## Public operations

- `ContentService.admit_lesson_package(AdmitLessonPackageRequest) -> AcceptedPackageVersion`
- `ContentService.get_published_lesson_version(GetPublishedLessonVersionRequest) -> PublishedLesson`

The read operation resolves one exact package ID, semantic version, and optional
digest. It never substitutes `latest`. Public results contain closed body-node
types and application-controlled asset identifiers; they contain no CommonMark,
HTML, host path, object key, database row, or driver value.

## Persistence and storage

The module owns `content.lesson_package_versions` through migration
`0001_content_lesson_package_versions`. Its filesystem object adapter accepts
only opaque `<digest-prefix>/<digest>` keys, writes a random restricted staging
directory, verifies staged bytes, and atomically renames the completed directory
before publication metadata becomes visible.

Validation or staging failure creates no publication. Metadata failure after
object finalization can leave an unreferenced digest-addressed object for later
bounded reconciliation, but never a partial published row. Exact stored bytes
are revalidated on read.
