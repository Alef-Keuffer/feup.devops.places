#!/usr/bin/env bash
# Mechanical checks on the report. Changes nothing; exits 1 if any check fails.
# Usage: check.sh [--self-test]

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# Fails on each Avoid word from glossary $1 (or its plural) found in files $2...
# A word listed with a condition in parentheses anywhere in the glossary is left to the agent review.
check_avoid() {
  glossary=$1; shift
  words=$(awk '
    /^_Avoid_:/ {
      sub(/^_Avoid_: */, "")
      n = split($0, item, / *, */)
      for (i = 1; i <= n; i++) {
        w = tolower(item[i])
        if (w ~ /\(/) { sub(/ *\(.*/, "", w); conditional[w] = 1 }
        else if (w !~ /\)/) plain[w] = 1
      }
    }
    END {
      for (w in plain) if (!(w in conditional)) {
        print w; print w "s"
        if (w ~ /y$/) print substr(w, 1, length(w) - 1) "ies"
      }
    }
  ' "$glossary")
  ! grep -HnoiwF -f <(printf '%s\n' "$words") "$@" | sed 's/^\([^:]*:[0-9]*\):\(.*\)/\1: Avoid word "\2" (see GLOSSARY.md)/' | grep .
}

self_test() {
  printf '_Avoid_: Owner, schedule entry, space (when a precise term is meant)\n_Avoid_: Hall, space\n' > "$tmp/GLOSSARY.md"
  printf 'The Venue is open.\nThe owners agreed.\n' > "$tmp/avoid.md"
  printf 'Two schedule entries.\n' > "$tmp/plural.md"
  printf 'A space inside a Venue.\n' > "$tmp/conditional.md"
  out=$(check_avoid "$tmp/GLOSSARY.md" "$tmp/avoid.md") && { echo "self-test FAIL: a sample with an Avoid word passed"; return 1; }
  case $out in *avoid.md:2*owners*) ;; *) echo "self-test FAIL: message does not name file, line and word: $out"; return 1 ;; esac
  check_avoid "$tmp/GLOSSARY.md" "$tmp/plural.md" >/dev/null && { echo "self-test FAIL: a plural in -ies passed"; return 1; }
  check_avoid "$tmp/GLOSSARY.md" "$tmp/conditional.md" || { echo "self-test FAIL: an Avoid word with a condition failed"; return 1; }
  echo "self-test ok"
}

[ "${1:-}" = --self-test ] && { self_test; exit; }

cd "$(git rev-parse --show-toplevel)" || exit 1
status=0
openapi=$(git ls-files -co --exclude-standard -- '*openapi.yaml')

echo "== Avoid words"
check_avoid GLOSSARY.md report/*.md $openapi || status=1

echo "== OpenAPI lint"
if [ -z "$openapi" ]; then
  echo "skipped: no openapi.yaml yet"
else
  npx --yes @redocly/cli lint $openapi || { echo "FAIL: $openapi does not lint clean"; status=1; }
fi

echo "== PDF build and citations"
# Builds to a temp file so the check changes nothing.
if ! pandoc -d report/pandoc.yaml -o "$tmp/report.pdf" 2> "$tmp/pandoc.log"; then
  cat "$tmp/pandoc.log"; echo "FAIL: the PDF does not build"; status=1
elif grep 'Citeproc: citation' "$tmp/pandoc.log"; then
  echo "FAIL: a citation does not resolve; add it to report/references.bib"; status=1
fi

[ $status = 0 ] && echo "All mechanical checks pass."
exit $status
