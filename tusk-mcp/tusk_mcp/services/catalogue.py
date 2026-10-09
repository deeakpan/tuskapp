"""Price-list import: a CSV (exported from Excel, Google Sheets or Numbers) becomes the business's services.

Rows are matched to existing services by name, so re-importing an updated sheet changes prices instead of
duplicating items. Bad rows are reported back by row number and skipped; good rows are still saved.
"""

import csv
import io
import re
from dataclasses import dataclass, field
from typing import Any

from sqlmodel import Session

from tusk_mcp.services import business as biz
from tusk_mcp.services.business import Business

MAX_ROWS = 500
DEFAULT_DURATION_MIN = 30

# Accepted spellings for each column, compared after lower-casing and dropping symbols.
COLUMNS = {
    "name": {"name", "service", "item", "product", "title"},
    "price": {"price", "pricenaira", "price₦", "amount", "cost", "naira"},
    "duration": {"duration", "durationmin", "durationmins", "mins", "minutes", "time"},
    "description": {"description", "details", "notes", "about"},
    "published": {"published", "live", "available", "instock", "show"},
}
TEMPLATE = (
    "name,price,duration,description,published\n"
    "Knotless braids (medium),35000,5 hrs,Includes wash and blow-dry,yes\n"
    "UK-used iPhone 13 Pro 128GB,450000,,Battery 85%+ with 3-month warranty,yes\n"
)


@dataclass
class ImportResult:
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)

    def view(self) -> dict[str, Any]:
        return {"created": self.created, "updated": self.updated, "errors": self.errors}


class CatalogueError(ValueError):
    pass


def _header_key(header: str) -> str | None:
    clean = re.sub(r"[^a-z₦]", "", header.lower())
    return next((key for key, names in COLUMNS.items() if clean in names), None)


def parse_price_kobo(value: str) -> int:
    """'₦35,000', '35000', 'N35k', '1.2m' -> kobo."""
    text = value.strip().lower().replace(",", "").replace("₦", "").removeprefix("ngn").removeprefix("n").strip()
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([km]?)", text)
    if not match:
        raise CatalogueError(f"price “{value}” isn't a number")
    amount = float(match[1]) * {"": 1, "k": 1_000, "m": 1_000_000}[match[2]]
    if amount <= 0:
        raise CatalogueError("price must be more than 0")
    return round(amount * 100)


def parse_duration_min(value: str) -> int:
    """'90', '90 mins', '1.5 hrs', '2h 30m' -> minutes. Blank means a quick visit (products, pickups)."""
    text = value.strip().lower()
    if not text:
        return DEFAULT_DURATION_MIN
    if re.fullmatch(r"\d+", text):
        return int(text)
    hours = re.search(r"(\d+(?:\.\d+)?)\s*h", text)
    minutes = re.search(r"(\d+)\s*m", text)
    if not hours and not minutes:
        raise CatalogueError(f"duration “{value}” should be minutes, e.g. 90 or 1.5 hrs")
    total = round(float(hours[1]) * 60 if hours else 0) + (int(minutes[1]) if minutes else 0)
    if total <= 0:
        raise CatalogueError("duration must be more than 0")
    return total


def _published(value: str) -> bool:
    return value.strip().lower() not in {"no", "n", "false", "0", "hidden", "hide", "off"}


def read_rows(raw: bytes) -> list[dict[str, str]]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    try:
        dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.reader(io.StringIO(text), dialect)
    header = next(reader, None)
    if not header:
        raise CatalogueError("The file is empty.")
    keys = [_header_key(h) for h in header]
    if "name" not in keys or "price" not in keys:
        raise CatalogueError("The first row needs column names, including “name” and “price”.")
    rows = []
    for cells in reader:
        if not any(c.strip() for c in cells):
            continue
        rows.append({k: cells[i].strip() for i, k in enumerate(keys) if k and i < len(cells)})
        if len(rows) > MAX_ROWS:
            raise CatalogueError(f"Up to {MAX_ROWS} items per file.")
    if not rows:
        raise CatalogueError("No items found under the header row.")
    return rows


def import_catalogue(session: Session, business: Business, raw: bytes) -> ImportResult:
    rows = read_rows(raw)
    existing = {s.name.casefold(): s for s in biz.list_services(session, business, published_only=False)}
    result = ImportResult()
    for number, row in enumerate(rows, start=2):
        name = row.get("name", "")
        try:
            if len(name) < 2:
                raise CatalogueError("name is missing")
            fields = {
                "price_kobo": parse_price_kobo(row.get("price", "")),
                "duration_min": parse_duration_min(row.get("duration", "")),
                "is_published": _published(row.get("published", "yes")),
            }
        except CatalogueError as exc:
            result.errors.append({"row": number, "name": name or None, "message": str(exc)})
            continue
        description = row.get("description")
        if service := existing.get(name.casefold()):
            biz.update_service(session, business, service.id, description=description, **fields)
            result.updated.append(name)
        else:
            existing[name.casefold()] = biz.add_service(
                session, business, name=name, description=description or "", **fields
            )
            result.created.append(name)
    return result
