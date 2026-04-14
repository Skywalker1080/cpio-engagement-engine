---
name: navigate-project-structure
description: Navigates the project structure and explains the purpose of each directory and file.
---

cpio-engagement-engine/
├── src/
│   ├── agents/
│   │   ├── discovery.py          # Scans platforms for conversations
│   │   ├── classifier.py         # Scores authors, assigns persona tier
│   │   ├── responder.py          # Generates contextual replies (8 archetypes)
│   │   ├── publisher.py          # Posts replies via Apify + APIs
│   │   ├── crm_tracker.py        # Logs interactions, manages relationships
│   │   └── analytics.py          # Daily engagement outcome review
│   ├── data/                     # Shared with carousel engine
│   │   ├── cryptocom.py
│   │   ├── coingecko.py
│   │   ├── defillama.py
│   │   ├── bigquery.py
│   │   └── postgres.py
│   ├── scrapers/
│   │   ├── twitter_scanner.py    # Apify tweet-scraper wrapper
│   │   ├── reddit_scanner.py     # Reddit API + Apify scraper
│   │   ├── linkedin_scanner.py   # Apify linkedin-post-search wrapper
│   │   ├── discord_monitor.py    # Discord Gateway WebSocket bot
│   │   └── telegram_monitor.py   # Apify telegram-scraper wrapper
│   ├── publish/
│   │   ├── twitter_reply.py      # Apify twitter-poster (reply mode)
│   │   ├── reddit_comment.py     # Reddit API comment endpoint
│   │   ├── linkedin_comment.py   # Apify linkedin-poster (comment mode)
│   │   ├── discord_reply.py      # Discord Bot API message
│   │   └── telegram_reply.py     # Telegram Bot API
│   ├── crm/
│   │   ├── models.py             # SQLAlchemy models for CRM tables
│   │   ├── tracker.py            # Relationship progression logic
│   │   └── digest.py             # Daily CRM digest generator
│   ├── safety/
│   │   ├── rate_limiter.py       # Redis-based per-platform rate limits
│   │   ├── blocklist.py          # Account/keyword blocklist
│   │   ├── content_filter.py     # Regex guardrails (no FA, no price predictions)
│   │   └── kill_switch.py        # Emergency stop via Telegram command
│   ├── approval/
│   │   └── telegram_queue.py     # Founder approval bot for Tier 1/2
│   ├── keywords.json             # Discovery keywords by persona
│   ├── config.py
│   └── orchestrator.py
├── migrations/
│   └── 001_crm_tables.sql        # CRM schema
├── tests/
├── .env.example
├── pyproject.toml
├── Dockerfile
└── README.md
