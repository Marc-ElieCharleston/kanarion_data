#!/bin/bash
# Tags a new database release
# Usage: ./scripts/tag_release.sh
# Reads version from _meta/version.json, creates annotated tag, pushes it
set -e

cd "$(dirname "$0")/.."

# Read version from version.json
VERSION=$(python3 -c "import json; print(json.load(open('_meta/version.json'))['version'])" 2>/dev/null \
  || python -c "import json; print(json.load(open('_meta/version.json'))['version'])")

TAG="db-v${VERSION}"

echo "Tagging: $TAG"

# Check if tag already exists
if git tag -l "$TAG" | grep -q "$TAG"; then
  echo "ERROR: Tag $TAG already exists!"
  echo "Bump the version in _meta/version.json first."
  exit 1
fi

# Verify hash is fresh
./scripts/gen_hash.sh

# Create and push tag
git tag -a "$TAG" -m "Database $VERSION"
git push origin "$TAG"

echo ""
echo "Tagged: $TAG"
echo "To use in front/back: update submodule to this commit"
