import re
from dataclasses import dataclass
from difflib import unified_diff


@dataclass
class AddHunk:
    b_startline: int
    b_endline: int
    b_content: str
    insert_line: int


@dataclass
class DelHunk:
    a_startline: int
    a_endline: int
    a_content: str


@dataclass
class ModHunk:
    a_startline: int
    a_endline: int
    b_startline: int
    b_endline: int
    a_content: str
    b_content: str


def diff(a: str, b: str) -> str:
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    diff_lines = list(unified_diff(a_lines, b_lines))
    return "".join(diff_lines)


def diff_files(a_path: str, b_path: str) -> str:
    with open(a_path, "r") as f:
        a = f.read()
    with open(b_path, "r") as f:
        b = f.read()
    return diff(a, b)


def parse_diff(diff: str) -> dict[str, list[int]]:
    """
    Parse a unified diff string and return a dictionary with added and deleted line numbers.
    The returned dictionary has two keys: "add" and "delete", each mapping to a list of line numbers.

    Args:
        diff (str): A unified diff string.

    Returns:
        dict[str, list[int]]: A dictionary with keys "add" and "delete" containing lists of line numbers that were added or deleted.
    """
    info = {"add": [], "delete": []}
    current_a = current_b = None

    for line in diff.splitlines():
        if line.startswith("@@"):
            match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            if not match:
                current_a = current_b = None
                continue
            current_a = int(match.group(1)) - 1
            current_b = int(match.group(3)) - 1
            continue
        if current_a is None or current_b is None:
            continue
        if line.startswith("\\ No newline at end of file") or line.startswith("?"):
            continue
        if line.startswith("+") and not line.startswith("+++"):
            current_b += 1
            info["add"].append(current_b)
            continue
        if line.startswith("-") and not line.startswith("---"):
            current_a += 1
            info["delete"].append(current_a)
            continue
        if line.startswith(" ") or line == "":
            current_a += 1
            current_b += 1
    return info


def context_map(content: str, diff_lines: list[int]) -> dict[int, int]:
    """
    Create a mapping from original line numbers to modified line numbers based on the diff lines.

    Args:
        content (str): The original content as a string.
        diff_lines (list[int]): A list of line numbers that were added or deleted.

    Returns:
        dict[int, int]: A dictionary mapping original line numbers to modified line numbers.
    """
    lines = content.splitlines(keepends=True)
    mapping = {}
    offset = 0
    for i in range(len(lines)):
        original_line_num = i + 1
        if original_line_num in diff_lines:
            offset += 1
        mapping[original_line_num] = original_line_num + offset
    return mapping


def diff_lines_group(diff_lines: list[int]) -> list[list[int]]:
    """
    Group consecutive line numbers into sublists.

    Args:
        diff_lines (list[int]): A list of line numbers.

    Returns:
        list[list[int]]: A list of lists, where each sublist contains consecutive line numbers
    """

    if not diff_lines:
        return []
    diff_lines = sorted(diff_lines)
    groups = []
    current_group = [diff_lines[0]]
    for line in diff_lines[1:]:
        if line == current_group[-1] + 1:
            current_group.append(line)
        else:
            groups.append(current_group)
            current_group = [line]
    groups.append(current_group)
    return groups


def lines_map(a_map: dict[int, int], b_map: dict[int, int]) -> dict[int, int]:
    """
    Create a mapping from line numbers in content A to line numbers in content B based on their
    respective context maps.
    """
    reverse_b = {pivot: line for line, pivot in b_map.items()}
    return {
        line: reverse_b[pivot] for line, pivot in a_map.items() if pivot in reverse_b
    }


def hunkmap(
    del_lines_group: list[list[int]],
    add_lines_group: list[list[int]],
    lines_mapping: dict[int, int],
):
    hunk_map: dict[tuple[int, int], tuple[int, int]] = {}
    lines_mapping[0] = 0
    lines_mapping[max(lines_mapping.keys()) + 1] = max(lines_mapping.values()) + 1
    for del_lines in del_lines_group:
        del_head = del_lines[0] - 1
        del_tail = del_lines[-1] + 1
        for add_lines in add_lines_group:
            add_head = add_lines[0] - 1
            add_tail = add_lines[-1] + 1
            if (
                del_head in lines_mapping
                and del_tail in lines_mapping
                and lines_mapping[del_head] == add_head
                and lines_mapping[del_tail] == add_tail
            ):
                hunk_map[(del_head + 1, del_tail - 1)] = (add_head + 1, add_tail - 1)
                continue
    return hunk_map


def diff_hunks(a: str, b: str) -> tuple[list[DelHunk], list[AddHunk], list[ModHunk]]:
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    modifiedLines = parse_diff(diff(a, b))
    a_map = context_map(a, modifiedLines["delete"])
    b_map = context_map(b, modifiedLines["add"])
    del_groups = diff_lines_group(modifiedLines["delete"])
    add_groups = diff_lines_group(modifiedLines["add"])
    lines_mapping = lines_map(a_map, b_map)
    modify_hunks_map = hunkmap(del_groups, add_groups, lines_mapping)
    r_line_map = {v: k for k, v in lines_mapping.items()}

    del_hunks: list[DelHunk] = []
    add_hunks: list[AddHunk] = []
    mod_hunks: list[ModHunk] = []

    for del_hunk in del_groups:
        first_line, last_line = del_hunk[0], del_hunk[-1]
        if (first_line, last_line) not in modify_hunks_map.keys():
            del_hunks.append(
                DelHunk(
                    first_line,
                    last_line,
                    "\n".join(a_lines[first_line - 1 : last_line]),
                )
            )
    for add_hunk in add_groups:
        first_line, last_line = add_hunk[0], add_hunk[-1]
        if (first_line, last_line) not in modify_hunks_map.values():
            insert_line = r_line_map[first_line - 1]
            add_hunks.append(
                AddHunk(
                    first_line,
                    last_line,
                    "\n".join(b_lines[first_line - 1 : last_line]),
                    insert_line,
                )
            )

    for a_hunk, b_hunk in modify_hunks_map.items():
        a_first_line, a_last_line = a_hunk
        b_first_line, b_last_line = b_hunk
        mod_hunks.append(
            ModHunk(
                a_first_line,
                a_last_line,
                b_first_line,
                b_last_line,
                "\n".join(a_lines[a_first_line - 1 : a_last_line]),
                "\n".join(b_lines[b_first_line - 1 : b_last_line]),
            )
        )
    return del_hunks, add_hunks, mod_hunks
