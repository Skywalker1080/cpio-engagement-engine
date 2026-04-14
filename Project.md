### Project Overview: CryptoPrism Social Engagement Engine

The project is building an **autonomous AI-driven Social Engagement Engine** for CryptoPrism.io. Unlike traditional marketing tools that broadcast advertisements, this system is designed to seamlessly discover, engage with, and build relationships with crypto stakeholders in one-on-one conversations across Twitter, Reddit, LinkedIn, Discord, and Telegram. 

The core philosophy of the engine is **"Signal before product"**. Because the crypto community is highly resistant to traditional paid ads (averaging a 0.3% click-through rate), the system relies purely on organic engagement, which has proven to be 27 times more efficient. The ultimate goal is to interact 50+ times a day by providing genuine, data-backed value to turn strangers into beta testers, customers, and brand advocates.

---

### Core Architecture: The 6-Agent Pipeline
The system operates through a continuous, automated pipeline powered by six distinct AI agents managed by Claude:

1.  **Discovery Agent:** Scans the target platforms every 30 to 120 minutes using keyword searches (e.g., "MVRV," "on-chain") and competitor mentions to find conversations worth joining.
2.  **Profile Classifier:** Evaluates the author of the discovered post, assigns them an engagement score out of 100, and categorizes them into a specific persona tier (such as a Tier 1 CT Analyst or a Tier 2 Frustrated Competitor User).
3.  **Response Generator:** Uses CryptoPrism’s real-time data to craft a highly contextual reply. It maps the conversation to one of **8 response archetypes** (like "Data Drop," "Pattern Spotter," or "Polite Correction") to ensure the reply is helpful and not promotional.
4.  **Interaction Publisher:** Posts the finalized reply or comment to the respective platform utilizing Apify actors or direct APIs.
5.  **Relationship Tracker (CRM):** Logs the interaction in a PostgreSQL database to map the ongoing relationship, helping the team know when to follow up or send a direct message with a beta invite.
6.  **Engagement Analytics:** Reviews the outcomes of these interactions daily (e.g., response rates, profile visits) to optimize future targeting.

---

### Strict Anti-Spam Guardrails & Safety
To prevent being banned or labeled as spam by the notoriously skeptical crypto community, the project enforces strict safety measures:

*   **Value First Rule:** Every single reply must contain a specific piece of data or insight that the original author didn't have. If the AI cannot add genuine value, it is programmed to remain silent.
*   **Human-in-the-Loop:** For high-value targets (Tier 1 and Tier 2 personas), the AI does not post automatically. Instead, it queues the drafted response in a Telegram bot for the founder to manually review and approve.
*   **Human Speed & Randomization:** The publisher operates with built-in delays, never replying instantly, and uses randomized intervals to mimic natural human behavior.
*   **Content Filters:** The system explicitly forbids giving financial advice, predicting prices, or using buzzwords like "bullish" or "bearish". 
*   **Emergency Kill Switch:** The founder can immediately halt all engagement across all platforms by sending a `/stop` command to the Telegram bot if market conditions crash or a bug is detected.