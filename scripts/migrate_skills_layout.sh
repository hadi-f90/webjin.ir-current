#!/usr/bin/env bash
# Verify or complete WebJin's canonical skill layout:
# .claude/skills/<skill-name>/SKILL.md

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
cd "$repo_root"

mode="${1:---check}"
legacy_root=".claude/agents"
canonical_root=".claude/skills"

fail=0

check_layout() {
  local skill_path skill_name canonical legacy
  local -a expected_skills=(
    analytics-metrics-agent business-model-agent conversion-monetization-agent
    database-agent deployment-agent django-backend-agent documentation-agent
    facts-register-agent final-gate-agent growth-agent naming-law
    orchestrator-agent persian-qa-agent product-requirements-agent security-agent
    seo-agent testing-qa-agent ui-ux-agent watchdog-agent
  )
  for skill_name in "${expected_skills[@]}"; do
    canonical="$canonical_root/$skill_name/SKILL.md"
    if [[ ! -f "$canonical" ]]; then
      echo "ABSENT CANONICAL: $canonical"
      fail=1
    fi
  done
  while IFS= read -r -d '' skill_path; do
    skill_name="$(basename "$(dirname "$skill_path")")"
    canonical="$canonical_root/$skill_name/SKILL.md"
    echo "LEGACY DUPLICATE: $skill_path"
    fail=1
    if [[ ! -f "$canonical" ]]; then
      echo "ABSENT CANONICAL: $canonical"
      fail=1
    elif ! cmp -s "$skill_path" "$canonical"; then
      echo "CONFLICT: $skill_path != $canonical"
      fail=1
    fi
  done < <(find "$legacy_root" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print0 2>/dev/null | sort -z)

  while IFS= read -r -d '' canonical; do
    skill_name="$(basename "$(dirname "$canonical")")"
    legacy="$legacy_root/$skill_name/SKILL.md"
    if [[ -f "$legacy" ]] && ! cmp -s "$legacy" "$canonical"; then
      echo "CONFLICT: $legacy != $canonical"
      fail=1
    fi
  done < <(find "$canonical_root" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print0 2>/dev/null | sort -z)

  if [[ -f "$legacy_root/naming-law/scripts/naming_check.py" ]]; then
    echo "LEGACY DUPLICATE: $legacy_root/naming-law/scripts/naming_check.py"
    fail=1
  fi
  if [[ ! -f "$canonical_root/naming-law/scripts/naming_check.py" ]]; then
    echo "ABSENT CANONICAL: $canonical_root/naming-law/scripts/naming_check.py"
    fail=1
  fi
  if [[ "$fail" -eq 0 ]]; then
    echo "OK: canonical skill layout; no legacy SKILL.md copies"
  fi
  return "$fail"
}

apply_layout() {
  local legacy_files=() source dest skill_name parent first_source
  mapfile -d '' legacy_files < <(find "$legacy_root" -mindepth 2 -maxdepth 3 -type f -print0 2>/dev/null | sort -z)

  if [[ "${#legacy_files[@]}" -eq 0 ]]; then
    check_layout
    return
  fi

  declare -A destinations=()
  for source in "${legacy_files[@]}"; do
    if [[ "$source" == "$legacy_root/naming-law/scripts/naming_check.py" ]]; then
      dest="$canonical_root/naming-law/scripts/naming_check.py"
    elif [[ "$source" == */SKILL.md ]]; then
      skill_name="$(basename "$(dirname "$source")")"
      dest="$canonical_root/$skill_name/SKILL.md"
    else
      skill_name="$(basename "$(dirname "$(dirname "$source")")")"
      dest="$canonical_root/$skill_name/${source#"$legacy_root/$skill_name/"}"
    fi
    if [[ -n "${destinations[$dest]:-}" ]]; then
      first_source="${destinations[$dest]}"
      if ! cmp -s "$first_source" "$source"; then
        echo "ERROR: source conflict: $first_source differs from $source for $dest"
        return 1
      fi
      continue
    fi
    destinations["$dest"]="$source"
    if [[ -e "$dest" || -L "$dest" ]]; then
      if [[ ! -f "$dest" ]] || ! cmp -s "$source" "$dest"; then
        echo "ERROR: destination conflict: $dest differs from $source"
        return 1
      fi
    fi
    parent="$(dirname "$dest")"
    while [[ "$parent" != "." ]]; do
      if [[ -e "$parent" && ! -d "$parent" ]]; then
        echo "ERROR: destination parent conflict: $parent is not a directory"
        return 1
      fi
      parent="$(dirname "$parent")"
    done
  done

  declare -a copied_destinations=()
  for source in "${legacy_files[@]}"; do
    if [[ "$source" == "$legacy_root/naming-law/scripts/naming_check.py" ]]; then
      dest="$canonical_root/naming-law/scripts/naming_check.py"
    elif [[ "$source" == */SKILL.md ]]; then
      skill_name="$(basename "$(dirname "$source")")"
      dest="$canonical_root/$skill_name/SKILL.md"
    else
      skill_name="$(basename "$(dirname "$(dirname "$source")")")"
      dest="$canonical_root/$skill_name/${source#"$legacy_root/$skill_name/"}"
    fi
    if [[ -f "$dest" ]]; then continue; fi
    if ! mkdir -p "$(dirname "$dest")" || ! cp -p "$source" "$dest"; then
      echo "ERROR: copy failed: $source -> $dest"
      rm -f "$dest" || true
      for dest in "${copied_destinations[@]}"; do rm -f "$dest" || true; done
      return 1
    fi
    copied_destinations+=("$dest")
  done

  for source in "${legacy_files[@]}"; do
    if [[ "$source" == "$legacy_root/naming-law/scripts/naming_check.py" ]]; then
      dest="$canonical_root/naming-law/scripts/naming_check.py"
    elif [[ "$source" == */SKILL.md ]]; then
      skill_name="$(basename "$(dirname "$source")")"
      dest="$canonical_root/$skill_name/SKILL.md"
    else
      skill_name="$(basename "$(dirname "$(dirname "$source")")")"
      dest="$canonical_root/$skill_name/${source#"$legacy_root/$skill_name/"}"
    fi
    if [[ ! -f "$dest" ]] || ! cmp -s "$source" "$dest"; then
      echo "ERROR: verification failed: $dest"
      for dest in "${copied_destinations[@]}"; do rm -f "$dest" || true; done
      return 1
    fi
  done

  for source in "${legacy_files[@]}"; do rm -f "$source"; done
  find "$legacy_root" -depth -type d -empty -delete 2>/dev/null || true
  echo "MIGRATED: verified canonical copies; legacy copies removed"
  check_layout
}

case "$mode" in
  --check) check_layout ;;
  --apply) apply_layout ;;
  *) echo "Usage: bash scripts/migrate_skills_layout.sh --check|--apply" >&2; exit 2 ;;
esac
