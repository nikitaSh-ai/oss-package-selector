# Raw Data Schema
Storage: SQLite (`data/raw_packages.db`), table name: `packages`

## Identity
- package_name        TEXT   -- npm package name, primary key
- category             TEXT   -- one of our 6 categories

## From GitHub API
- repo_url             TEXT
- stars                INTEGER
- forks                INTEGER
- open_issues          INTEGER
- last_commit_date     TEXT   -- ISO 8601 datetime
- created_at           TEXT   -- ISO 8601 datetime (repo age)
- contributor_count    INTEGER
- has_readme           INTEGER  -- 0/1 boolean
- has_wiki             INTEGER  -- 0/1 boolean
- license               TEXT
- default_branch        TEXT

## From npm Registry
- latest_version        TEXT
- weekly_downloads       INTEGER
- dependents_count       INTEGER
- is_deprecated          INTEGER  -- 0/1 boolean
- last_publish_date      TEXT     -- ISO 8601 datetime
- num_versions           INTEGER

## Metadata
- fetch_date             TEXT   -- ISO 8601 datetime, when we pulled this row
- fetch_errors           TEXT   -- nullable, notes partial/failed fetches

## Notes
- SQLite has no native BOOLEAN or DATETIME type — booleans stored as 
  INTEGER (0/1), dates stored as ISO 8601 TEXT strings (sortable, 
  parseable by pandas/Python directly).
- package_name is the primary key since npm names are globally unique.


## Known Data Limitations

### dependents_count
No reliable source was found for this metric. Investigated 3 options:
1. **npm registry API** — no official endpoint exists. Confirmed via 
   npm's own issue tracker (feature requested since 2017, never shipped).
2. **npmjs.com website scraping** — blocked by Cloudflare bot protection 
   (HTTP 403 on all requests).
3. **npms.io aggregator API** — endpoint exists but data is stale 
   (last analyzed ~2022); `dependentsCount` field is absent from 
   current responses, suggesting the service is no longer actively 
   maintained.

**Decision:** This field is retained in the schema for completeness 
but will remain NULL for all packages. This is documented as a known 
limitation rather than silently omitted.