#!/usr/bin/env bash
# Pinned official release for GitHub's x86_64 Ubuntu runners.
set -euo pipefail

mdbook_archive="${RUNNER_TEMP:?}/mdbook-v0.4.52.tar.gz"
mdbook_bin="${RUNNER_TEMP}/omt-mdbook-bin"
mkdir -p "$mdbook_bin"
curl --fail --location --retry 3 \
  'https://github.com/rust-lang/mdBook/releases/download/v0.4.52/mdbook-v0.4.52-x86_64-unknown-linux-musl.tar.gz' \
  --output "$mdbook_archive"
printf '%s  %s\n' \
  'c96bdabf3754d9e016fb803c1565a41050434479b2dc1e02a87c8d0da7524c6c' \
  "$mdbook_archive" | sha256sum --check
tar -xzf "$mdbook_archive" -C "$mdbook_bin" mdbook
printf '%s\n' "$mdbook_bin" >> "${GITHUB_PATH:?}"
"$mdbook_bin/mdbook" --version
