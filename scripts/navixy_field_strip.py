"""
Trim Navixy Field values down to their parameter name (no label text).
"""

import csv
from pathlib import Path
from typing import Iterable, Tuple


def read_csv(path: Path) -> Tuple[list[list[str]], str]:
    """Read CSV using a set of common encodings."""
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            with path.open(newline="", encoding=encoding) as f:
                return list(csv.reader(f)), encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8", b"", 0, 1, "Unable to decode file with supported encodings")


def write_csv(path: Path, rows: Iterable[list[str]], encoding: str) -> None:
    with path.open("w", newline="", encoding=encoding) as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def main() -> None:
    path = Path("docs/working/Fleeti_Field_Mapping_Expanded.csv")
    rows, encoding = read_csv(path)
    if not rows:
        return
    header = rows[0]
    idx_navixy = header.index("Navixy Field")
    count = 0

    for row in rows[1:]:
        if len(row) <= idx_navixy:
            continue
        value = row[idx_navixy]
        l = value.find("(")
        if l != -1:
            code = value[:l].strip()
            if code:
                row[idx_navixy] = code
                count += 1

    write_csv(path, rows, encoding)
    print(count)


if __name__ == "__main__":
    main()

