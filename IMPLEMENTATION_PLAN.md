# PIXEL NOTES - SECRET CHAT MODE
## Complete Production Implementation Plan

**Version:** v0.1-ALPHA  
**Owner:** Pixel Solusindo

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLOUDFLARE TUNNEL                        │
│                                                                  │
│  note.pixelsolusindo.space ──────► Frontend (Flutter Web:94837) │
│  api94837.pixelsolusindo.space ──► Backend (FastAPI:94838)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DOCKER NETWORK                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Frontend   │  │   Backend    │  │    Redis     │          │
│  │  Flutter Web │  │   FastAPI    │  │  (Ephemeral) │          │
│  │   :94837     │  │   :94838     │  │    :6379     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  NO PUBLIC IP | NO PORT FORWARDING | INTERNAL NETWORK ONLY      │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features:
- **Surface App:** Simple Notes application (CRUD operations)
- **Hidden Feature:** Secret Chat Mode accessible via hidden symbol
- **Security:** AES-256-GCM encryption, JWT auth, rate limiting
- **Ephemeral:** All chat messages auto-delete after 24 hours (Redis TTL)

---

## 2. FOLDER STRUCTURE

```
pixelnotes/
├── docker-compose.yml           # Main orchestration file
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── masterplan.txt               # Original project specification
│
├── backend/                     # FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI application entry
│       ├── config.py            # Settings from .env
│       ├── auth.py              # JWT & password handling
│       ├── encryption.py        # AES-256-GCM encryption
│       ├── models.py            # Pydantic models
│       ├── redis_client.py      # Redis operations
│       └── routes/
│           ├── __init__.py
│           ├── auth.py          # /api/auth/* endpoints
│           ├── chat.py          # /api/chat/* endpoints
│           └── notes.py         # /api/notes/* endpoints
│
├── frontend/                    # Flutter Web Frontend
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── pubspec.yaml
│   └── lib/
│       ├── main.dart            # App entry point
│       ├── services/
│       │   ├── api_service.dart       # HTTP client
│       │   └── encryption_service.dart # Client-side encryption
│       ├── providers/
│       │   ├── auth_provider.dart     # Auth state management
│       │   ├── notes_provider.dart    # Notes state management
│       │   └── chat_provider.dart     # Chat state management
│       └── pages/
│           ├── notes_page.dart        # Main notes UI
│           ├── settings_page.dart     # Settings + secret symbol
│           ├── secret_login_page.dart # Login form
│           └── secret_chat_page.dart  # Chat room UI
│
└── cloudflare/                  # Cloudflare Tunnel Config
    └── config.yml
```

---

## 3. PHASED IMPLEMENTATION PLAN

### PHASE 1 – BASE INFRASTRUCTURE

**Objective:** Set up core infrastructure with Docker, Redis, FastAPI, and Flutter base.

#### Backend Tasks:
- [x] Create FastAPI application structure
- [x] Configure Redis client with TTL support
- [x] Implement health check endpoints
- [x] Set up CORS and security middleware

#### Frontend Tasks:
- [x] Create Flutter project structure
- [x] Implement API service
- [x] Create base notes page UI
- [x] Create settings page UI

#### DevOps Tasks:
- [x] Create Docker Compose configuration
- [x] Create Dockerfiles for frontend and backend
- [x] Configure nginx for Flutter web
- [x] Create Cloudflare Tunnel config

#### UI Checklist:
- [x] Minimal Notes UI built
- [x] Settings page accessible
- [x] Secret symbol added (⟁)
- [x] No chat visible yet

#### Security Checklist:
- [x] Redis internal only
- [x] CORS locked to frontend domain
- [x] .env not exposed
- [x] No debug mode in production

**Acceptance Criteria:** System boots fully via `docker compose up`

---

### PHASE 2 – SECRET ENTRY SYSTEM

**Objective:** Implement hidden entry system with password validation and JWT authentication.

