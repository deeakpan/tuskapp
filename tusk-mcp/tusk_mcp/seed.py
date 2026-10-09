"""Demo data for an empty database: two businesses with owner logins and owner MCP tokens.

`python -m tusk_mcp.seed` prints the demo owner MCP tokens (they depend on SECRET_KEY).
"""

from datetime import time

from msflib.core.security import create_access_token
from sqlmodel import Session, select

from tusk_mcp.actions import account_action
from tusk_mcp.core.config import settings
from tusk_mcp.models import AccountCreate, Service
from tusk_mcp.services import business as biz
from tusk_mcp.services.tokens import OWNER_MCP_SCOPE, issue_mcp_token

DEMO_PASSWORD = "tusk-demo-123"
DEMO_OWNERS = {"glam-by-tolu": "tolu@tuskapp.demo", "mama-put-kitchen": "mama@tuskapp.demo"}
DEMO_PROFILES = {
    "glam-by-tolu": {
        "about": (
            "Protective styles for natural hair, done neat and on time. Known for knotless braids that last "
            "6–8 weeks and silk presses without heat damage. Popular with brides, students and busy "
            "professionals; quiet studio with Wi-Fi and a waiting area, 5 minutes from Yaba bus stop."
        ),
        "whatsapp": "08030000001",
    },
    "mama-put-kitchen": {
        "about": (
            "Home-style Yoruba and Nigerian party food, cooked fresh every morning. Best for office lunches, "
            "family trays and small parties. Our jollof is smoky party jollof; amala is soft and served hot. "
            "Generous portions, spice level on request, delivery in Surulere and Yaba."
        ),
        "whatsapp": "08030000002",
    },
}


def _owner(session: Session, name: str, email: str, phone: str):
    return account_action.create(
        session,
        data=AccountCreate(
            email=email,
            phone=biz.account_phone(phone),
            password=DEMO_PASSWORD,
            data={"kind": "owner"},
            profile=biz.profile_for(name),
        ),
        commit=False,
    )


def _demo_jti(slug: str) -> str:
    return f"demo-{slug}"


def demo_owner_token(slug: str, workspace_id: int) -> str:
    return create_access_token(
        DEMO_OWNERS[slug],
        settings.SECRET_KEY,
        None,
        claims={"scope": OWNER_MCP_SCOPE, "workspace_id": workspace_id, "jti": _demo_jti(slug)},
    )


DEMO_LOCATIONS = {"glam-by-tolu": (6.5095, 3.3711), "mama-put-kitchen": (6.4969, 3.3540)}

# Phone vendors in Uyo with different prices, locations and home service, so recommendations have
# real trade-offs to explain. Coordinates are approximate.
UYO_VENDORS = [
    {
        "owner": ("Ini Okon", "gadgethub@tuskapp.demo", "08030000011"),
        "name": "Gadget Hub Uyo",
        "area": "Uyo, Akwa Ibom",
        "address": "45 Ikot Ekpene Road, Uyo",
        "location": (5.0452, 7.9101),
        "about": "Tested UK-used and brand-new iPhones and Samsungs. Every phone is checked for battery health "
        "and iCloud lock, and comes with a 3-month warranty. Walk-ins welcome; we also buy and swap phones.",
        "items": [("iPhone 13 Pro 128GB (UK used)", 450_000), ("iPhone 13 Pro 256GB (UK used)", 520_000)],
        "home_service_fee": None,
    },
    {
        "owner": ("Anietie Udo", "anyi@tuskapp.demo", "08030000012"),
        "name": "Anyi Gadgets",
        "area": "Itam, Uyo",
        "address": "Itam Market Road, Itam, Uyo",
        "location": (5.0702, 7.8759),
        "about": "Premium phone shop in Itam. Clean UK-used iPhones with 85%+ battery, screen protector and "
        "case included. Quick pickup near Itam Market.",
        "items": [("iPhone 13 Pro 128GB (UK used)", 470_000), ("iPhone 12 Pro 128GB (UK used)", 360_000)],
        "home_service_fee": None,
    },
    {
        "owner": ("Paul Effiong", "paul@tuskapp.demo", "08030000013"),
        "name": "Paul Phones",
        "area": "Ewet Housing, Uyo",
        "address": "12 Osongama Road, Ewet Housing, Uyo",
        "location": (5.0121, 7.9452),
        "about": "Budget-friendly UK-used phones. Lowest prices in Uyo, every phone tested in front of you. "
        "No warranty on discounted stock.",
        "items": [("iPhone 13 Pro 128GB (UK used)", 430_000), ("iPhone 11 128GB (UK used)", 240_000)],
        "home_service_fee": None,
    },
    {
        "owner": ("Charles Bassey", "charles@tuskapp.demo", "08030000014"),
        "name": "Charles Mobile",
        "area": "Uyo, Akwa Ibom",
        "address": "Aka Road, Uyo",
        "location": (5.0398, 7.9002),
        "about": "We bring the phone to you: home and office delivery anywhere in Uyo, with setup and data "
        "transfer from your old phone. Brand-new and UK-used iPhones.",
        "items": [("iPhone 13 Pro 128GB (UK used)", 480_000), ("iPhone 14 Pro 128GB (UK used)", 640_000)],
        "home_service_fee": 3_000,
    },
]


