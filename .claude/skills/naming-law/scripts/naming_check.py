#!/usr/bin/env python3
"""naming_check.py - static naming/consistency checks for WebJin.

Usage: python naming_check.py [project_root]
Exit code 1 if any ERROR is found. WARN items are advisory.
Checks: undefined URL names, blocks not defined by the parent template,
JS getElementById ids missing from the page, partials without '_',
related_name ending in _set.
"""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SKIP = {".git", ".venv", "venv", "node_modules", "staticfiles", "__pycache__"}


def files(pattern):
    return [p for p in root.rglob(pattern) if not (set(p.parts) & SKIP)]


errors, warns = [], []

# 1. URL names
defined = set()
for f in files("urls.py"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    defined |= set(re.findall(r"name\s*=\s*['\"]([\w\-]+)['\"]", text))
used = {}
for f in files("*.html"):
    for n in re.findall(r"{%\s*url\s+['\"]([\w\-]+)['\"]", f.read_text(encoding="utf-8", errors="ignore")):
        used.setdefault(n, set()).add(f)
for f in files("*.py"):
    if f.name == "urls.py":
        continue
    for n in re.findall(r"(?:reverse|reverse_lazy|redirect)\(\s*['\"]([\w\-]+)['\"]", f.read_text(encoding="utf-8", errors="ignore")):
        used.setdefault(n, set()).add(f)
for n, where in sorted(used.items()):
    if defined and n not in defined and not n.startswith(("admin:", "captcha")):
        errors.append(f"URL name '{n}' not defined (used in {', '.join(sorted(str(w.relative_to(root)) for w in where))})")

# 2. blocks vs parent
tmpl = {}
for f in files("*.html"):
    tmpl[f] = f.read_text(encoding="utf-8", errors="ignore")


def find_template(name):
    for f in tmpl:
        if str(f).replace("\\", "/").endswith("/" + name):
            return f
    return None


def blocks_of(f, seen=None):
    seen = seen or set()
    if f in seen:
        return set()
    seen.add(f)
    text = tmpl[f]
    out = set(re.findall(r"{%\s*block\s+(\w+)", text))
    m = re.search(r"{%\s*extends\s+['\"]([^'\"]+)['\"]", text)
    if m:
        parent = find_template(m.group(1))
        if parent:
            out |= blocks_of(parent, seen)
    return out


for f, text in tmpl.items():
    m = re.search(r"{%\s*extends\s+['\"]([^'\"]+)['\"]", text)
    if not m:
        continue
    parent = find_template(m.group(1))
    if not parent:
        warns.append(f"{f.relative_to(root)}: parent '{m.group(1)}' not found")
        continue
    parent_blocks = blocks_of(parent)
    for b in set(re.findall(r"{%\s*block\s+(\w+)", text)):
        if b not in parent_blocks:
            errors.append(f"{f.relative_to(root)}: block '{b}' not defined by parent chain ({m.group(1)})")

# 3. DOM ids
for f, text in tmpl.items():
    ids = set(re.findall(r"\bid\s*=\s*[\"']([\w\-]+)[\"']", text))
    refs = set(re.findall(r"getElementById\(\s*['\"]([\w\-]+)['\"]", text))
    for i in sorted(refs - ids):
        warns.append(f"{f.relative_to(root)}: JS reads id '{i}' that is not in this template")

# 4. partials
for f, text in tmpl.items():
    pass
included = set()
for text in tmpl.values():
    included |= set(re.findall(r"{%\s*include\s+['\"]([^'\"]+)['\"]", text))
for inc in sorted(included):
    base = inc.split("/")[-1]
    if not base.startswith("_"):
        warns.append(f"partial '{inc}' does not start with '_' (naming-law 3)")

# 5. related_name *_set
for f in files("models.py"):
    for n in re.findall(r"related_name\s*=\s*['\"](\w+_set)['\"]", f.read_text(encoding="utf-8", errors="ignore")):
        warns.append(f"{f.relative_to(root)}: related_name '{n}' ends with _set (legacy L-01)")

for e in errors:
    print("ERROR", e)
for w_ in warns:
    print("WARN ", w_)
print(f"{len(errors)} error(s), {len(warns)} warning(s)")
sys.exit(1 if errors else 0)
