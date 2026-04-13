# Door App — MASTER ROADMAP

> Global offline-first QR interaction, queue, communication, and coordination platform.

---

## Architecture Overview

```
door-app/
├── door_backend/        # Django + DRF + Channels + Celery
├── door_web/            # Next.js 14 admin panel
└── door_mobile/         # Flutter cross-platform mobile
```

---

## Core Stack

| Layer          | Technology                              |
|----------------|-----------------------------------------|
| Backend API    | Django 4.2, DRF, drf-spectacular        |
| Real-time      | Django Channels 4, daphne, Redis        |
| Task queue     | Celery 5 + Redis broker                 |
| Database       | PostgreSQL 15                           |
| Local offline  | SQLite (Flutter sqflite), Hive          |
| Web admin      | Next.js 14, Tailwind, React Query       |
| Mobile         | Flutter 3.19, BLoC, go_router           |
| Push notif     | Firebase FCM                            |
| Auth           | Phone OTP + JWT (simplejwt)             |
| i18n           | Django Rosetta · next-intl · Flutter i18n (en/ar/ur) |

---

## Django App Structure

```
apps/
├── auth_identity/    OTP auth · User · UserDevice
├── organizations/    Organization · Member · Event
├── qr_engine/        QRCode · QRScan · ScanToken
├── queue_control/    Queue · QueueTicket  (+ WS consumer)
├── chat/             ChatRoom · Message   (+ WS consumer)
├── broadcast/        Channel · Message · Delivery  (+ WS + Celery)
├── sync/             SyncQueue · SyncSession · ConflictLog
├── audit/            AuditLog (auto via middleware)
└── notifications/    Notification (in-app)
```

---

## MVP Database Schema

### auth_identity
| Table            | Key Columns                                                     |
|------------------|-----------------------------------------------------------------|
| auth_users       | id(uuid) phone(unique) full_name role locale is_verified        |
| auth_otps        | id phone code expires_at used                                   |
| auth_user_devices| id user device_id fcm_token platform                           |

### organizations
| Table       | Key Columns                                             |
|-------------|----------------------------------------------------------|
| organizations| id name slug type owner locale is_active settings      |
| org_members | id organization user role joined_at                     |
| org_events  | id organization name starts_at ends_at status capacity  |

### qr_engine
| Table          | Key Columns                                                |
|----------------|------------------------------------------------------------|
| qr_codes       | id org event label payload_type payload_data scans_limit expires_at |
| qr_scans       | id qr_code scanned_by device_id location scanned_at       |
| qr_scan_tokens | id scan token status expires_at action_result             |

### queue_control
| Table         | Key Columns                                             |
|---------------|---------------------------------------------------------|
| queues        | id org event name max_capacity current_serving status   |
| queue_tickets | id queue user number status desk_number called_at       |

### chat
| Table               | Key Columns                                           |
|---------------------|-------------------------------------------------------|
| chat_rooms          | id org event type name                                |
| chat_room_members   | id room user is_admin last_read_at                    |
| chat_messages       | id room sender type content reply_to sent_at client_id|
| chat_message_statuses| id message user status                               |

### broadcast
| Table                  | Key Columns                                       |
|------------------------|---------------------------------------------------|
| broadcast_channels     | id org name type is_active                        |
| broadcast_subscriptions| id channel user is_muted                         |
| broadcast_messages     | id channel sender title body type payload sent_at |
| broadcast_deliveries   | id message user status delivered_at read_at       |

### sync
| Table          | Key Columns                                                   |
|----------------|---------------------------------------------------------------|
| sync_sessions  | id user device_id last_sync_at entity_types                   |
| sync_queue     | id user device_id operation entity_type entity_id client_id payload status sequence |
| sync_conflicts | id sync_queue_item entity_type server_version client_version resolution |

### audit
| Table      | Key Columns                                               |
|------------|-----------------------------------------------------------|
| audit_logs | id user org action entity_type entity_id payload ip_address created_at |

