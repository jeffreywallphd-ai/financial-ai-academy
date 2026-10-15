# Curriculum Graph v1 Compatibility Corpus

This corpus fixes one synthetic approved curriculum graph, canonical
`graph_digest` bytes, closed relationship and branch vocabularies, exact public
lesson and assessment references, and bounded denial behavior. The fixture
deliberately contains multiple entry activities, one required branch, multiple
optional branches, a partial presentation hint, and one unbranched activity.
Additional conformance coverage shares activities between branches of the same
kind, normalizes equivalent timestamps within the contract's bounded
microsecond-precision profile, and removes empty presentation hints before
hashing so the contract does not imply a single linear pathway, visual layout,
or representation-dependent digest. Values outside that profile fail closed
rather than being rounded or truncated.

The corpus contains no learner evidence, eligibility result, mastery estimate,
recommendation score, provider payload, tenancy fact, or approval record.
Contract conformance does not qualify persistence, API authorization, browser
behavior, or adaptation.
