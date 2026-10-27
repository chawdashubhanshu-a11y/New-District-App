# jojo

A going-out and lifestyle web app, loosely modelled on District by Zomato.
I built it for DVM Round 2 (Basic track) using Django and PostgreSQL.
Customers top up a wallet and book events. Organizations list their events,
check people in at the door, and keep an eye on how sales are going.

## Stack

- Django and PostgreSQL
- uv for packages
- Django groups for roles (`Customer` and `Organization`)

## Running it locally

1. Install Python, PostgreSQL and uv.
2. Create the database:

       psql -U postgres -c "CREATE DATABASE jojo;"

3. Make a `.env` file in the project root (next to `manage.py`):

       DB_NAME=jojo
       DB_USER=postgres
       DB_PASSWORD=your_password
       DB_HOST=localhost
       DB_PORT=5432
       SECRET_KEY=your_secret_key
       DEBUG=True

4. Install, migrate and start the server:

       uv sync
       uv run python manage.py migrate
       uv run python manage.py createsuperuser
       uv run python manage.py runserver

5. Open http://127.0.0.1:8000.

## Using the app

### Superuser

Log in at `/admin`. To set up an organization, add a user, tick the
`Organization` group, and fill in the organization profile at the bottom of
the same page. Organizations can't sign themselves up, which is deliberate.

### Customers

- Sign up at `/accounts/signup/`. You join the `Customer` group and get a
  wallet automatically.
- The wallet page has a fake "add money" form (no real payment happens) and
  a timestamped history of everything that went in or out.
- Open an event to book it. For ticket events you just book. For slot
  events you pick a slot.
- "My bookings" shows your active tickets, each with its own ID, and the
  ones that have already been used.

### Organizations

- After logging in you land on `/dashboard/`.
- You can create ticket events (price, start time, number of tickets) and
  slot events (a price, then slots with a start, end and capacity).
- The tickets page lists everything that's been bought, with the ticket ID,
  customer and time of purchase. You can filter by event, status or ticket
  ID, and press "Mark consumed" when someone arrives.
- The analytics page shows tickets sold, total revenue, how many have been
  used, and a breakdown per event.

## How the code is organised

- **accounts**: a custom `User` (extends `AbstractUser`) and
  `OrganizationProfile`, which is one-to-one with a user.
- **events**: `Event` (belongs to an organization, either `SLOT` or
  `TICKET`) and `Slot` (a time window with a capacity).
- **wallet**: `Wallet` (one per user) and `Transaction`, a ledger of every
  top-up and purchase.
- **bookings**: `Booking`, one row per ticket, with a UUID `ticket_id` and a
  status of `ACTIVE` or `CONSUMED`. The booking logic is in
  `bookings/services.py`.
- **dashboard**: everything organizations see: event creation, the ticket
  list, mark-as-consumed and analytics.

## Why I modelled it this way

- I used a custom user model from the start, because changing it later is
  painful.
- Roles are Django groups, as the task asked. A small decorator,
  `organization_required`, checks the group and the profile.
- Each ticket is its own `Booking` row. That gives every ticket a unique ID
  for check-in, without needing a separate ticket table.
- The wallet balance only ever changes together with a `Transaction` row, so
  the history always adds up.
- Money is stored as `DecimalField`, never floats.
- Bookings and transactions use `PROTECT` on their foreign keys, so you
  can't delete an event or user and wipe out financial history.
- Every organization query is filtered by the logged-in organization, so
  nobody can see another organization's events or tickets.

## Keeping money and tickets consistent

Booking runs inside `transaction.atomic()` and locks the wallet and the
event or slot row with `select_for_update()`. So if two people go for the
last ticket at the same moment, one gets it and the other sees "sold out",
and a double-click can't spend the same money twice. Marking a ticket as
consumed locks its row too, so a ticket can only be used once.

As a second safety net, the database itself has `CheckConstraint`s: the
balance can't go negative, tickets can't be oversold, and a slot can't end
before it starts.

## Not done yet

- Payment is a fake form, as the task allows.
- There's no refund flow. Revenue is simply the sum of what customers paid.

## Status

- Phase 1 (setup and user flow): done
- Phase 2 (organization dashboard): done
- Phase 3 (Docker and hosting): in progress