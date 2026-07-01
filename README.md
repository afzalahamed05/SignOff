# SignOff AI 🚀

**The AI-Powered Creative Operations Platform for Agencies & Freelancers.**

SignOff AI eliminates the chaos of agency-client feedback loops. It centralizes file versioning, visual inline feedback, milestone tracking, and automated billing into a single, professional workspace. Enhanced by a 100% free, locally-hosted AI engine, it transforms messy client comments into structured, prioritized action lists for design teams.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![Stripe](https://img.shields.io/badge/Stripe-Integrated-purple?logo=stripe)

---

## ✨ Key Features

- **🏢 Multi-Tenant Workspaces:** Complete isolation for agencies, with Role-Based Access Control (Admin, PM, Creative, Client).
- **📁 Direct-to-Storage Uploads:** Secure, high-performance file uploads directly to Supabase Storage via presigned URLs (zero backend bandwidth bottleneck).
- **📌 Visual Inline Feedback:** Figma-style canvas where clients click directly on images to drop pins and leave contextual comments.
- **🤖 100% Free Local AI Synthesizer:** Uses local Ollama (`qwen2.5:3b`) via Celery background workers to read threaded feedback and generate prioritized JSON action items. Zero API costs.
- **⚡ Real-Time Collaboration:** Instant comment updates and AI status notifications via WebSockets backed by Redis Pub/Sub.
- **💳 Automated Stripe Billing:** Generate invoices directly from completed milestones. Clients pay via hosted Stripe pages, with automatic status updates via Webhooks.
- **🔒 Enterprise-Grade Security:** JWT Auth, strict Workspace-scoping to prevent IDOR vulnerabilities, and secure presigned URLs for private files.

---

## 🏗 High-Level Architecture

```mermaid
graph TD
    Client[Next.js 15 Frontend] -->|REST / WS| API[FastAPI Backend]
    API -->|Async ORM| DB[(MySQL)]
    API -->|Pub/Sub| Cache[(Redis)]
    Cache -->|Broker| Worker[Celery Worker]
    Worker -->|Inference| AI[Local Ollama AI]
    Worker -->|Webhook| API
    Client -->|Presigned PUT| Storage[(Supabase Storage)]
    API -->|Presigned URLs| Storage
    API -->|Billing| Stripe[Stripe API]
