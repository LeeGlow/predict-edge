# PredictEdge

AI-powered prediction market arbitrage platform. Real-time cross-platform probability deviation detection, historical win rate analysis, and executable arbitrage signals.

## Features

- **Real-time Monitoring**: Track 5+ prediction markets (Polymarket, Manifold, Kalshi) with <100ms data latency
- **AI Deviation Detection**: Identify logical mispricing using historical data and news semantic models
- **Arbitrage Signals**: Auto-calculate fees, slippage, and order depth to surface net-positive opportunities
- **Multi-language Support**: English and Chinese interface
- **Subscription Tiers**: Free preview, Basic ($9.9/mo), Pro ($29.9/mo), Enterprise ($99.9/mo)

## Tech Stack

- **Frontend**: Vanilla HTML/JS + Tailwind CSS (SPA)
- **Backend**: FastAPI (Python 3.11)
- **Auth**: JWT with bcrypt password hashing
- **Rate Limiting**: slowapi (5 req/min register, 10 req/min login)
- **Security**: CORS whitelist, security headers, CSP

## Quick Start

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8002

# Frontend
# Open frontend/index.html directly or serve via any static server
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | JWT signing key |
| `ALLOWED_ORIGINS` | No | CORS origins (comma-separated, default: `*`) |
| `PYTHON_VERSION` | No | Python version for Render |

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/api/auth/register` | POST | No | User registration |
| `/api/auth/login` | POST | No | User login |
| `/api/auth/me` | GET | Yes | Current user info |
| `/api/events` | GET | No | List prediction events |
| `/api/alerts` | GET | Yes | User alerts |

Full API docs available at `/docs` (Swagger UI) when running locally.

## Deployment

### Render (Recommended)

1. Connect GitHub repo to Render
2. Use `render.yaml` blueprint (auto-detected)
3. Backend deploys as Web Service with auto static file serving

Live URL: `https://predict-edge-backend.onrender.com`

### Manual

```bash
git clone https://github.com/LeeGlow/predict-edge.git
cd predict-edge/backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port $PORT
```

## Project Structure

```
predict-edge/
├── frontend/
│   └── index.html          # Single-page app
├── backend/
│   ├── app.py              # FastAPI application
│   └── requirements.txt    # Python dependencies
├── render.yaml             # Render deployment config
└── README.md
```

## Security

- Passwords hashed with bcrypt
- JWT tokens with expiration
- Rate limiting on auth endpoints
- Security headers (CSP, HSTS, X-Frame-Options)
- CORS configured via environment variable

## License

MIT
