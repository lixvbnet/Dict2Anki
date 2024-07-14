#!/bin/bash

find . -type f -name "*.py" -exec \
  gsed -i -E 's/^from[[:space:]]+PyQt5[[:space:]]+import[[:space:]]+(.*)/try:\n\tfrom PyQt6 import \1\nexcept Exception:\n\tfrom PyQt5 import \1/g' {} \;