def _seed_uyo_vendors(session: Session) -> None:
    for vendor in UYO_VENDORS:
        name, email, phone = vendor["owner"]
        if account_action.get_by_email(session, email=email):
            continue
        business = biz.create_business(
            session,
            _owner(session, name, email, phone),
            vendor["name"],
            category="phones",
            area=vendor["area"],
            address=vendor["address"],
            about=vendor["about"],
            whatsapp=phone,
            location=vendor["location"],
            deposit_kobo=2_000_000,
            home_service_fee_kobo=vendor["home_service_fee"] * 100 if vendor["home_service_fee"] is not None else None,
            policies=["Deposit holds the phone for you until pickup; it's deducted from the price."],
            hours=[(day, time(9), time(19)) for day in range(6)],
        )
        for item, price in vendor["items"]:
            biz.add_service(session, business, item, price * 100, 30, "Inspect and collect in store")
    session.commit()


def _backfill_profiles(session: Session) -> None:
    """Demo databases made before businesses had an `about` get the demo text."""
    for slug, profile in DEMO_PROFILES.items():
        business = biz.business_by_slug(session, slug)
        if "·" in business.about or not business.about:
            biz.update_profile(session, business, **profile)
        if business.location is None:
            lat, lng = DEMO_LOCATIONS[slug]
            business.workspace.data = {**(business.workspace.data or {}), "lat": lat, "lng": lng}
            session.add(business.workspace)
    # Services used to be created with a generated placeholder photo; only uploaded photos are kept now.
    for service in session.exec(select(Service)):
        real = [url for url in service.photo_urls if not url.startswith(biz.PLACEHOLDER_PHOTO)]
        if real != service.photo_urls:
            service.photo_urls = real
            session.add(service)
    session.commit()


def seed_demo(session: Session) -> bool:
    if account_action.get_by_email(session, email=DEMO_OWNERS["glam-by-tolu"]):
        _backfill_profiles(session)
        _seed_uyo_vendors(session)
        return False

    tolu = _owner(session, "Tolu Adebayo", DEMO_OWNERS["glam-by-tolu"], "08030000001")
    glam = biz.create_business(
        session,
        tolu,
        "Glam by Tolu",
        category="salon",
        area="Yaba, Lagos",
        address="12 Herbert Macaulay Way, Yaba, Lagos",
        **DEMO_PROFILES["glam-by-tolu"],
        location=DEMO_LOCATIONS["glam-by-tolu"],
        deposit_kobo=500_000,
        home_service_fee_kobo=700_000,
        policies=[
            "Open Tuesday to Saturday, 9am to 7pm. Closed Sunday and Monday.",
            "A ₦5,000 deposit is needed to book.",
            "No refunds for no-shows.",
            "Home service in Yaba and Surulere only, +₦7,000.",
        ],
        hours=[(day, time(9), time(19)) for day in range(1, 6)],
    )
    for name, price, minutes, description in [
        ("Knotless braids (medium)", 35_000, 300, "Medium knotless box braids"),
        ("Knotless braids (small)", 45_000, 420, "Small knotless box braids"),
        ("Cornrows", 8_000, 90, "Straight-back or patterned cornrows"),
        ("Wig installation", 15_000, 120, "Frontal or closure wig install"),
        ("Silk press", 12_000, 120, "Wash, blow-dry and silk press"),
    ]:
        biz.add_service(session, glam, name, price * 100, minutes, description)

    mama = _owner(session, "Mama Put", DEMO_OWNERS["mama-put-kitchen"], "08030000002")
    kitchen = biz.create_business(
        session,
        mama,
        "Mama Put Kitchen",
        category="restaurant",
        area="Surulere, Lagos",
        address="5 Adeniran Ogunsanya Street, Surulere, Lagos",
        **DEMO_PROFILES["mama-put-kitchen"],
        location=DEMO_LOCATIONS["mama-put-kitchen"],
        home_service_fee_kobo=150_000,
        policies=["Open every day, 10am to 9pm.", "Delivery within Surulere ₦1,500, Yaba ₦2,500."],
        hours=[(day, time(10), time(21)) for day in range(7)],
    )
    for name, price, minutes, description in [
        ("Jollof rice + chicken", 3_500, 30, "Party jollof with fried chicken"),
        ("Fried rice + turkey", 4_500, 30, "Fried rice with peppered turkey"),
        ("Amala + ewedu + gbegiri", 2_500, 30, "With assorted meat"),
        ("Pounded yam + egusi", 3_000, 30, "With beef or fish"),
    ]:
        biz.add_service(session, kitchen, name, price * 100, minutes, description)

    for business, owner in ((glam, tolu), (kitchen, mama)):
        issue_mcp_token(session, business, owner, "Demo token", jti=_demo_jti(business.slug), expires=False)
    session.commit()
    _seed_uyo_vendors(session)
    return True


def main() -> None:
    from tusk_mcp.db.session import session_scope

    with session_scope() as session:
        for slug in DEMO_OWNERS:
            business = biz.business_by_slug(session, slug)
            print(f"{slug}: {demo_owner_token(slug, business.id)}")


if __name__ == "__main__":
    main()
