# ⚡ WartaKilat — Automated News Portal Engine (Zero-Cost Architecture)

[![Stack: Jamstack](https://img.shields.io/badge/Architecture-JAMstack-blue.svg)](https://jamstack.org)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![Database: Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-emerald.svg)](https://supabase.com)
[![AI Engine: Groq](https://img.shields.io/badge/AI Engine-Groq%20LLaMA--3.3-orange.svg)](https://groq.com)
[![Host: Cloudflare Pages](https://img.shields.io/badge/Hosting-Cloudflare%20Pages-f38020.svg)](https://pages.cloudflare.com)

> **⚠️ PRIVATE REPOSITORY / INTERNAL ENGINE**  
> *Notice: This repository contains custom automated content generation (AGC) scripts, RSS parsers, and frontend layouts tailored for private deployment on specific domains. It is not intended for general public library use or general-purpose distribution.*

---

## 📌 Project Overview

**WartaKilat** is an automated, zero-cost digital news platform specializing in **Government/Law (Hukum & Politik)** and **Sports (Olahraga)** news feeds.

The engine automatically collects feeds from verified news providers, generates AI-driven click-worthy headlines, summarizes key facts into a **"30-Second TL;DR"** reading format using Groq's LLaMA 3.3 model, and serves static edge pages with sub-second page loads.

---

## 🏗️ System Architecture (100% Zero-Cost Stack)

```
[ Target RSS Feeds ] (Hukum / Olahraga)
         │
         ▼
[ GitHub Actions Cron ] (Runs every 60 mins / 24x daily)
         │
         ├───> [ Groq API (LLaMA-3.3-70B) ] ──> (Generate Titles & TL;DR)
         │
         ▼
[ Supabase PostgreSQL ] (Data Storage with UNIQUE Url Constraints)
         │
         ▼
[ Cloudflare Pages / Vercel ] (Vanilla JS + Tailwind CSS Frontend)
```

---

## 🚀 Key Features & Direct Fixes Built-in

* **🤖 Dynamic AI Rewriting (Groq API):** Automatically rewrites raw headlines to be engaging and creates 3 bulleted TL;DR points per article.
* **⚡ Sub-Second Edge Performance:** Static Jamstack frontend hosted on Cloudflare Pages with zero database bottlenecks on client requests.
* **🛡️ Hotlink Protection Bypass:** Includes `<meta name="referrer" content="no-referrer">` to safely render target images without broken link icons.
* **🧹 Anti-Duplicate Mechanism:** Database schema enforces `source_url UNIQUE` constraints to eliminate duplicate content insertion.
* **📦 Rate-Limited & Safe AI Processing:** Enforces a hard limit of maximum 3-5 processed articles per run to stay well within Groq API free-tier limits.
* **💰 Multi-Ad Network Ready:** Pre-configured slots for Google AdSense, Adsterra, or Monetag pop-under/native banners.

---

## 📂 Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── scraper.yml     # Automated Cron trigger (runs every hour)
├── index.html              # Dynamic JAMstack Frontend (Tailwind + Supabase JS)
├── scraper.py              # Main Python Scraper & Groq AI processing script
├── requirements.txt        # Python dependencies (feedparser, supabase, groq)
└── README.md               # Project documentation
```

---

## 🛠️ Database Schema (Supabase SQL)

Before running the scraper script, execute the following schema setup in your Supabase SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS articles (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    summary TEXT,
    tldr JSONB,
    content TEXT,
    source_url VARCHAR(1000) UNIQUE NOT NULL,
    image_url TEXT,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIMEZONE DEFAULT NOW()
);

-- Optimization Indexes
CREATE INDEX idx_category ON articles(category);
CREATE INDEX idx_created_at ON articles(created_at DESC);
```

---

## ⚙️ Environment Variables & Setup

This project requires three secret parameters. Add them to your repository under **Settings > Secrets and Variables > Actions**:

| Secret Name | Description | Example |
| :--- | :--- | :--- |
| `SUPABASE_URL` | Your Supabase project URL | `https://xyzproject.supabase.co` |
| `SUPABASE_KEY` | Supabase Service Role / Anon Key | `eyJhbGciOiJKV1Qi...` |
| `GROQ_API_KEY` | Groq API Key (Free Tier) | `gsk_xxxxxxxxxxxxxxxxx` |

---

## 🚦 How to Extend / Add New Categories

To add a new category (e.g., *Teknologi*):

1. **Open `scraper.py`** and add target RSS feeds to the `RSS_FEEDS` dictionary:
   ```python
   RSS_FEEDS = {
       'hukum': ['https://www.antaranews.com/rss/hukum.xml'],
       'olahraga': ['https://www.antaranews.com/rss/olahraga.xml'],
       'teknologi': ['https://www.antaranews.com/rss/tekno.xml']  # Added topic
   }
   ```
2. **Open `index.html`** and add a filter button in the navigation bar:
   ```html
   <button onclick="filterCategory('teknologi')" class="text-sky-400 hover:underline">💻 Teknologi</button>
   ```

---

## 🔒 Security & License Notice

This repository is strictly intended for private deployment. Commercial redistribution or public mirroring of this codebase without custom modification is not recommended.

**Developer:** Custom Private Engine  
**Status:** Active Maintenance / Operational