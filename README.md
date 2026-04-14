# CryptoPrism Social Engagement Engine

An autonomous AI-driven engagement system designed to build relationships with crypto stakeholders through organic, data-backed conversations.

## 🚀 The Philosophy: "Signal Before Product"

The crypto community is resistant to traditional advertisements. This engine moves away from broadcasting and moves toward **genuine interaction**. By providing real-time on-chain insights and helpful data drops, we convert strangers into beta testers and brand advocates.

## 🧠 Core Architecture: 6-Agent Pipeline

The system operates through a modular pipeline managed by synchronized AI agents:

1.  **Discovery Agent**: Scans Discord (and soon Twitter/Reddit) for high-intent keywords like "MVRV", "on-chain", and competitor mentions.
2.  **Profile Classifier**: (In Progress) Scores authors and assigns them to Persona Tiers (Tier 1 Analysts vs. Tier 2 Competitor Users).
3.  **LLM Responder**: Generates highly contextual replies using model-agnostic interfaces (currently powered by Ollama/Llama3).
4.  **Interaction Publisher**: Posts replies with human-mimicking delay logic to evade anti-spam filters.
5.  **Relationship Tracker (CRM)**: Logs every interaction to track community sentiment and conversion.
6.  **Engagement Analytics**: Daily reviews of outcomes to optimize targeting heuristics.

## 🛠️ Tech Stack

- **Core**: Python 3.11+
- **Discord**: `discord.py` (Gateway Intents enabled)
- **AI/LLM**: Ollama (local) with support for model-agnostic providers (Claude/OpenAI ready)
- **Networking**: `aiohttp` for non-blocking async LLM requests
- **Config**: `python-dotenv` for secure environment management

## 🚦 Getting Started

### Prerequisites

1.  **Python 3.11+**
2.  **Ollama**: Install and run locally ([ollama.com](https://ollama.com))
    ```bash
    ollama run llama3
    ```

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Skywalker1080/cpio-engagement-engine.git
    cd cpio-engagement-engine
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt  # Or manually: pip install discord.py python-dotenv aiohttp
    ```

3.  **Configure `.env`**:
    Create a `.env` file in the root directory:
    ```env
    # Discord Credentials
    APP_ID="your_app_id"
    DISCORD_TOKEN="your_bot_token"
    PUBLIC_KEY="your_public_key"

    # LLM Settings
    LLM_PROVIDER="ollama"
    OLLAMA_MODEL="llama3"
    OLLAMA_HOST="http://localhost:11434"
    ```

4.  **Run the Engine**:
    ```bash
    python main.py
    ```

## 🛡️ Safety & Anti-Spam Guardrails

- **Value-First Rule**: The AI only speaks if it can add specific data or insight.
- **Human Speed**: Built-in randomized delays (2-8 seconds) to mimic human typing.
- **Content Filtering**: Strictly forbids financial advice, price predictions, or typical "moon" buzzwords.
- **Emergency Kill Switch**: (Planned) Centralized management via Telegram.

## 📁 Project Structure

- `src/scrapers/`: Gateway monitors and platform scanners.
- `src/agents/`: Logic for discovery, classification, and response generation.
- `src/publish/`: Platform-specific posting implementations.
- `src/orchestrator.py`: The glue connecting the ingestion path to the response path.
- `docs/project_logs.md`: Detailed history of development milestones.

---
*Built for CryptoPrism.io*
