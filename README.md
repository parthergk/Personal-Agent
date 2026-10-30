# VXYAK — Personal AI Agent

> **Your world, in quiet sync.**  
> An intelligent, multimodal personal memory and task assistant accessible directly through WhatsApp. Powered by OpenAI, Qdrant Vector Database, Sarvam AI, FastAPI, and Next.js.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![Qdrant](https://img.shields.io/badge/Vector_DB-Qdrant-red.svg)](https://qdrant.tech/)
[![OpenAI](https://img.shields.io/badge/LLM-GPT--4o--mini-412991.svg)](https://openai.com/)
[![Sarvam AI](https://img.shields.io/badge/STT-Sarvam_AI-orange.svg)](https://sarvam.ai/)
[![WhatsApp](https://img.shields.io/badge/Messaging-WhatsApp_Cloud_API-25D366.svg)](https://developers.facebook.com/docs/whatsapp/cloud-api)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](#license)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture & System Flow](#-architecture--system-flow)
- [Repository Structure](#-repository-structure)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Environment Configuration](#-environment-configuration)
  - [Backend (.env)](#1-backend-configuration-apienv)
  - [Frontend (.env.local)](#2-frontend-configuration-landing-pageenvlocal)
- [Quickstart & Local Development](#-quickstart--local-development)
  - [1. Start Qdrant Vector DB](#1-start-qdrant-vector-database)
  - [2. Start the Backend API](#2-start-fastapi-backend)
  - [3. Start the Next.js Frontend](#3-start-nextjs-frontend)
  - [4. Expose Webhook for WhatsApp](#4-connect-whatsapp-webhook-via-tunnel)
- [WhatsApp Cloud API Webhook Setup](#-whatsapp-cloud-api-webhook-setup)
- [API Reference](#-api-reference)
- [Production & Deployment](#-production--deployment)
  - [AWS EC2 Deployment with PM2](#aws-ec2--pm2)
  - [CI/CD Workflow](#github-actions-cicd)
  - [Next.js Frontend on Vercel](#frontend-on-vercel)
- [License](#-license)

---

## 🌟 Overview

**VXYAK** is a production-ready personal AI companion designed to eliminate mental clutter. Unlike traditional chatbots that require a dedicated app, VXYAK lives inside **WhatsApp**, where users already spend their time.

Send voice notes, screenshots, documents, photos, or simple text notes to VXYAK. It analyzes, classifies, and indexes them into a high-dimensional vector space. Whenever you need anything — from a misplaced document, a saved screenshot, or a past decision — just ask in plain English, Hindi, or Hinglish, and VXYAK fetches it instantly. Need to be reminded of something later? VXYAK schedules it with atomic background workers and messages you right when it's due.

---

## ✨ Key Features

- **💬 WhatsApp-Native Interface**:
  - Full two-way communication using Meta's official WhatsApp Business Cloud API.
  - Automatic read receipts (blue ticks) and typing indicators for a responsive chat feel.
  - Dynamic media responses: seamlessly returns images, videos, audio, and documents directly to the WhatsApp chat.

- **🧠 Semantic Long-Term Memory (RAG)**:
  - Vector embeddings powered by OpenAI (`text-embedding-3-small`, 1536 dimensions).
  - Storage and hybrid filtering in **Qdrant Vector Database**.
  - Search notes and media by semantic meaning, context, or category — no exact keyword matches required.
  - Strict multi-tenant isolation via indexed `user_id` attributes.

- **🎙️ Multimodal Preprocessing Pipeline**:
  - **Voice Notes & Audio**: Transcribed into text with **Sarvam AI** (`saaras:v3`), optimized for Indian accents, regional nuances, and Hindi/Hinglish speech. Handles files up to 25MB.
  - **Images & Photos**: Automatic scene and visual understanding via **OpenAI GPT-4o-mini Vision**. Prompts the user before storing and preserves file references.
  - **Documents**: Inline reading for code, text, CSV, JSON, and markdown files up to 100KB; structured ingestion for PDFs, Word documents, spreadsheets, and archives.
  - **Video**: File validation and metadata categorization.

- **⏰ Smart Background Reminders**:
  - Natural language scheduling (e.g., *"Remind me to call Mom tomorrow at 6 PM"* or *"Kal subah 9 baje yaad dilana"*).
  - Background scheduler driven by **APScheduler** polling every 5 seconds.
  - Distributed atomic locking (`status='processing'`, `locked_until`, retry exponential caps) prevents duplicate alerts and recovers gracefully from crashes.
  - Automated WhatsApp message dispatch when due.

- **🔐 Phone Authentication & WhatsApp OTP**:
  - Self-serve registration portal built with Next.js 16.
  - Secure verification codes generated and delivered via WhatsApp.
  - HMAC-SHA256 hashed OTP verification, 60-second cooldown rate-limiting, and brute-force attempt limits backed by Redis (with fallback in-memory caching).
  - Webhook intercepts unauthorized senders and prompts them to verify via the web onboarding portal.

- **💬 Conversation History & Context Filtering**:
  - Sliding-window context stored in SQLite (`ConversationContext`) retaining recent user-assistant dialogue turns across sessions.
  - Intelligent filtering discards out-of-scope chit-chat and prompt injections to keep memory clean.

---

## 🏗️ Architecture & System Flow

```
                      +------------------------------------+
                      |       Next.js Web Portal           |
                      |  (Landing, Onboarding & Login)     |
                      +-----------------+------------------+
                                        |  REST (OTP & Auth)
                                        v
+-----------------------+     +--------------------+     +-----------------------+
|  User on WhatsApp     | --> | WhatsApp Cloud API | --> |  FastAPI Webhook      |
| (Text, Voice, Images) | <-- | (Meta Graph API)   | <-- |  (/webhook)           |
+-----------------------+     +--------------------+     +-----------+-----------+
                                                                     |
       +-------------------------------------------------------------+
       |
       v
+--------------------------------------------------------------------------------+
| Multimodal Preprocessors                                                       |
|  - Audio: Sarvam AI (Speech-to-Text saaras:v3)                                |
|  - Image: OpenAI GPT-4o-mini Vision                                            |
|  - Docs: Plaintext inliner & file type classifier                              |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
| AI Agent Orchestrator (OpenAI GPT-4o-mini + Function Calling)                  |
+-------------------+--------------------+-------------------+-------------------+
                    |                    |                   |
                    v                    v                   v
           +-----------------+  +-----------------+  +-----------------+
           |   save_memory   |  |  search_memory  |  | create_reminder |
           +--------+--------+  +--------+--------+  +--------+--------+
                    |                    |                    |
                    v                    v                    v
           +--------------------------------------+  +-----------------+
           |      Qdrant Vector Database          |  | SQLite / DB     |
           |     (memories collection)            |  | (reminders.db)  |
           +--------------------------------------+  +--------+--------+
                                                              |
                                                              v
                                                     +-----------------+
                                                     |  APScheduler    |
                                                     | (Worker Loop)   |
                                                     +--------+--------+
                                                              |
                                                              v
                                                     +-----------------+
                                                     | Send Reminder   |
                                                     |   via WhatsApp  |
                                                     +-----------------+
```

---

## 📁 Repository Structure

```
Personal-Agent/
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD pipeline deploying to AWS EC2 via SSH
├── api/                          # FastAPI Backend Application
│   ├── agent/                    # Agent logic, Prompts, Tools & Memory
│   │   ├── conversation_store.py # Persistent user conversation context
│   │   ├── core.py               # Main message processing & LLM agent loop
│   │   ├── memory_store.py       # OpenAI embeddings + Qdrant search/upsert
│   │   ├── models.py             # Pydantic schemas (IncomingMessage, AgentResponse)
│   │   ├── prompts.py            # System prompts, behavioral rules & instructions
│   │   ├── reminder.py           # Tool handler for creating reminders
│   │   └── tools.py              # Function call schemas for OpenAI
│   ├── db/                       # Database engine, sessions & models
│   │   ├── models/
│   │   │   ├── conversation.py   # ConversationContext model
│   │   │   ├── reminder.py       # Reminder model with locks & retry state
│   │   │   └── user.py           # User model (phone, name, timezone, is_active)
│   │   ├── qdrant_client.py      # Qdrant client connection instance
│   │   ├── session.py            # SQLAlchemy database engine and session factory
│   │   └── setup.py              # Qdrant collection & index initialization
│   ├── processors/               # Multimodal media handlers
│   │   ├── audio.py              # Sarvam AI STT speech transcription
│   │   ├── document.py           # Document parser & inline reader
│   │   ├── image.py              # GPT-4o-mini Vision analysis & prompt builder
│   │   ├── preprocessor.py       # High-level dispatcher for incoming media
│   │   └── video.py              # Video preprocessor
│   ├── routes/                   # API endpoint routers
│   │   ├── auth.py               # Phone OTP registration & verification
│   │   └── webhook.py            # Meta WhatsApp Cloud API webhook handler
│   ├── services/                 # External services & background workers
│   │   ├── auth_service.py       # Redis-backed auth verification & cache
│   │   ├── get_msg.py            # WhatsApp webhook message parser & downloader
│   │   ├── otp_service.py        # OTP generator, HMAC hasher & rate limiter
│   │   ├── reminder_scheduler.py # APScheduler background polling engine
│   │   ├── send_reminder.py      # Reminder WhatsApp message formatter & sender
│   │   └── whatsapp.py           # WhatsApp Graph API media uploader & sender
│   ├── uploads/                  # Temporary storage for downloaded user media
│   ├── main.py                   # FastAPI entrypoint, CORS, lifespan & scheduler
│   ├── requirements.txt          # Python dependencies
│   └── .env.example              # Template for backend environment variables
├── landing-page/                 # Next.js 16 Web Application
│   ├── public/                   # Static assets & background art
│   ├── src/
│   │   ├── app/                  # App Router pages (Home, /register, /login)
│   │   ├── components/           # Reusable UI components
│   │   └── lib/                  # Client-side messaging & API handlers
│   ├── package.json              # Frontend npm dependencies and scripts
│   └── .env.local                # Frontend environment variables template
├── docker-compose.yml            # Container definitions (Qdrant Vector DB)
├── ecosystem.config.cjs          # PM2 production configuration for FastAPI
└── README.md                     # Project documentation
```

---

## 🛠️ Tech Stack

| Category | Technology | Description |
|---|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | Modern, high-performance async Python web framework |
| **Server / ASGI** | [Uvicorn](https://www.uvicorn.org/) | Lightning-fast ASGI web server implementation |
| **Frontend Framework** | [Next.js 16](https://nextjs.org/) | React 19 App Router framework with TypeScript |
| **Styling** | [Tailwind CSS v4](https://tailwindcss.com/) | Utility-first styling with modern typography |
| **LLM & Vision** | [OpenAI](https://openai.com/) | `gpt-4o-mini` for chat, function calling, and image vision |
| **Embeddings** | [OpenAI](https://platform.openai.com/docs/guides/embeddings) | `text-embedding-3-small` (1536 dimensions) |
| **Speech-to-Text** | [Sarvam AI](https://sarvam.ai/) | High-accuracy transcription (`saaras:v3`) for Indian accents & Hinglish |
| **Vector Database** | [Qdrant](https://qdrant.tech/) | Vector similarity search engine with payload index filtering |
| **Relational Database** | [SQLAlchemy](https://www.sqlalchemy.org/) + [SQLite](https://sqlite.org/) | Stores users, persistent chat history, and reminders |
| **Background Jobs** | [APScheduler](https://apscheduler.readthedocs.io/) | Advanced Python Scheduler for due reminder polling |
| **Caching & OTP** | [Redis](https://redis.io/) | Async Redis client for auth caching and OTP cooldowns |
| **Messaging API** | [Meta WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api) | Cloud API Graph v21.0 for messaging and media delivery |
| **Process Manager** | [PM2](https://pm2.keymetrics.io/) | Production process manager for Node and Python services |

---

## 📋 Prerequisites

Before running the project locally or in production, ensure you have:

1. **Python 3.10+** installed
2. **Node.js 18+** & **npm** installed
3. **Docker & Docker Compose** installed
4. **Meta Developer Account** with a WhatsApp Business Cloud App created
5. **OpenAI API Key** with access to GPT-4o-mini and embeddings
6. **Sarvam AI API Key** for audio transcription
7. *(Optional)* **Redis** server running (falls back to in-memory caching if omitted)

---

## ⚙️ Environment Configuration

### 1. Backend Configuration (`api/.env`)

Create a `.env` file in the `api/` directory by copying `api/.env.example`:

```bash
cp api/.env.example api/.env
```

Fill in the appropriate configuration keys:

```ini
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Qdrant Vector Database
# Use http://localhost:6333 for local Docker container, or your Qdrant Cloud cluster URL
QDRANT_URL=http://localhost:6333
API_KEY=your-qdrant-api-key-if-cloud-else-empty

# Sarvam AI (Speech-to-Text Audio Transcription)
SARVAM_API_KEY=your-sarvam-api-key

# Relational Database (Users, Reminders & Chat Context)
DATABASE_URL=sqlite:///./db/reminders.db

# Redis (Auth Status & OTP Cooldowns)
REDIS_URL=redis://localhost:6379/0
OTP_SECRET=your-random-hmac-secret-key-32-chars

# WhatsApp Business Cloud API (Meta)
WHATSAPP_TOKEN=your-meta-whatsapp-system-user-access-token
PHONE_NUMBER_ID=your-whatsapp-phone-number-id
WHATSAPP_VERIFY_TOKEN=any-secure-string-for-webhook-verification

# Fallback phone number (for tests / direct alerts)
RECIPIENT_PHONE_NUMBER=919876543210

# Environment & Frontend
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
```

### 2. Frontend Configuration (`landing-page/.env.local`)

Create `.env.local` inside the `landing-page/` directory:

```ini
# Point to your running FastAPI backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# WhatsApp Bot Phone Number (digits with country code, e.g. 17112345905)
NEXT_PUBLIC_WHATSAPP_BOT_NUMBER=17112345905
```

---

## 🚀 Quickstart & Local Development

Follow these steps to spin up the entire system on your development machine:

### 1. Start Qdrant Vector Database

Start Qdrant locally using Docker Compose:

```bash
docker compose up -d
```

This launches Qdrant on port `6333` with data persisted to `./qdrant_data`. Check the dashboard in your browser at [http://localhost:6333/dashboard](http://localhost:6333/dashboard).

### 2. Start FastAPI Backend

Navigate to the `api/` directory, set up your Python virtual environment, install dependencies, and run Uvicorn:

```bash
cd api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database & Qdrant collection setup (auto-creates tables and indices)
python db/setup.py

# Launch development server with auto-reload
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The API will now be running at:
- **Base URL**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Start Next.js Frontend

In a separate terminal, navigate to the `landing-page/` directory:

```bash
cd landing-page

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to explore the landing page and registration flow.

### 4. Connect WhatsApp Webhook via Tunnel

WhatsApp requires an externally reachable HTTPS URL to deliver incoming webhook notifications. Use a tunneling tool like **ngrok** or **Cloudflare Tunnel**:

```bash
ngrok http 8000
```

Copy the generated HTTPS URL (e.g. `https://your-domain.ngrok-free.app`). Your webhook address will be:
```
https://your-domain.ngrok-free.app/webhook
```

---

## 📲 WhatsApp Cloud API Webhook Setup

1. Open the [Meta for Developers Portal](https://developers.facebook.com/).
2. Select your App and navigate to **WhatsApp** -> **Configuration**.
3. Under **Webhook**, click **Edit**:
   - **Callback URL**: Enter `https://your-domain/webhook`
   - **Verify Token**: Enter the exact string configured in `WHATSAPP_VERIFY_TOKEN` in your `.env`.
   - Click **Verify and Save**.
4. In **Webhook fields**, click **Manage** and subscribe to **`messages`**.
5. Ensure your Test or Production WhatsApp Phone Number is linked to your app and your System User Access Token has `whatsapp_business_messaging` and `whatsapp_business_management` permissions.

---

## 📡 API Reference

### Health
- **`GET /health`**
  - Returns `{"status": "ok"}`.

### WhatsApp Webhook
- **`GET /webhook`**
  - Webhook verification challenge used by Meta Graph API during setup.
  - Requires `hub.mode=subscribe`, `hub.verify_token`, and returns `hub.challenge`.
- **`POST /webhook`**
  - Ingestion endpoint for all WhatsApp events: incoming text, voice notes, photos, documents, and delivery receipts.

### Authentication & Registration
- **`POST /register`** or **`POST /send-otp`**
  - Initiates user signup or login by requesting a WhatsApp OTP.
  - **Body**:
    ```json
    {
      "phone": "+919876543210",
      "name": "Alex"
    }
    ```
  - **Response**:
    ```json
    {
      "success": true,
      "message": "Verification code sent successfully",
      "phone": "+919876543210"
    }
    ```
- **`POST /verify-otp`**
  - Validates the 6-digit OTP code sent via WhatsApp and activates the user account.
  - **Body**:
    ```json
    {
      "phone": "+919876543210",
      "otp": "123456",
      "name": "Alex"
    }
    ```
  - **Response**:
    ```json
    {
      "success": true,
      "message": "User verified and activated successfully",
      "user": {
        "id": 1,
        "phone": "+919876543210",
        "name": "Alex",
        "timezone": "Asia/Kolkata",
        "is_active": true
      }
    }
    ```

---

## 🚀 Production & Deployment

### AWS EC2 & PM2

The backend is configured to run under **PM2** via [ecosystem.config.cjs](file:///d:/projects/Personal-Agent/ecosystem.config.cjs).

1. Clone the repository on your EC2 instance into `~/Personal-Agent`.
2. Setup the Python virtual environment in `api/venv`.
3. Start the application with PM2:
   ```bash
   pm2 start ecosystem.config.cjs --only agent-api
   pm2 save
   ```

### GitHub Actions CI/CD

An automated deployment pipeline is set up in [.github/workflows/deploy.yml](file:///d:/projects/Personal-Agent/.github/workflows/deploy.yml):

- On push to `main`, GitHub Actions connects to the EC2 server over SSH.
- Pulls the latest code.
- Installs updated dependencies in `api/venv`.
- Reloads the FastAPI instance via `pm2 startOrReload ecosystem.config.cjs --only agent-api --update-env`.

**Required GitHub Repository Secrets**:
- `AWS_EC2_IP`: Public IP of your EC2 instance.
- `AWS_EC2_USERNAME`: SSH username (e.g. `ubuntu` or `ec2-user`).
- `AWS_EC2_PRIVATE_KEY`: Raw SSH private key (`.pem`).
- `AWS_EC2_PORT`: SSH port (defaults to `22`).

### Frontend on Vercel

The Next.js landing page can be deployed directly to [Vercel](https://vercel.com/):

1. Import the repository into Vercel and specify the Root Directory as `landing-page`.
2. Add environment variables:
   - `NEXT_PUBLIC_API_URL`: Your production backend API URL (e.g., `https://api.vxyak.com`).
   - `NEXT_PUBLIC_WHATSAPP_BOT_NUMBER`: Your production WhatsApp bot number.
3. Deploy!

---

## 🔒 Security & Privacy

- **Data Privacy**: Internal server file paths and vector database IDs are strictly protected and never exposed to users in WhatsApp messages.
- **Multi-Tenant Protection**: Every search and memory retrieval query is explicitly constrained with `user_id` filtering at the database layer.
- **Rate-Limiting**: OTP requests are protected with cooldown periods and maximum retry attempts to mitigate spam and brute-force attacks.
- **Fail-Safe Processing**: Audio, document, and vision processors are bounded by strict timeouts and file size limits to prevent Denial of Service (DoS) or unexpected resource exhaustion.

---

## 📄 License & Intellectual Property

Copyright © 2026 Vxyak. All rights reserved.

This software and associated documentation files are **proprietary and confidential**. Unauthorized copying, modification, distribution, reverse engineering, or commercial use of this codebase, via any medium, is strictly prohibited without explicit written permission.
