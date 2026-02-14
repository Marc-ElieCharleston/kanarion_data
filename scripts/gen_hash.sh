#!/bin/bash
# Generates a SHA-256 content_hash of all gameplay JSON files
# Includes: file paths + content (detects renames)
# Excludes: metadata files that shouldn't invalidate authoritative gameplay
# Usage: ./scripts/gen_hash.sh

set -e
cd "$(dirname "$0")/.."

# Hash = SHA-256 of (filepath + content) for each gameplay JSON
# Sorted by path for determinism
HASH=$(find . -name "*.json" \
  -not -path "./.git/*" \
  -not -path "./kanarion-editor/*" \
  -not -path "./scripts/*" \
  -not -path "./_meta/version.json" \
  -not -path "./_meta/statistics.json" \
  -not -path "./_meta/index.json" \
  -not -path "./_meta/changelog.json" \
  -not -path "./_meta/ideas_to_integrate.json" \
  | sort \
  | while read f; do
      echo "$f"
      cat "$f"
    done \
  | sha256sum | cut -d' ' -f1)

echo "content_hash: sha256:${HASH}"

# Update version.json
python -c "
import json
with open('_meta/version.json', 'r') as f:
    v = json.load(f)
v['content_hash'] = 'sha256:${HASH}'
v['last_updated'] = '$(date +%Y-%m-%d)'
with open('_meta/version.json', 'w') as f:
    json.dump(v, f, indent=2)
    f.write('\n')
print('Updated _meta/version.json')
print(f'  content_hash: sha256:${HASH}')
print(f'  schema_version: {v.get(\"schema_version\", \"N/A\")}')
print(f'  database_version: {v.get(\"database_version\", \"N/A\")}')
"
