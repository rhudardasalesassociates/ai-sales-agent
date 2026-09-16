# AI Sales Agent - Facebook Messenger

An AI-powered sales agent that handles customer conversations, recommends products, and manages leads through Facebook Messenger.

## Features

- **Lead Qualification**: Automatically qualifies leads through conversation
- **Product Recommendations**: Suggests products based on customer needs
- **Sales Conversations**: Handles objections and guides to purchase
- **Human Handoff**: Escalates to human agent when needed
- **Multi-Language**: Supports English, Spanish, French, German, Tagalog
- **Scheduling**: Books appointments via conversation
- **CRM Integration**: Tracks leads and conversations
- **Analytics**: Real-time conversation statistics

## Prerequisites

- Python 3.11+
- Facebook Developer Account
- OpenAI API Key
- Google Sheets API Credentials (optional)

## Quick Start

### 1. Clone and Setup

```bash
cd ai-sales-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Facebook Messenger
FACEBOOK_PAGE_ACCESS_TOKEN=your_token
FACEBOOK_VERIFY_TOKEN=your_verify_token
FACEBOOK_APP_SECRET=your_app_secret

# OpenAI
OPENAI_API_KEY=your_api_key

# Business Info
BUSINESS_NAME=Your Store
BUSINESS_PHONE=+1234567890
BUSINESS_EMAIL=support@yourstore.com
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Setup Facebook Webhook

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create a new app or use existing
3. Add Messenger product
4. Set webhook URL: `https://your-domain.com/webhook/`
5. Verify token: Use your `FACEBOOK_VERIFY_TOKEN`
6. Subscribe to messages and postbacks

## Google Sheets Integration

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account
5. Download credentials JSON file
6. Save as `credentials.json` in project root

### 2. Setup Spreadsheet

Create a Google Sheet with these columns:

| name | description | price | category | in_stock | image_url | features |
|------|-------------|-------|----------|----------|-----------|----------|
| Product Name | Description | 99.99 | Category | Yes | https://... | Feature1, Feature2 |

Share the spreadsheet with your service account email.

### 3. Configure

```env
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/your-sheet-id
```

## Deployment

### Railway (Recommended - Free Tier)

1. Create account at [Railway](https://railway.app)
2. Connect your GitHub repo
3. Add environment variables
4. Deploy

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render (Free Tier)

1. Create account at [Render](https://render.com)
2. Create new Web Service
3. Connect GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables

### Docker

```bash
docker-compose up -d
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server status |
| `/health` | GET | Health check |
| `/stats` | GET | Conversation statistics |
| `/webhook/` | GET | Facebook webhook verification |
| `/webhook/` | POST | Facebook webhook handler |

## Project Structure

```
ai-sales-agent/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── messenger/
│   │   ├── webhook.py       # Webhook handler
│   │   └── sender.py        # Message sender
│   ├── ai/
│   │   ├── engine.py        # OpenAI integration
│   │   ├── prompts.py       # Sales prompts
│   │   └── language.py      # Language detection
│   ├── services/
│   │   ├── conversation.py  # Conversation management
│   │   ├── products.py      # Product catalog
│   │   ├── scheduler.py     # Appointment booking
│   │   └── handoff.py       # Human escalation
│   └── models/
│       └── schemas.py       # Data models
├── .env.example             # Environment template
├── requirements.txt         # Dependencies
├── Procfile                 # Railway deployment
├── Dockerfile              # Docker configuration
└── docker-compose.yml      # Docker Compose
```

## Conversation Flow

```
User Message
    ↓
Language Detection
    ↓
Intent Analysis
    ↓
State Machine:
├── GREETING → Welcome message
├── QUALIFYING → Ask qualifying questions
├── RECOMMENDING → Suggest products
├── HANDLING_OBJECTIONS → Address concerns
├── CLOSING → Guide to purchase
├── SCHEDULING → Book appointment
└── HANDOFF → Transfer to human
    ↓
Generate Response
    ↓
Send to Messenger
```

## Customization

### Adding New Languages

Edit `app/ai/language.py`:

```python
COMMON_WORDS = {
    "your_lang": ["word1", "word2", ...]
}
```

Edit `app/ai/prompts.py`:

```python
def _get_language_instructions(self, language: str) -> str:
    instructions = {
        "your_lang": "Respond in Your Language."
    }
```

### Custom Handoff Keywords

Edit `.env`:

```env
HUMAN_HANDOFF_KEYWORDS=human,agent,support,help,supervisor
```

## Monitoring

### View Statistics

```bash
curl http://localhost:8000/stats
```

Response:

```json
{
  "total_conversations": 150,
  "active_conversations": 12,
  "leads_generated": 45,
  "appointments_scheduled": 8,
  "handoffs": 5
}
```

## Troubleshooting

### Webhook Not Receiving Events

1. Verify webhook URL is accessible
2. Check Facebook App Secret is correct
3. Ensure server returns 200 status
4. Check server logs for errors

### Messages Not Sending

1. Verify Page Access Token is valid
2. Check token has required permissions
3. Ensure recipient ID is correct

### OpenAI Errors

1. Verify API key is valid
2. Check account has credits
3. Monitor rate limits

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.