#### Backend Tasks:
- [x] Implement `/api/auth/entry` endpoint
- [x] Implement `/api/auth/login` endpoint
- [x] Implement `/api/auth/verify` endpoint
- [x] Add rate limiting to auth endpoints
- [x] JWT token generation and validation

#### Frontend Tasks:
- [x] Create secret symbol tap handler
- [x] Implement entry password dialog
- [x] Create login form page
- [x] Implement JWT token storage
- [x] Initialize encryption service with server key

#### DevOps Tasks:
- [x] Configure JWT secret in .env
- [x] Set up bcrypt password hashing

#### UI Checklist:
- [x] Secret symbol subtle (looks decorative)
- [x] Password modal clean
- [x] No visible errors on wrong password
- [x] Login form minimal

#### Security Checklist:
- [x] Password hashed compare (bcrypt)
- [x] JWT secure (HS256, 2h expiry)
- [x] Rate limiting (5/minute entry, 10/minute login)
- [x] No plaintext storage

**Acceptance Criteria:** User can login only if credentials match .env

---

### PHASE 3 – REDIS CHAT ENGINE

**Objective:** Implement ephemeral chat with encryption and TTL enforcement.

#### Backend Tasks:
- [x] Implement `/api/chat/messages` endpoint
- [x] Implement `/api/chat/send` endpoint
- [x] Implement `/api/chat/clear` endpoint
- [x] Redis TTL enforcement (86400 seconds)
- [x] AES-256-GCM encryption service

#### Frontend Tasks:
- [x] Create chat page UI
- [x] Implement message list with auto-refresh
- [x] Client-side encryption before sending
- [x] Client-side decryption for display
- [x] Message timestamps display

#### DevOps Tasks:
- [x] Configure Redis maxmemory policy
- [x] Set up encryption key in .env

#### UI Checklist:
- [x] Chat layout clean
- [x] Timestamps visible
- [x] No flashy UI
- [x] Message input minimal

#### Security Checklist:
- [x] AES-256-GCM encryption working
- [x] No plaintext in Redis
- [x] TTL validated (24 hours)
- [x] Messages auto-expire

**Acceptance Criteria:** Messages auto-delete after TTL

---

### PHASE 4 – HARDENING & PRODUCTION MODE

**Objective:** Apply production security hardening.

#### Backend Tasks:
- [x] Strict CORS configuration
- [x] Rate limiting on all endpoints
- [x] Security headers middleware
- [x] Request logging (sanitized)
- [x] Disable API docs in production

#### Frontend Tasks:
- [x] Remove debug prints
- [x] Secure token storage
- [x] Smooth transitions

#### DevOps Tasks:
- [x] Cloudflare Zero Trust ready
- [x] Health monitoring endpoints
- [x] Fail2ban optional (manual setup)

#### UI Checklist:
- [x] No debug console leaks
- [x] No unnecessary UI hints
- [x] Smooth transitions

#### Security Checklist:
- [x] JWT expiration verified (2h)
- [x] Token refresh disabled (by design)
- [x] Rate limit validated
- [x] DDoS mitigation via Cloudflare

**Acceptance Criteria:** System secure and production-ready

---

### PHASE 5 – FINAL AUDIT

**Objective:** Validate complete system functionality and security.

#### Tasks:
- [ ] Code cleanup
- [ ] Remove unused dependencies
- [ ] Validate env configuration
- [ ] Performance test (load testing)
- [ ] Security audit

#### UI Checklist:
- [ ] Responsive layout
- [ ] No layout overflow
- [ ] Works in Chrome + Edge

#### Security Checklist:
- [ ] Redis unreachable externally
- [ ] Backend unreachable externally
- [ ] Only tunnel exposed
- [ ] TLS verified (Cloudflare)

**Acceptance Criteria:** System fully operational and secure

---

