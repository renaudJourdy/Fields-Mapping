import csv
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


TELTONIKA_URL = "https://flespi.com/protocols/teltonika"
START_MARKER = '<div class="d-table -parameters tab">'
END_MARKER = '<div class="d-table -commands tab">'
OUTPUT_PATH = Path("docs/reference/Flespi - Teltonika AVL ID.csv")
NOTES_VALUE = "flespi Teltonika protocol page, last retrieved 2025-11-28"


class ParametersTableParser(HTMLParser):
    """Extract ordered table cell texts from the Teltonika parameters table."""

    def __init__(self) -> None:
        super().__init__()
        self._cells: list[tuple[str, bool]] = []
        self._capture = False
        self._head_cell = False
        self._buffer: list[str] = []

    @property
    def cells(self) -> list[tuple[str, bool]]:
        return self._cells

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        attrs_map = dict(attrs)
        if tag == "div" and "class" in attrs_map and "d-table__cell" in attrs_map["class"]:
            self._capture = True
            self._head_cell = "-head" in attrs_map["class"]
            self._buffer = []
            return

        if self._capture and tag == "br":
            self._buffer.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._capture and tag == "div":
            text = "".join(self._buffer).strip()
            # collapse internal whitespace while preserving single spaces
            cleaned = re.sub(r"\s+", " ", text)
            self._cells.append((cleaned, self._head_cell))
            self._capture = False
            self._head_cell = False

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buffer.append(data)


def fetch_teltonika_html() -> str:
    with urllib.request.urlopen(TELTONIKA_URL) as response:
        return response.read().decode("utf-8")


def extract_table_html(raw_html: str) -> str:
    start_idx = raw_html.index(START_MARKER)
    end_idx = raw_html.index(END_MARKER, start_idx)
    return raw_html[start_idx:end_idx]


def parse_cells(table_html: str) -> list[dict[str, str]]:
    parser = ParametersTableParser()
    parser.feed(table_html)
    data_cells = [text for text, is_head in parser.cells if not is_head]

    if len(data_cells) % 5 != 0:
        raise ValueError(f"Unexpected cell count: {len(data_cells)} is not divisible by 5")

    rows = []
    for idx in range(0, len(data_cells), 5):
        rows.append(
            {
                "name": data_cells[idx],
                "type": data_cells[idx + 1],
                "unit": data_cells[idx + 2],
                "description": data_cells[idx + 3],
                "sources": data_cells[idx + 4],
            }
        )
    return rows


def expand_avl_ids(source_text: str) -> list[int]:
    ids: list[int] = []
    for match in re.finditer(r"AVL ID\s*([0-9]+(?:\.\.\.[0-9]+)?)", source_text):
        token = match.group(1)
        if "..." in token:
            start_str, end_str = token.split("...")
            start, end = int(start_str), int(end_str)
            if end < start:
                start, end = end, start
            ids.extend(range(start, end + 1))
        else:
            ids.append(int(token))
    return ids


def build_records(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in rows:
        avl_ids = expand_avl_ids(row["sources"])
        if not avl_ids:
            continue
        for avl_id in avl_ids:
            records.append(
                {
                    "AVL ID": str(avl_id),
                    "Parameter Name": row["name"],
                    "flespi Parameter Path": row["name"],
                    "Data Type": row["type"],
                    "Units": row["unit"] or "N/A",
                    "Description": row["description"],
                    "Notes / Source": NOTES_VALUE,
                }
            )
    records.sort(key=lambda item: int(item["AVL ID"]))
    return records


def write_csv(records: list[dict[str, str]]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "AVL ID",
                "Parameter Name",
                "flespi Parameter Path",
                "Data Type",
                "Units",
                "Description",
                "Notes / Source",
            ],
        )
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    html = fetch_teltonika_html()
    table_html = extract_table_html(html)
    parsed_rows = parse_cells(table_html)
    records = build_records(parsed_rows)
    write_csv(records)
    print(f"Wrote {len(records)} parameter rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

