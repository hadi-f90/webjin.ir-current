import os
import sys
import re

# ---------------------------------------------------------
# Help message
# ---------------------------------------------------------
HELP_TEXT = """
File Concatenation Utility
--------------------------

Usage:
  python concat.py <ext-filters> [directory] [depth] [--output=<file>] [--tree]

Where <ext-filters> supports inclusion (+) and exclusion (-) groups:

Accepted formats for extension groups:
  +(py,html)    tuple-style
  +[py,html]    list-style
  +{py,html}    set-style

  -(log,tmp)
  -[log,tmp]
  -{git,cache}

Examples:
  python concat.py '+(py,html) -(git,)' . --tree
  python concat.py '+[py,md]' src 2 --output=merged.txt
  python concat.py '+{txt,md} -{log,tmp}'

Options:
  directory         Directory to scan (default: current directory)
  depth             Maximum folder depth (integer; default: unlimited)
  --output=<file>   Output file path (default: ./concatenated_output.txt)
  --tree            Add directory tree at the top of the output
  -h, --help        Show this help message and exit

Additional:
  · The script automatically skips itself when concatenating.
  · UTF-8 text is assumed; unreadable files are skipped.
"""

# ---------------------------------------------------------
# Parse extension groups: +(py,html), +[py,html], +{py,html}
# ---------------------------------------------------------
def parse_ext_groups(text):
    includes, excludes = [], []
    pattern = r'([+-])\s*[\(\[\{]\s*([^)\]\}]+?)\s*[\)\]\}]'
    matches = re.findall(pattern, text)

    for sign, content in matches:
        exts = [
            x.strip().lstrip('.')
            for x in content.split(',')
            if x.strip()
        ]
        if sign == '+':
            includes.extend('.' + e for e in exts)
        else:
            excludes.extend('.' + e for e in exts)

    return includes, excludes


# ---------------------------------------------------------
# Walk directories with depth control
# ---------------------------------------------------------
def walk_directory(base_dir, max_depth):
    base_dir = os.path.abspath(base_dir)
    base_depth = base_dir.rstrip(os.sep).count(os.sep)

    for root, dirs, files in os.walk(base_dir):
        current_depth = root.count(os.sep) - base_depth
        if max_depth is not None and current_depth > max_depth:
            dirs[:] = []
            continue
        for f in files:
            yield os.path.join(root, f)


# ---------------------------------------------------------
# Filtering logic
# ---------------------------------------------------------
def is_allowed(filename, includes, excludes):
    if any(filename.endswith(ext) for ext in excludes):
        return False
    if includes and not any(filename.endswith(ext) for ext in includes):
        return False
    return True


# ---------------------------------------------------------
# Build directory tree
# ---------------------------------------------------------
def build_tree(root_dir, max_depth):
    root_dir = os.path.abspath(root_dir)
    tree_lines = []
    base_depth = root_dir.rstrip(os.sep).count(os.sep)

    for root, dirs, files in os.walk(root_dir):
        depth = root.count(os.sep) - base_depth
        if max_depth is not None and depth > max_depth:
            dirs[:] = []
            continue

        indent = "  " * depth
        tree_lines.append(f"{indent}{os.path.basename(root)}/")

        for f in files:
            tree_lines.append(f"{indent}  {f}")

    return "\n".join(tree_lines)


# ---------------------------------------------------------
# Main Program
# ---------------------------------------------------------
def main():
    # Early help-parsing
    if any(arg in ("--help", "-h") for arg in sys.argv[1:]):
        print(HELP_TEXT)
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Error: Missing extension filters.\n")
        print(HELP_TEXT)
        sys.exit(1)

    script_path = os.path.abspath(sys.argv[0])

    ext_arg = sys.argv[1]
    includes, excludes = parse_ext_groups(ext_arg)

    directory = "."
    depth = None
    output_file = None
    show_tree = False

    for arg in sys.argv[2:]:
        if arg.startswith("--output="):
            output_file = arg.split("=", 1)[1].strip()
        elif arg == "--tree":
            show_tree = True
        elif arg.isdigit():
            depth = int(arg)
        else:
            directory = arg

    if not output_file:
        output_file = os.path.join(os.getcwd(), "concatenated_output.txt")

    with open(output_file, "w", encoding="utf-8", buffering=1024 * 1024) as out:

        if show_tree:
            out.write("=== DIRECTORY TREE ===\n")
            out.write(build_tree(directory, depth))
            out.write("\n\n=== FILE CONTENTS ===\n\n")

        for filepath in walk_directory(directory, depth):
            if os.path.abspath(filepath) == script_path:
                continue
            filename = os.path.basename(filepath)
            if not is_allowed(filename, includes, excludes):
                continue

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    out.write(f"----- {filepath} -----\n")
                    out.write(f.read())
                    out.write("\n\n")
            except Exception as e:
                sys.stderr.write(f"Skipping {filepath}: {e}\n")

    print(f"Done. Output saved to: {output_file}")


if __name__ == "__main__":
    main()

