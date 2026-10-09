# TuskApp — Put any business inside ChatGPT
> Built for **KodeHauz @ 10 — The Decennium Sprint** on top of **MSFLib**.

---

## 1. One-liner

**TuskApp lets any Nigerian business — a salon, restaurant, clinic, tailor, school, car dealer — become a ChatGPT/Claude app in 5 minutes, so customers can ask questions, see prices and photos, and book or order without leaving the chat.**

---

## 2. The problem

- Nigerian customers already live in **WhatsApp, Instagram and ChatGPT**. They don't download business apps and rarely use business websites.
- Small businesses answer the **same questions all day** on WhatsApp: "How much?", "Are you open Sunday?", "Do you deliver to Lekki?", "Is 2pm free?". Replies are slow, prices are inconsistent, bookings get lost in chats.
- Big brands can afford custom ChatGPT apps. **A salon in Yaba can't.** There is no "Shopify for ChatGPT".

## 3. The solution

A platform where a business owner:

1. Signs up and creates their business.
2. Uploads what they **already have** — a price-list photo, a menu PDF, FAQs, opening hours, photos of their work.
3. TuskApp turns it into structured, searchable business data (services, prices, hours, policies, photos).
4. The business gets a **ChatGPT/Claude link** to share: *"Find us on ChatGPT"*.

Customers then talk to the business **inside ChatGPT or Claude**, and every booking/order lands in the owner's dashboard instantly.

---

## 4. Real example — "Glam by Tolu", a salon in Yaba

### 4.1 Owner onboarding (5 minutes)

Tolu runs a hair salon. Today she answers 60+ WhatsApp messages a day.

1. Tolu signs up on the TuskApp dashboard and creates **"Glam by Tolu"**.
2. She uploads:
   - a **photo of her price list** (the one taped to her mirror),
   - **6 photos** of her best styles,
   - a short note: *"Open Tue–Sat 9am–7pm. ₦5,000 deposit to book. No refunds for no-shows. Home service in Yaba/Surulere only, +₦7,000."*
3. TuskApp reads the price list and shows a **review screen**:

   | Service | Price | Duration |
   |---|---|---|
   | Knotless braids (medium) | ₦35,000 | 5 hrs |
   | Knotless braids (small) | ₦45,000 | 7 hrs |
   | Cornrows | ₦8,000 | 1.5 hrs |
   | Wig installation | ₦15,000 | 2 hrs |
   | Silk press | ₦12,000 | 2 hrs |

   Tolu fixes one price, attaches photos to services, and clicks **Publish**.
4. She sets her deposit amount; deposits are collected through **Paystack** (see section 10 for how money flows).
5. She gets her link and posts on Instagram: *"You can now book Glam by Tolu on ChatGPT 💇🏾‍♀️"*.

### 4.2 Customer conversation in ChatGPT

