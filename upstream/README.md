# Upstream snapshots

`manifest.json` records the exact Open Music Theory source used by each
translation batch. Large source exports are not committed automatically.

The importer must never overwrite translated chapters. It stores normalized
English source separately, computes hashes, and reports chapters whose upstream
source has changed since review.

