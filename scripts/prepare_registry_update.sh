# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

#!/bin/bash
set -e

# Extract module name and version from MODULE.bazel
MODULE_LINE=$(grep -m1 "^module(" MODULE.bazel)
MODULE_NAME=$(echo "$MODULE_LINE" | sed -n 's/.*name *= *"\([^"]*\)".*/\1/p')
MODULE_VERSION=$(echo "$MODULE_LINE" | sed -n 's/.*version *= *"\([^"]*\)".*/\1/p')

if [[ -z "$MODULE_NAME" || -z "$MODULE_VERSION" ]]; then
  echo "Failed to extract module name or version from MODULE.bazel"
  exit 1
fi

# Prepare paths
DEST_DIR="bazel_registry_fork/modules/${MODULE_NAME}/${MODULE_VERSION}"
mkdir -p "$DEST_DIR"

# Copy MODULE.bazel
cp MODULE.bazel "$DEST_DIR"

# Generate source.json
REPO_URL="https://github.com/${GITHUB_REPOSITORY}"
TARBALL_URL="${REPO_URL}/archive/refs/tags/v${MODULE_VERSION}.tar.gz"
STRIP_PREFIX="$(basename "$REPO_URL")-${MODULE_VERSION}"

SOURCE_JSON=$(cat <<EOF
{
  "integrity": "",
  "strip_prefix": "${STRIP_PREFIX}",
  "url": "${TARBALL_URL}"
}
EOF
)
echo "$SOURCE_JSON" > "$DEST_DIR/source.json"

# Update metadata.json
METADATA_PATH="bazel_registry_fork/modules/${MODULE_NAME}/metadata.json"

if [[ -f "$METADATA_PATH" ]]; then
  if ! grep -q "\"${MODULE_VERSION}\"" "$METADATA_PATH"; then
    sed -i "/\"versions\": \[/a\    \"${MODULE_VERSION}\"," "$METADATA_PATH"
    # Optional: remove trailing comma from last element (make valid JSON)
    sed -i ':a;N;$!ba;s/,\n\s*]/\n  ]/' "$METADATA_PATH"
  fi
else
  echo "Warning: $METADATA_PATH not found. Creating a minimal one."
  cat <<EOF > "$METADATA_PATH"
{
  "repository": ["github:${GITHUB_REPOSITORY}"],
  "versions": ["${MODULE_VERSION}"],
  "yanked_versions": {}
}
EOF
fi

echo "Prepared registry update for ${MODULE_NAME} version ${MODULE_VERSION}."