---

## REST API Map

| Method | Endpoint                                   | Description                  |
|--------|--------------------------------------------|------------------------------|
| POST   | /api/v1/auth/otp/request/                  | Send OTP                     |
| POST   | /api/v1/auth/otp/verify/                   | Verify OTP → JWT             |
| POST   | /api/v1/auth/token/refresh/                | Refresh JWT                  |
| GET/PATCH | /api/v1/auth/me/                        | Current user profile         |
| POST   | /api/v1/auth/devices/                      | Register device (FCM)        |
| CRUD   | /api/v1/organizations/                     | Organizations                |
| CRUD   | /api/v1/organizations/{id}/members/        | Org members                  |
| CRUD   | /api/v1/organizations/{id}/events/         | Org events                   |
| CRUD   | /api/v1/qr/codes/                          | QR codes                     |
| POST   | /api/v1/qr/scan/                           | Scan a QR → token            |
| POST   | /api/v1/qr/token/redeem/                   | Redeem scan token            |
| CRUD   | /api/v1/queues/                            | Queues                       |
| POST   | /api/v1/queues/{id}/call-next/             | Call next ticket             |
| POST   | /api/v1/queues/{id}/toggle/                | Open/pause/close queue       |
| CRUD   | /api/v1/queues/{id}/tickets/               | Tickets in queue             |
| CRUD   | /api/v1/chat/rooms/                        | Chat rooms                   |
| LIST   | /api/v1/chat/messages/                     | Messages (read-only HTTP)    |
| CRUD   | /api/v1/broadcast/channels/                | Broadcast channels           |
| POST   | /api/v1/broadcast/channels/{id}/subscribe/ | Subscribe                    |
| CRUD   | /api/v1/broadcast/messages/                | Send broadcast               |
| POST   | /api/v1/sync/upload/                       | Push offline ops             |
| POST   | /api/v1/sync/pull/                         | Pull server delta            |
| GET    | /api/v1/sync/conflicts/                    | List conflicts               |
| GET    | /api/v1/audit/                             | Audit logs                   |
| GET    | /api/v1/notifications/                     | Notifications                |
| POST   | /api/v1/notifications/mark-read/           | Mark all read                |

---

## WebSocket Flows

### Queue  `ws/queues/<id>/?token=JWT`
```
Client → Server:  { type: "join",   device_id: "..." }
Client → Server:  { type: "cancel" }

Server → Client:  { type: "queue.state",  data: QueueSerializer }
Server → Client:  { type: "ticket.called", data: { number, desk_number } }
Server → Client:  { type: "ticket.update", data: TicketSerializer }
Server → Client:  { type: "queue.status",  data: { status } }
```

### Chat  `ws/chat/<room_id>/?token=JWT`
```
Client → Server:  { type: "message.send", msg_type, content, client_id, reply_to }
Client → Server:  { type: "message.read", message_id }
Client → Server:  { type: "typing", is_typing }

Server → Client:  { type: "message.new",    data: ChatMessageSerializer }
Server → Client:  { type: "message.status", data: { message_id, status } }
Server → Client:  { type: "user.typing",    data: { user_id, name, is_typing } }
```

### Broadcast  `ws/broadcast/<channel_id>/?token=JWT`
```
Server → Client:  { type: "broadcast.message", data: { id, title, body, msg_type, payload } }
```

---

## Offline Sync Engine Design

```
┌────────────────────────────────────────────────────────────────┐
│  MOBILE/WEB CLIENT (offline-first)                             │
│                                                                │
│  User Action → Write to Local SQLite (sync_queue table)       │
│              → Apply optimistic UI update                      │
│                                                                │
│  On connectivity restore:                                      │
│    POST /sync/upload/  { device_id, operations: [...] }       │
│      ↓                                                         │
│    Server applies ops idempotently (client_id dedup)          │
│    Returns { applied, conflicts, errors }                      │
│      ↓                                                         │
│    POST /sync/pull/  { device_id, since, entity_types }       │
│    Receive delta → merge into local cache                      │
│                                                                │
│  Conflict strategy: server_wins by default                     │
│  ConflictLog stored for manual review                         │
└────────────────────────────────────────────────────────────────┘
```