> **Ada:** Find me a salon in Yaba that does knotless braids, what are the prices?
>
> *(ChatGPT calls `find_businesses` → `list_services`)*
>
> **ChatGPT:** Glam by Tolu in Yaba does knotless braids:
> 🖼️ *[card with photo]* **Knotless braids (medium)** — ₦35,000 · ~5 hrs
> 🖼️ *[card with photo]* **Knotless braids (small)** — ₦45,000 · ~7 hrs
> They're open Tue–Sat, 9am–7pm. A ₦5,000 deposit is needed to book.
>
> **Ada:** Is Saturday morning free for medium?
>
> *(ChatGPT calls `check_availability`)*
>
> **ChatGPT:** Saturday 11 Oct has **9:00am** and **10:00am** free (a 5-hour style needs to start by 2pm).
>
> **Ada:** Book 9am. Can she come to my place in Surulere?
>
> *(ChatGPT calls `ask_business` → policy says home service is available in Surulere for +₦7,000; then `create_booking`)*
>
> **ChatGPT:** Yes — home service in Surulere is +₦7,000, so the total is **₦42,000**.
> I've reserved **Sat 11 Oct, 9:00am**. Pay the ₦5,000 deposit here to confirm: **[Pay with Paystack]**
> The slot is held for 30 minutes.
>
> *(Ada pays → Paystack redirects to TuskApp's "payment complete" page → TuskApp verifies the payment with Paystack → booking confirmed)*
>
> **ChatGPT:** ✅ Confirmed! Booking ref **GBT-0412**. Tolu will see you Saturday at 9am.

### 4.3 What Tolu sees

- 🔔 In-app notification on her dashboard **plus an SMS/email**: **"New booking: Ada — Knotless (medium), home service Surulere, Sat 9:00am. Deposit ₦5,000 paid."**
- The booking appears on her dashboard calendar.
- Weekly insight: *"Knotless braids were asked about 41 times this week; 12 people asked about Sunday — consider opening Sundays."*

### 4.4 Tolu manages her business from Claude/ChatGPT too (owner mode)

> **Tolu:** What bookings do I have tomorrow?
> **Tolu:** Raise silk press to ₦14,000.
> **Tolu:** Block next Friday, I'm travelling.
> **Tolu:** Who hasn't paid their balance this week?

### 4.5 Second example — "Mama Put Kitchen", Surulere (food)

- Uploads a menu photo + "Delivery within Surulere ₦1,500, Yaba ₦2,500. Closes 9pm."
- Customer in ChatGPT: *"What's on Mama Put's menu today and can I get jollof + chicken delivered to Yaba?"* → sees menu cards with food photos, gets total with delivery, pays via Paystack link, order lands on the kitchen dashboard.

Same platform, different business type — that's the point.

---

## 5. Users & roles

| Role | Who | What they do |
|---|---|---|
| **Owner** | Business owner | Sets up business, uploads data, connects Paystack, sees bookings/insights |
| **Staff** | Stylists, waiters, receptionists | See and manage bookings/orders, update availability |
| **Customer** | Anyone in ChatGPT/Claude | Asks questions, sees prices/photos, books/orders, pays deposits — **no account needed** |
| **Platform admin** | Us | Moderation, support |

---

## 6. Features

### MVP (hackathon)

- Owner sign-up, login, create business (multi-tenant).
- Upload price list / menu (image or PDF) → AI extracts services → **owner reviews before publishing**.
- Upload photos and attach to services.
- Opening hours + simple availability rules.
- Free-text policies (deposit, refunds, delivery areas) → answered by AI from the business's own data only.
- **Customer MCP**: find business, list services (with images), check availability, ask a question, create booking.
- **Owner MCP**: today's bookings, update price, block dates.
- Paystack test-mode deposit link (MSFLib `payments`) → payment verified → booking confirmed.
- Notifications to owner on new booking (in-app + email/SMS).
- Every customer chat saved as a conversation the owner can read (MSFLib `conversation`).
- Dashboard: services, bookings, simple stats.

### Later

- Orders + delivery (Shipbubble).
- WhatsApp channel using the same business brain.
- Multi-branch businesses.
- Reviews and ratings.
- Owner mobile app (Flutter).
- OAuth "Sign in with TuskApp" for customers (saved details, booking history).

---

## 7. How MSFLib powers it (the "meaningful use")

| MSFLib module | What it does in TuskApp |
|---|---|
| `core` | Config, database conventions, event bus (`booking.created`, payment fulfilment events), scopes, seeding |
| `tenancy` | The platform tenant every business belongs to (single default tenant for now) |
| `auth` | Owner/staff login (JWT), password reset, Google login, token revocation; tokens for the owner MCP |
| `account` | Owner and staff accounts and profiles; lightweight customer accounts for payments |
| `workspaces` | **Each business is a workspace** — complete data isolation between businesses, staff membership and roles |
| `workspace_config` | Per-business settings: hours, deposit amount, booking rules, AI tone, delivery fees |
| `payments` | Paystack deposit checkout, payment records, verification, and a fulfilment event that confirms the booking |
| `conversation` | Every customer chat stored as a conversation in the business's workspace (user + agent turns), so the owner can read what customers asked and pick up unanswered questions |
| `drivelink` | Virtual file storage for uploaded price lists, menus and service photos |
| `documents` | Upload of price lists, menus, PDFs; extraction + chunking + indexing |
| `ingestion` | Background jobs (Celery + Redis) that process uploads without blocking the app |
| `knowledge` | Services, prices, durations, policies and FAQs as **structured facts with evidence** (which upload each fact came from) |
| `ai_core` | LLM + embeddings (vision model reads price-list photos), vector search, usage tracking and rate limits |
| `ai_api` | Grounded Q&A ("Do you do home service in Surulere?") answered **only** from that business's data |
| `notifications` / `workspace_notifications` | "New booking", "Deposit paid", "Slot cancelled" to owner and staff — in-app, email or SMS |

**Frontend stack:**

| MSFLib layer | Use |
|---|---|
| **React** workspace | Owner dashboard (onboarding, review screen, calendar, stats) |
| **TypeScript** utils | Shared helpers (money formatting in kobo/naira, dates, API client) |
| **Flutter** (`kh_core`, `kh_theme`, `kh_ui`, `kh_screens`) | Owner mobile app — booking notifications and calendar (stretch goal) |

---

## 8. Architecture

```text
 Customer in ChatGPT / Claude            Owner in ChatGPT / Claude
            │  (public tools)                   │  (token-protected tools)
            ▼                                   ▼
   ┌───────────────────────────────────────────────────────────┐
   │           FastAPI app built on MSFLib                     │
   │                                                           │
   │   /mcp/customer   ← FastMCP (customer tools)              │
   │   /mcp/owner      ← FastMCP (owner tools, auth required)  │
   │   /api/v1/...     ← REST for dashboard (MSFLib routers)   │
   │   /pay/complete   ← Paystack redirect → verify payment    │
   │                                                           │
   │   tenancy · auth · account · workspaces · workspace_config│
   │   payments · conversation · drivelink                     │
   │   documents · ingestion · knowledge · ai_core · ai_api    │
   │   notifications                                           │
   └───────────────┬───────────────────────────┬───────────────┘
                   │                           │
            PostgreSQL + pgvector        Redis + Celery worker
                                          (upload processing)
                   ▲
                   │ REST
        React owner dashboard  ·  Flutter owner app (stretch)

 External: Paystack (test mode) · LLM provider · email/SMS provider
```

---

## 9. MCP design

### 9.1 Two MCP servers, one backend

| Server | Who | Auth | Tools |
|---|---|---|---|
| **Customer MCP** `/mcp/customer` | Anyone | None for browsing; name + phone to book | `find_businesses`, `get_business`, `list_services`, `check_availability`, `ask_business`, `create_booking`, `get_booking` |
| **Owner MCP** `/mcp/owner` | Owner/staff | Token from dashboard (MSFLib auth) | `list_bookings`, `update_service`, `block_dates`, `get_insights`, `cancel_booking` |

Each business also gets a **shareable scoped link** (e.g. `/mcp/customer?b=glam-by-tolu`) so the chat starts already "inside" that business.

### 9.2 Customer tools (sketch)

| Tool | Input | Output |
|---|---|---|
| `find_businesses` | `query`, `area?`, `category?` | List of businesses with name, area, category, cover photo |
| `get_business` | `slug` | Hours, address, policies summary, photos |
| `list_services` | `slug`, `query?` | Services with price (₦), duration, photo URLs |
| `check_availability` | `slug`, `service_id`, `date` | Free start times |
| `ask_business` | `slug`, `question` | Answer grounded in the business's knowledge + source |
| `create_booking` | `slug`, `service_id`, `start_time`, `name`, `phone`, `notes?` | Booking ref, total, Paystack deposit link, hold expiry |
| `get_booking` | `ref`, `phone` | Status (held / confirmed / cancelled) |

### 9.3 Guardrails

- AI answers **only** from the business's published data; if unknown → "I'll ask Tolu" (creates an enquiry notification).
- Prices always come from the database, never from the model.
- Bookings are **held** until the deposit payment is verified; holds expire automatically.
- Every MCP tool call is logged per workspace (audit + insights).

### 9.4 Images and rich cards

- **ChatGPT:** supports rich UI from MCP servers via the **Apps SDK / MCP Apps** (custom components rendered in the chat — cards, carousels, images, buttons).
- **Claude:** renders images from MCP tool results and supports **MCP Apps** UI as well.
- **Fallback (works everywhere):** tool results include image URLs and markdown, so even plain clients show links/photos.

For the demo: a **service card carousel** (photo, name, price, duration, "Book" button).

### 9.5 Connecting

- **Hackathon:** expose the backend with **ngrok / Cloudflare Tunnel** (ChatGPT needs a public HTTPS URL).
- **ChatGPT:** Settings → Developer mode → add connector → paste Customer MCP URL (no auth).
- **Claude Desktop / Claude Code:** add the URL; owner MCP with `Authorization: Bearer <token>` header.
- **Later:** full OAuth so owners can connect the owner MCP in ChatGPT/Claude.ai.

---

## 10. Payments — using MSFLib `payments`

### How the module works

- `process_payment(...)` creates a Paystack checkout and returns an `authorization_url` (the "Pay with Paystack" link), stores a `Payment` record, and a `PaymentQueue` row holding our booking data.
- Verification is **pull-based** (no webhooks): after paying, Paystack redirects the customer to our callback URL; we verify the reference with Paystack.
- On success MSFLib fires `payment-queue-execute-{event_key}` on the event bus → our listener confirms the booking and triggers notifications.
- It also checks the paid amount matches the expected amount.

### The flow in TuskApp

1. `create_booking` (MCP tool) → booking **held** → `process_payment(..., queue_event_key="booking-deposit", queue_data={"booking_ref": "GBT-0412"})` → return the Paystack link to ChatGPT.
2. Customer pays → Paystack redirects to `/pay/complete?reference=...`.
3. We verify → `payment-queue-execute-booking-deposit` fires → listener marks booking **confirmed** → notification to owner/staff.
4. Customer asks ChatGPT "is my booking confirmed?" → `get_booking` shows **confirmed**.

### Gaps to handle (from MSFLib's own docs)

| Gap | What we do |
|---|---|
| A payment must belong to an **account**, and the built-in verify route only works for the logged-in payer | Create a lightweight **customer account** from name + phone/email at booking time, and verify through our own `/pay/complete` endpoint using the module's `PaymentProcessor` instead of the built-in route |
| **One Paystack key for the whole app** — money lands in the platform's Paystack balance | Hackathon: fine in **test mode**. Production: per-business Paystack keys (stored per workspace) or Paystack **subaccounts/split payments** so money settles **directly to each business** and TuskApp never holds funds — this needs a small extension to the module |
| No webhooks, refunds or subscriptions | Callback-based verification is enough for deposits; refunds handled manually by the business for now |

- **Hackathon:** Paystack **test mode** + test cards.

---

## 11. Data model (first pass)

| Table | Key fields |
|---|---|
| `Workspace` (business) — MSFLib | name, slug, category, area, address, cover photo |
| `WorkspaceUser` — MSFLib | account, workspace, role (owner / staff) |
| `Service` | workspace_id, name, description, price_kobo, duration_min, photo_urls, is_published, source_document_id |
| `AvailabilityRule` | workspace_id, weekday, open_time, close_time |
| `BlockedSlot` | workspace_id, start, end, reason |
| `Booking` | workspace_id, ref, service_id, start, end, customer_account_id, customer_name, customer_phone, total_kobo, deposit_kobo, status, payment_id, hold_expires_at |
| `Payment` / `PaymentQueue` — MSFLib | Paystack reference, amount, status, booking data for fulfilment |
| Conversations / messages — MSFLib | Each customer chat with a business, user + agent turns |
| `Enquiry` | workspace_id, question, customer_phone, status |
| `McpCallLog` | workspace_id, server, tool, arguments, status, duration_ms, created_at |
| Documents / knowledge — MSFLib | uploads, extracted facts, policies |
| Config — MSFLib `workspace_config` | deposit, hours, booking rules, AI tone |

---

## 12. Demo script (3 minutes)

1. **The pain (20s):** show a real WhatsApp screenshot of 50 unanswered "how much?" messages.
2. **Onboard live (60s):** create "Glam by Tolu", upload the price-list photo → services appear → fix one price → Publish.
3. **Customer in ChatGPT (60s):** "Knotless braids in Yaba, Saturday morning?" → service cards with photos → book 9am → pay deposit (Paystack test card).
4. **Owner side (30s):** dashboard + notification pops: *"New booking — Ada, Sat 9am, deposit paid."* Then in Claude: *"What bookings do I have Saturday?"*
5. **Close (10s):** *"Every business in Nigeria can now be on ChatGPT — in 5 minutes, built on MSFLib."*

---

## 13. Hackathon build plan

| Block | Work |
|---|---|
| Setup | MSFLib FastAPI template running (auth, account, workspaces), Postgres, Redis, ngrok |
| Backend core | `Service`, `AvailabilityRule`, `Booking` models + actions; availability calculation |
| AI pipeline | Upload → documents/ingestion → vision extraction → review → knowledge |
| MCP | Customer MCP tools, then owner MCP; mount in FastAPI; test in Claude, then ChatGPT |
| Payments | MSFLib `payments` + Paystack test key; `/pay/complete` verify endpoint; fulfilment listener confirms booking |
| Dashboard | React: onboarding, review screen, bookings list, notifications |
| Polish | Service card UI in ChatGPT, seed 2–3 demo businesses, rehearse demo |

**Team split suggestion:** 1 on backend + MCP, 1 on AI pipeline (documents/knowledge), 1 on React dashboard, 1 on payments + demo/pitch.

---

## 14. Risks & open questions

| Risk | Mitigation |
|---|---|
| MSFLib repos are private | Confirm GitHub access with organisers before the event |
| `payments` module ties payments to accounts and uses one platform Paystack key | Lightweight customer accounts + own verify endpoint; per-business keys/subaccounts in production (section 10) |
| MSFLib modules have documented known issues (settings env-var style, tenant slug) | Keep default tenant slug `default`; use flat env var names (`PAYSTACK_SECRET_KEY`) with subclassed settings |
| Price-list photo extraction mistakes | Owner **review screen** before publishing; prices only from DB |
| ChatGPT connector needs public HTTPS + paid plan | ngrok/Cloudflare Tunnel; Claude Desktop as backup demo client |
| Rich UI (Apps SDK) takes time | Ship plain text + image URLs first, add card UI if time allows |
| Celery/Redis setup on the day | Docker Compose ready in advance |
| Customer spam bookings | Deposit required to confirm; holds expire |

---

## 15. Pitch lines

- *"Nigerians don't visit websites. They chat. So we put businesses where the chat is."*
- *"Shopify gave every business a website. TuskApp gives every business a ChatGPT app."*
- *"Upload your price list photo, and in five minutes customers can book you from ChatGPT."*
- *"MSFLib isn't a dependency here — it's the engine: every business is a workspace, every price list becomes knowledge, every answer is grounded."*
