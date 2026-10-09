"""Matches a customer's request to businesses and lays out the trade-offs between them.

Nothing here knows about particular businesses or categories. Every candidate is measured on the same
criteria (how well it fits the request, price, distance, home service, how soon it's free), the
criteria are weighted by what the customer says matters most, and each option is described relative to
the others ("closest, but the priciest") so the assistant can explain the choice in its own words.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Literal

from sqlmodel import Session

from tusk_mcp.models import Service
from tusk_mcp.services import geo
from tusk_mcp.services.business import (
    LAGOS,
    Business,
    duration_label,
    free_start_times,
    keywords,
    list_services,
    naira,
    open_businesses,
    when_label,
)

Priority = Literal["balanced", "closest", "cheapest", "soonest", "best_match"]

WEIGHTS: dict[str, dict[str, float]] = {
    "balanced": {"fit": 0.35, "price": 0.25, "distance": 0.25, "soonest": 0.15},
    "closest": {"fit": 0.25, "price": 0.15, "distance": 0.50, "soonest": 0.10},
    "cheapest": {"fit": 0.25, "price": 0.50, "distance": 0.15, "soonest": 0.10},
    "soonest": {"fit": 0.25, "price": 0.15, "distance": 0.15, "soonest": 0.45},
    "best_match": {"fit": 0.60, "price": 0.15, "distance": 0.15, "soonest": 0.10},
}
OVER_BUDGET_PENALTY = 0.6
SEARCH_DAYS = 7
MAX_OPTIONS = 5
# Options matching less than this share of what the best option matches are noise ("office" in "office delivery").
MIN_RELATIVE_FIT = 0.5


@dataclass
class Preferences:
    need: str = ""
    near: str | None = None
    budget_kobo: int | None = None
    home_service: bool = False
    day: date | None = None
    category: str | None = None
    priority: Priority = "balanced"


@dataclass
class Option:
    business: Business
    services: list[Service]
    fit: float
    price_kobo: int
    distance_km: float | None
    in_area: bool
    next_free: datetime | None
    over_budget: bool = False
    score: float = 0.0
    strengths: list[str] = field(default_factory=list)
    tradeoffs: list[str] = field(default_factory=list)


def _next_free(session: Session, business: Business, service: Service, day: date | None) -> datetime | None:
    today = datetime.now(LAGOS).date()
    days = [day] if day else [today + timedelta(days=i) for i in range(SEARCH_DAYS)]
    for candidate in days:
        if times := free_start_times(session, business, service, candidate):
            return times[0]
    return None


def _in_category(business: Business, category: str) -> bool:
    """Loose match, so 'hair salon' or 'phone shop' finds a business filed under 'salon' or 'phones'."""
    return bool(keywords(category) & keywords(f"{business.category} {business.name}"))


def _candidate(
    session: Session, business: Business, prefs: Preferences, words: set[str], origin: geo.Point | None
) -> Option | None:
    if prefs.category and not _in_category(business, prefs.category):
        return None
    if prefs.home_service and not business.home_service:
        return None
    services = list_services(session, business)
    if not services:
        return None
    fit = 1.0
    if words:
        overlap = {s.id: len(words & keywords(f"{s.name} {s.description}")) for s in services}
        best = max(overlap.values())
        matched = [s for s in services if best and overlap[s.id] == best]
        found = keywords(f"{business.name} {business.category} {business.about}")
        for service in matched:
            found |= keywords(f"{service.name} {service.description}")
        fit = len(words & found) / len(words)
        # A casual description ("something for my sister's wedding") may share no words with a business
        # that's still the right kind; the category keeps it in, ranked below anything that does match.
        if not fit and not prefs.category:
            return None
        services = matched or services
    services = sorted(services, key=lambda s: s.price_kobo)
    price = services[0].price_kobo + (business.home_service_fee_kobo if prefs.home_service else 0)
    location = business.location
    near_words = keywords(prefs.near or "")
    return Option(
        business=business,
        services=services,
        fit=fit,
        price_kobo=price,
        distance_km=geo.distance_km(origin, location) if origin and location else None,
        in_area=bool(near_words & keywords(f"{business.area} {business.address}")),
        next_free=_next_free(session, business, services[0], prefs.day),
        over_budget=prefs.budget_kobo is not None and price > prefs.budget_kobo,
    )


def _closeness(value: float, values: list[float]) -> float:
    """1 for the lowest of `values`, 0 for the highest, linear in between; 1 when they're all equal."""
    low, high = min(values), max(values)
    return 1.0 if high == low else (high - value) / (high - low)


def _score(options: list[Option], prefs: Preferences) -> None:
    weights = WEIGHTS[prefs.priority]
    prices = [o.price_kobo for o in options]
    distances = [o.distance_km for o in options if o.distance_km is not None]
    now = datetime.now(LAGOS)
    waits = [(o.next_free - now).total_seconds() for o in options if o.next_free]
    for o in options:
        if o.distance_km is not None:
            distance = _closeness(o.distance_km, distances)
        else:
            distance = 0.6 if o.in_area else 0.3 if distances else 0.5
        soonest = _closeness((o.next_free - now).total_seconds(), waits) if o.next_free else 0.0
        o.score = (
            weights["fit"] * o.fit
            + weights["price"] * _closeness(o.price_kobo, prices)
            + weights["distance"] * distance
            + weights["soonest"] * soonest
        ) * (OVER_BUDGET_PENALTY if o.over_budget else 1)


