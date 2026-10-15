# API Contracts

The reviewed OpenAPI 3.1 snapshot is generated from validated API models and
committed here. Generated TypeScript clients must be reproducible from that
snapshot.

`GET /api/v1/curriculum/opportunities` is the protected, queryless discovery
browse operation. It requires the opaque session cookie, accepts no learner or
permission selector, and returns the closed discovery v1 envelope with no
provider, database, or learner identity fields. Search, filtering, sorting,
and pagination are deliberately absent until their later slice defines stable
semantics.

