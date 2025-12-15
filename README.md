# Onboarding Mock App (Executive Demo)

A lightweight mock to demonstrate the onboarding automation concept with **Slack Block Kit-style chat** and **Slack integration**:
- HR creates an onboarding request (role x grade, start date)
- Manager approves/rejects (mock buttons)
- The app shows DM previews for the new hire and the manager
- A reminders page simulates scheduled nudges
- **Web chat UI** with Slack Block Kit-style interface
- **Slack integration** for QA and escalation

## Features

### Web Features
- `/chat` - HR Chat with Block Kit-style UI
- `/tickets` - HR ticket management dashboard
- Multi-language support (EN/JA)
- Onboarding workflow (Create → Approve → Tasks → Reminders)

### Slack Integration (Optional)
- `/hrhelp` slash command for HR questions
- Block Kit responses with escalation support
- Automatic ticket creation on escalation
- HR channel notifications (optional)

## Run locally

### 1. Setup

```bash
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

### 2. Environment Variables (Optional for Slack)

Create `.env` file (optional, only if using Slack):

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_HR_CHANNEL_ID=C1234567890  # Optional: HR channel for notifications
TZ=Asia/Tokyo
```

### 3. Start Server

```bash
uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000

### 4. Test Web Chat

- Visit http://127.0.0.1:8000/chat
- Try questions like:
  - "How do I request time off?"
  - "What is the attendance policy?"
  - "I need to change my address"
  - "Tell me about onboarding"
- Click "Escalate to HR" button to create a ticket
- View tickets at http://127.0.0.1:8000/tickets

## Slack App Setup (Optional)

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "HR Bot" (or your choice)
4. Select your workspace

### 2. Configure Bot Token Scopes

**OAuth & Permissions** → **Scopes** → **Bot Token Scopes**:
- `app_mentions:read` (for @bot mentions)
- `chat:write` (to send messages)
- `commands` (for slash commands)
- `channels:read` (optional, for channel info)

### 3. Install App to Workspace

**OAuth & Permissions** → Click "Install to Workspace" → Authorize

Copy the **Bot User OAuth Token** (starts with `xoxb-`) → Set as `SLACK_BOT_TOKEN`

### 4. Configure Slash Command

**Slash Commands** → **Create New Command**:
- Command: `/hrhelp`
- Request URL: `https://your-domain.com/slack/commands` (or ngrok URL for local)
- Short Description: "Ask HR questions"
- Usage Hint: `[your question]`

### 5. Configure Event Subscriptions

**Event Subscriptions** → Enable Events:
- Request URL: `https://your-domain.com/slack/events` (or ngrok URL for local)
- Subscribe to bot events:
  - `app_mention` (for @bot mentions)

### 6. Configure Interactivity

**Interactivity** → Enable Interactivity:
- Request URL: `https://your-domain.com/slack/interactive` (or ngrok URL for local)

### 7. Get Signing Secret

**Basic Information** → **App Credentials** → Copy **Signing Secret** → Set as `SLACK_SIGNING_SECRET`

### 8. Local Testing with ngrok

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# Use the HTTPS URL (e.g., https://abc123.ngrok.io) in Slack app settings:
# - Event Subscriptions Request URL: https://abc123.ngrok.io/slack/events
# - Slash Commands Request URL: https://abc123.ngrok.io/slack/commands
# - Interactivity Request URL: https://abc123.ngrok.io/slack/interactive
```

### 9. Test Slack Integration

1. Invite bot to a channel: `/invite @HR Bot`
2. Try slash command: `/hrhelp How do I request time off?`
3. Or mention bot: `@HR Bot what is the attendance policy?`
4. Click "Escalate to HR" button to create a ticket

## Deploy to Render

### 1. Create Web Service

- Create a new Render Web Service from this repo
- Build command: `pip install --upgrade pip && pip install -r ./requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2. Environment Variables (Optional for Slack)

Add in Render dashboard:
- `SLACK_BOT_TOKEN` (if using Slack)
- `SLACK_SIGNING_SECRET` (if using Slack)
- `SLACK_HR_CHANNEL_ID` (optional, for HR notifications)
- `TZ=Asia/Tokyo` (optional)

### 3. Update Slack App URLs

After deployment, update Slack app settings with your Render URL:
- Event Subscriptions: `https://your-app.onrender.com/slack/events`
- Slash Commands: `https://your-app.onrender.com/slack/commands`
- Interactivity: `https://your-app.onrender.com/slack/interactive`

## API Endpoints

- `GET /` - Home page
- `GET /chat` - Web chat UI
- `POST /chat/ask` - Process chat question (JSON)
- `POST /chat/escalate` - Escalate to HR (JSON)
- `GET /tickets` - Ticket list (HR dashboard)
- `POST /tickets/{id}/close` - Close ticket
- `GET /health` - Health check
- `POST /slack/events` - Slack Events API (if Slack enabled)
- `POST /slack/commands` - Slack Slash Commands (if Slack enabled)
- `POST /slack/interactive` - Slack Interactive Components (if Slack enabled)

## Notes

- Storage uses SQLite (`app/data.db`) created automatically at startup.
- Templates are embedded in code for simplicity; later phases can replace with YAML.
- Slack integration is optional - app works without it.
- QA engine is rule-based (keyword matching) - no LLM required.
- Personal information is not stored (only user_id, channel_id for Slack tickets).