def _only_best(options: list[Option], value, best) -> Option | None:
    """The single option holding the best value, or None when it's shared."""
    winners = [o for o in options if value(o) == best]
    return winners[0] if len(winners) == 1 else None


def _describe(options: list[Option], prefs: Preferences) -> None:
    compare = len(options) > 1
    if compare:
        low, high = min(o.price_kobo for o in options), max(o.price_kobo for o in options)
        if cheapest := _only_best(options, lambda o: o.price_kobo, low):
            cheapest.strengths.append(f"Cheapest: from {naira(low)}")
        if high > low * 1.05 and (priciest := _only_best(options, lambda o: o.price_kobo, high)):
            name = cheapest.business.name if cheapest else "the cheapest"
            priciest.tradeoffs.append(f"Priciest: from {naira(high)} vs {naira(low)} at {name}")

        located = [o for o in options if o.distance_km is not None]
        if len(located) > 1:
            near = min(o.distance_km for o in located)
            far = max(o.distance_km for o in located)
            if closest := _only_best(located, lambda o: o.distance_km, near):
                closest.strengths.append(f"Closest: {near:.1f} km away")
            if far - near >= 1 and (farthest := _only_best(located, lambda o: o.distance_km, far)):
                farthest.tradeoffs.append(f"Farthest: {far:.1f} km away")
        elif prefs.near:
            for o in options:
                if o.in_area:
                    o.strengths.append(f"In {o.business.area}")

        offering = [o for o in options if o.business.home_service]
        if not prefs.home_service and 0 < len(offering) < len(options):
            for o in options:
                if o.business.home_service:
                    fee = o.business.home_service_fee_kobo
                    o.strengths.append(f"Comes to you (home service {'+' + naira(fee) if fee else 'free'})")
                else:
                    o.tradeoffs.append("No home service")

        timed = [o for o in options if o.next_free]
        if len(timed) > 1:
            first = min(o.next_free for o in timed)
            if soonest := _only_best(timed, lambda o: o.next_free, first):
                soonest.strengths.append(f"Soonest: free {when_label(first)}")

        if prefs.need and (best := _only_best(options, lambda o: o.fit, max(o.fit for o in options))):
            best.strengths.append(f"Closest match for “{prefs.need}”")

    for o in options:
        if o.over_budget and prefs.budget_kobo is not None:
            o.tradeoffs.append(f"Above your {naira(prefs.budget_kobo)} budget")
        if o.next_free is None:
            o.tradeoffs.append(f"Not free on {prefs.day:%a %d %b}" if prefs.day else f"Fully booked for {SEARCH_DAYS} days")


def _summary(o: Option) -> str:
    if o.strengths and o.tradeoffs:
        return f"{o.strengths[0]}, but {o.tradeoffs[0][0].lower()}{o.tradeoffs[0][1:]}."
    if o.strengths:
        return "; ".join(o.strengths) + "."
    if o.tradeoffs:
        return o.tradeoffs[0] + "."
    return "A solid all-round option."


def option_view(o: Option, prefs: Preferences) -> dict[str, Any]:
    b = o.business
    return {
        "slug": b.slug,
        "name": b.name,
        "category": b.category,
        "area": b.area,
        "about": b.about,
        "profile_url": b.profile_url,
        "cover_photo": b.cover_photo,
        "matching_services": [
            {"id": s.id, "name": s.name, "price": naira(s.price_kobo), "duration": duration_label(s.duration_min)}
            for s in o.services[:3]
        ],
        "price_from": naira(o.price_kobo),
        "price_includes_home_service": prefs.home_service,
        "distance_km": round(o.distance_km, 1) if o.distance_km is not None else None,
        "home_service": {
            "offered": b.home_service,
            "fee": naira(b.home_service_fee_kobo) if b.home_service else None,
        },
        "next_available": when_label(o.next_free) if o.next_free else None,
        "next_available_start_time": o.next_free.isoformat() if o.next_free else None,
        "strengths": o.strengths,
        "tradeoffs": o.tradeoffs,
        "summary": _summary(o),
    }


def recommend(session: Session, prefs: Preferences) -> dict[str, Any]:
    words = keywords(prefs.need)
    origin = geo.geocode(prefs.near) if prefs.near else None
    options = [
        option
        for business in open_businesses(session)
        if (option := _candidate(session, business, prefs, words, origin)) is not None
    ]
    notes = []
    if prefs.near and origin is None:
        notes.append(f"Couldn't place “{prefs.near}” on a map, so distance is judged by area name only.")
    if not options:
        notes.append("No business on TuskApp matches that yet. Try fewer details or another area.")
    else:
        best_fit = max(o.fit for o in options)
        options = [o for o in options if o.fit >= best_fit * MIN_RELATIVE_FIT]
        if best_fit == 0:
            notes.append(
                "Nothing matched the request word for word; these are the closest kind of business. "
                "Check their services before recommending one."
            )
        _score(options, prefs)
        options.sort(key=lambda o: o.score, reverse=True)
        options = options[:MAX_OPTIONS]
        _describe(options, prefs)
    return {
        "options": [option_view(o, prefs) for o in options],
        "ranked_by": prefs.priority,
        "notes": notes,
    }