Key rules:
- Every write carries a `client_id` (UUID) — server skips if already synced
- `sequence` number preserves client-side ordering
- `updated_at` on all models enables delta pull
- Soft-delete (`is_deleted`) instead of hard-delete for sync safety

---

## Flutter App Structure

```
lib/
├── main.dart
├── core/
│   ├── api/          api_client.dart (Dio + JWT auto-refresh)
│   ├── config/       env constants
│   ├── router/       app_router.dart (go_router)
│   ├── theme/        app_theme.dart
│   └── l10n/         en/ar/ur ARB files
├── features/
│   ├── auth/         login_screen · otp_screen · auth_repository
│   ├── qr/           qr_scanner_screen (mobile_scanner)
│   ├── queue/        queue_screen (WebSocket live updates)
│   ├── chat/         chat_room_screen (WebSocket)
│   ├── broadcast/    broadcast_screen (WebSocket)
│   └── sync/         sync_service.dart (SQLite queue + pull)
└── shared/
    ├── models/
    └── widgets/
```

---

## i18n / RTL / Multilingual

- **Django**: `USE_I18N=True`, LANGUAGE_CODE, `django-rosetta`, `.po` files in `locale/en|ar|ur/`
- **Next.js**: `next-intl`, JSON message files per locale, `dir="rtl"` on html tag for ar/ur
- **Flutter**: `flutter_localizations`, ARB files, `Directionality` widget wraps layout per locale

---

## MVP Phases

| Phase | Scope                                           | Status   |
|-------|-------------------------------------------------|----------|
| 0     | Scaffold, Docker, base models, auth             | ✅ Done   |
| 1     | QR engine + scan flow                          | ✅ Done   |
| 2     | Queue control + real-time WS                   | ✅ Done   |
| 3     | Chat (group + direct) + WS                     | ✅ Done   |
| 4     | Broadcast + FCM push + Celery                  | ✅ Done   |
| 5     | Offline sync engine (upload/pull/conflict)     | ✅ Done   |
| 6     | Audit logs + middleware                         | ✅ Done   |
| 7     | Next.js web admin (auth, dashboard, QR, queue) | ✅ Done   |
| 8     | Flutter mobile (scan, queue, chat, broadcast)  | ✅ Done   |
| 9     | i18n ar/ur RTL                                 | 🔜 Next  |
| 10    | n8n/webhook integration                        | 🔜 Next  |
| 11    | E2E tests + CI/CD                              | 🔜 Next  |

---

## Running Locally

```bash
# 1. Copy env
cp door_backend/.env.example door_backend/.env

# 2. Start services
docker-compose up -d db redis

# 3. Run backend
cd door_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 4. Run Channels (ASGI)
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# 5. Run Celery worker
celery -A config worker -l info

# 6. Web admin
cd ../door_web
npm install && npm run dev

# 7. Flutter
cd ../door_mobile
flutter pub get && flutter run
```

---

## Security Checklist (OWASP Top 10)

- [x] JWT + blacklist on rotation
- [x] OTP expiry (10 min) + one-time use
- [x] Sensitive fields stripped from audit payload
- [x] `ATOMIC_REQUESTS=True` for DB transactions
- [x] `AllowedHostsOriginValidator` on WebSocket
- [x] CORS locked down in production
- [x] HSTS + secure cookies in production settings
- [x] No passwords/secrets in audit logs
- [ ] Rate limiting on OTP endpoint (add `django-ratelimit`)
- [ ] Input validation on sync payload (add schema enforcement per entity)