## 4. API ENDPOINTS

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/entry` | Validate entry password | No |
| POST | `/api/auth/login` | Login with credentials | No |
| GET | `/api/auth/verify` | Verify JWT token | Yes |

### Chat
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/chat/messages` | Get all messages | Yes |
| POST | `/api/chat/send` | Send a message | Yes |
| DELETE | `/api/chat/clear` | Clear all messages | Yes |
| GET | `/api/chat/count` | Get message count | Yes |

### Notes (Surface App)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/notes` | List all notes | No |
| GET | `/api/notes/{id}` | Get a note | No |
| POST | `/api/notes` | Create a note | No |
| PUT | `/api/notes/{id}` | Update a note | No |
| DELETE | `/api/notes/{id}` | Delete a note | No |

### Health
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Backend health check | No |
| GET | `/` | Root status | No |

---

## 5. DEPLOYMENT INSTRUCTIONS

### Prerequisites:
1. Docker and Docker Compose installed
2. Cloudflare account with tunnel configured
3. Domain configured (note.pixelsolusindo.space, api94837.pixelsolusindo.space)

### Steps:

```bash
# 1. Clone the project
git clone <repository>
cd pixelnotes

# 2. Create .env from template
cp .env.example .env

# 3. Edit .env with your values
nano .env

# 4. Generate bcrypt password hashes
python3 -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"

# 5. Generate encryption key
openssl rand -hex 32

# 6. Start the system
docker compose up -d

# 7. Check logs
docker compose logs -f

# 8. Verify health
curl http://localhost:94838/health
```

### Cloudflare Tunnel Setup:

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared

# Login
./cloudflared tunnel login

# Create tunnel
./cloudflared tunnel create pixelnotes

# Configure DNS
./cloudflared tunnel route dns pixelnotes note.pixelsolusindo.space
./cloudflared tunnel route dns pixelnotes api94837.pixelsolusindo.space

# Get tunnel token for Docker
./cloudflared tunnel token pixelnotes
```

---

## 6. SECURITY HARDENING CHECKLIST

- [x] Redis protected by internal network only
- [x] Backend not accessible publicly
- [x] JWT secret strong (64+ chars)
- [x] Entry password strong
- [x] Cloudflare Tunnel (no public IP)
- [ ] Cloudflare Zero Trust enabled (manual)
- [ ] Bot protection enabled (Cloudflare)
- [x] Rate limiting active
- [x] Logs sanitized (no sensitive data)
- [x] CORS restricted to frontend domain
- [x] Security headers (X-Frame-Options, CSP, etc.)
- [x] No API docs in production

---

## 7. ENVIRONMENT VARIABLES

| Variable | Description | Example |
|----------|-------------|---------|
| FRONTEND_PORT | Frontend port | 94837 |
| BACKEND_PORT | Backend port | 94838 |
| API_BASE_URL | Backend URL | https://api94837.pixelsolusindo.space |
| SECRET_ENTRY_PASSWORD | Entry password | your_secret_password |
| SECRET_USER_1 | User 1 username | user_alpha |
| SECRET_PASS_1 | User 1 bcrypt hash | $2b$12$... |
| SECRET_USER_2 | User 2 username | user_beta |
| SECRET_PASS_2 | User 2 bcrypt hash | $2b$12$... |
| JWT_SECRET | JWT signing key | 64+ char random string |
| JWT_EXPIRY_HOURS | Token expiry | 2 |
| ENCRYPTION_KEY | AES-256 key | 64 hex chars |
| REDIS_HOST | Redis hostname | redis |
| REDIS_PORT | Redis port | 6379 |
| REDIS_TTL_SECONDS | Message TTL | 86400 |
| CF_TUNNEL_TOKEN | Cloudflare token | from cloudflared |
| CORS_ORIGINS | Allowed origins | https://note.pixelsolusindo.space |

---

## 8. FUTURE ROADMAP

### Phase 2:
- Self-destruct timer per message
- Per message TTL
- Secret image sending
- Device binding

### Phase 3:
- Full peer-to-peer WebRTC
- No server storage
- Perfect Forward Secrecy

---

**END OF IMPLEMENTATION PLAN**
