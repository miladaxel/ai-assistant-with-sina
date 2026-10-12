# Query caching

Query caching is enabled by default. Set `DJANGO_QUERY_CACHE_ENABLED=False` in
`.env` to temporarily use live database reads. Redis connection settings remain
in `ai_asistant_with_sina/settings.py` and `.env.example`.

| Cached data | Lifetime |
| --- | --- |
| Exam questions and subquestions, shared by summary and correction | 30 minutes |
| Summary participants and participation list | 5 minutes |
| Teacher dashboard metrics | 1 minute |
| Classes and students | 5 minutes |
| Exam list pages and participant counts | 2 minutes |
| Grouped exam results report | 5 minutes |
| Analysis/exercise list pages and paginator counts | 1 minute |
| Successful analysis/exercise details | 1 hour |
| Prompt display choices | 30 minutes |
| Snapshot list pages and latest snapshot metadata | 5 minutes |
| Stage-one bundle options in the stage-two form | 1 minute |
| Homepage rendered HTML, anonymous visitors only | 5 minutes |

The homepage caches only its rendered HTML body for anonymous visitors. Logged-in
users bypass that cache on every request. Host, scheme and active language are
part of the guest key, and both guest and authenticated responses use
`Vary: Cookie`. Response cookies and middleware output are not stored in Redis.
Homepage template changes become visible after the five-minute lifetime expires;
`DJANGO_QUERY_CACHE_ENABLED=False` also disables this HTML cache during editing.

## Freshness and ownership

`ai_asistant_with_sina/query_cache.py` caches evaluated lists, model objects or
dictionaries, never an unevaluated QuerySet. List pages are fetched separately;
caching does not load every row before pagination. Keys include the user,
object, view and page as applicable.

Authentication and ownership checks execute before private detail/report cache
reads. Successful bundle details have a fresh ownership/status lookup. Pending
and failed bundle details use live reads. Grading responses and submitted form
validation use the database; only prompt display choices are cached.

`question/cache_signals.py` invalidates cache dependencies for model save/delete
and many-to-many add/remove/clear, including writes made through Django admin.
Custom managers cover `update`, `bulk_create` and `bulk_update` for cached domain
models. Invalidation runs after transaction commit. A rollback does not publish
invalidations. Cache misses inside SQL transactions are not stored, and ordinary
cached reads inside transactions bypass Redis. Correction can reuse already
cached question structure while keeping grades and missing-result creation live.

Dependency groups are `people`, `exams`, `participants`, `questions`, `grades`,
`bundles`, `prompts` and `snapshots`. Each group has a persistent random generation
token; invalidation changes that token, so old data keys expire naturally. Groups
are shared across teachers conservatively: a write can invalidate the same type
of cached data for other teachers, but values themselves remain owner-specific.
No Redis key scan or database-wide flush is used for application invalidation.

When adding raw SQL writes or direct writes to automatically generated join
tables, call `invalidate_groups(..., using=...)` for the affected dependencies.
Bulk writes through the authentication `Users` manager also need explicit
`people` invalidation if they change names displayed in cached data; normal user
save/delete is covered by signals. Keep the original UserManager for Django's
authentication and migration compatibility.

Redis connection failures fall back to database reads and are logged. If an
invalidation fails during an outage, previously stored values can remain until
their lifetime expires after Redis recovers.

## Verification

Run the suite from PowerShell:

```powershell
$env:DJANGO_DEBUG='False'
.\.venv\Scripts\python.exe manage.py test
```

Existing uncached SQL-count tests explicitly disable query caching. The dedicated
`question/test_query_cache.py` suite uses transactions and an isolated local
cache to verify hits, bulk/admin writes, membership changes, commit/rollback,
pagination, owner isolation, live form validation and database fallback.
`Profile/test_home_cache.py` verifies shared guest hits, authenticated bypass,
login/logout transitions, disabled caching and HEAD requests in an isolated cache.

An additional smoke check against the real Redis backend and the existing local
data verified serialization and cold/warm requests using a temporary, unique key
prefix. Only keys created by that check were removed afterwards. SQL counts for
views/templates (excluding session/auth middleware) were:

| Page | Cold cache | Warm cache |
| --- | ---: | ---: |
| Teacher dashboard | 4 | 1 |
| Exam summary | 4 | 1 |
| Results report | 2 | 1 |
| Exam list | 2 | 0 |
| Classes | 3 | 1 |
| Stage-one / stage-three lists | 2 | 0 |
| Stage-two list | 2 | 1 |
| Snapshot list | 3 | 1 |
| Successful stage-one / stage-two / stage-three details | 2 | 1 |

The cold summary fetch also preloads subquestions for subsequent correction
requests. The summary now supplies `exam_id` to its existing correction links.
No database schema changes or migrations are needed.
