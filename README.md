# TuskApp

TuskApp puts Nigerian small businesses inside ChatGPT and Claude.

A customer asks their AI something like *"I'm moving into a new apartment in Uyo, where can I get furniture?"* and gets real local businesses with prices, photos and free times. From the same chat they can book, pay a deposit with Paystack, or get the seller's number.

Business owners sign up on the TuskApp dashboard, add their services, and see every booking, customer, question and payment that came in through chat. They can also connect their own AI and run the business by talking to it.

## Add TuskApp to your chat

There are two links. Use the customer one to try it out.

**Customer link** (no login):
`https://tuskapp-production.up.railway.app/mcp/customer/`

**Owner link** (log in with your dashboard email and password):
`https://tuskapp-production.up.railway.app/mcp/owner/`

### ChatGPT

1. Open **Settings → Security and login** and turn on **Developer mode**.
2. Open **Plugins** in the sidebar, click **+** next to the search box and choose **Add custom MCP server**.
3. Name it TuskApp and paste the link as the **Server URL**.
4. Set **Authentication** to **No Auth** for the customer link, or **OAuth** for the owner link.
5. Tick **I understand and want to continue**, then **Create**.
6. In a new chat, click **+** in the message box and choose **TuskApp**. Leave web search off, or ChatGPT may search the web instead.

Screenshots of each step are on the dashboard at `/connect`.

### Claude

1. Open **Settings → Connectors → Add custom connector**.
2. Give it a name (TuskApp) and paste the link.
3. Click **Add**. The owner link opens the TuskApp sign-in page; the customer link connects straight away.
4. In a new chat, open the tools menu, make sure TuskApp is on, and turn off web search for the demo.

### Things to try

- "I'm relocating to a new apartment in Uyo, where can I get furniture?"
- "I need a plumber in Abuja to fix a leaking pipe."
- "Book the mahogany dining table and send me the payment link."
- "Give me the seller's number, I want to talk to him."

With the owner link connected:

- "What's booked this week?"
- "Block next Friday, I'm travelling."
- "Change the wardrobe price to 500k."

Paystack is in test mode. Pay with card `4084 0840 8408 4081`, CVV `408`, any future expiry, PIN `0000`, OTP `123456`.

## How it works

1. The customer's AI calls TuskApp tools such as `find_businesses`, `create_booking` and `contact_business`.
2. The backend saves the customer and booking, creates a Paystack link for the deposit and alerts the business.
3. When Paystack confirms the payment, the booking is confirmed and the business is alerted again.
4. The business sees everything on the dashboard.

The repo has two apps:

- `tusk-mcp/` is the Python backend: both MCP servers, the dashboard API and payments.
- `tusk-dashboard/` is the Next.js website: sign-up, the dashboard and a public page for each business.

## Where MSFLib is used

TuskApp is built on MSFLib. TuskApp's own code covers services, bookings, recommendations and the chat tools. MSFLib handles the parts every product needs:

- **Accounts and login.** Sign-up, passwords, login tokens and logout for business owners. The dashboard's login endpoints are MSFLib's own. (`api/router.py`, `api/deps.py`)
- **Businesses.** Each business is an MSFLib workspace, and its settings (deposit, opening hours) are MSFLib workspace config. (`services/business.py`)
- **Owner AI sign-in.** The tokens behind the owner link are MSFLib tokens, and the sign-in page checks passwords with MSFLib. (`services/tokens.py`, `servers/oauth.py`)
- **Payments.** Paystack deposits run through MSFLib payments. When a payment clears, MSFLib's event bus tells TuskApp to confirm the booking. (`services/payments.py`, `listeners.py`)
- **Notifications.** Alerts like "New booking confirmed" or "Customer wants to talk" are MSFLib notifications: the dashboard bell, plus email and SMS when they're set up. (`services/notify.py`)
- **Chat history.** Each customer's chat is saved as an MSFLib conversation, so the owner can read it. (`services/chats.py`)
- **Uploads.** Service photos are checked and stored by MSFLib storage. (`api/routes.py`)
- **Database and settings.** All tables use MSFLib's model base, and all `.env` settings are MSFLib settings classes. (`models/`, `core/config.py`)

All paths are inside `tusk-mcp/tusk_mcp/`.

## Run it locally

Backend (needs access to the private MSFLib repo):

```powershell
cd tusk-mcp
poetry install
copy .env.example .env
poetry run python -m tusk_mcp.app
```

Dashboard:

```powershell
cd tusk-dashboard
npm install
npm run dev
```

In `tusk-dashboard/.env.local`, set `TUSK_API_URL` to the backend URL (`http://127.0.0.1:8100` locally) and `NEXT_PUBLIC_SITE_URL` to the dashboard URL.

Run the backend tests with `poetry run pytest` inside `tusk-mcp`.

## Deploy

- **Backend on Railway**, root `tusk-mcp`. Add `GITHUB_TOKEN` so the build can install MSFLib, and attach a volume at `/data`, or the database and photos are wiped on every deploy.
- **Dashboard on Vercel**, root `tusk-dashboard`. Set `TUSK_API_URL` to the Railway URL and `NEXT_PUBLIC_SITE_URL` to the Vercel URL.
- **Paystack**: put the secret key in `PAYSTACK_SECRET_KEY` on Railway and set the webhook to `https://<railway-url>/pay/webhook`.
