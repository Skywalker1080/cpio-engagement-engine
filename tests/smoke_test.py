"""Quick smoke test — runs the pipeline in-memory (no Discord connection)."""

from src.scrapers.discord_monitor import _build_keyword_index, find_keyword_matches
from src.agents.discovery import evaluate_message
from src.agents.responder import generate_reply
from src.config import load_keywords


def main():
    # Load keywords
    kw = load_keywords()
    idx = _build_keyword_index(kw)
    print(f"Loaded {len(idx)} keywords across {len(kw)} categories\n")

    # Simulate a message
    test_msg = "What do you think about MVRV ratio? Glassnode shows interesting data"
    print(f"Test message: {test_msg!r}\n")

    # Keyword matching
    matches = find_keyword_matches(test_msg, idx)
    print(f"Keyword matches: {matches}\n")

    # Discovery — score the signal
    signal = evaluate_message(test_msg, "TestUser", "general", matches)
    print(f"Signal score: {signal['score']}")
    print(f"Is question: {signal['is_question']}")
    print(f"Categories:  {signal['categories']}\n")

    # Responder — generate reply
    reply = generate_reply(signal)
    print(f"Generated reply:\n  {reply}\n")

    print("--- SMOKE TEST PASSED ---")


if __name__ == "__main__":
    main()
