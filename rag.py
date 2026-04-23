import json

def load_knowledge_base(path="knowledge_base.json"):
    with open(path, "r") as f:
        return json.load(f)

def retrieve_context(query: str) -> str:
    """
    Simple keyword-based RAG retrieval from local knowledge base.
    Returns a formatted string of relevant information.
    """
    kb = load_knowledge_base()
    query_lower = query.lower()
    results = []

    # Pricing / plan queries
    if any(word in query_lower for word in ["price", "pricing", "cost", "plan", "basic", "pro", "how much", "pay", "subscription"]):
        plans = kb["plans"]
        results.append("=== AutoStream Pricing Plans ===")
        results.append(
            f"BASIC PLAN: {plans['basic']['price']} | {plans['basic']['videos']} | "
            f"{plans['basic']['resolution']} resolution | No AI captions | {plans['basic']['support']}"
        )
        results.append(
            f"PRO PLAN: {plans['pro']['price']} | {plans['pro']['videos']} | "
            f"{plans['pro']['resolution']} resolution | AI captions included | {plans['pro']['support']}"
        )

    # Policy queries
    if any(word in query_lower for word in ["refund", "cancel", "policy", "return", "money back"]):
        results.append(f"=== Refund Policy ===\n{kb['policies']['refund']}")

    if any(word in query_lower for word in ["support", "help", "contact", "24/7"]):
        results.append(f"=== Support Policy ===\n{kb['policies']['support']}")

    # General / feature queries
    if any(word in query_lower for word in ["feature", "caption", "4k", "resolution", "video", "edit", "autostream", "what is", "tell me"]):
        results.append(f"=== About AutoStream ===\n{kb['company']['tagline']}")
        results.append("Features: Automated video editing, AI captions (Pro), up to 4K export, batch processing.")

    if not results:
        # Return everything as fallback
        results.append("=== AutoStream Overview ===")
        results.append(f"{kb['company']['tagline']}")
        results.append("Plans: Basic ($29/mo, 10 videos, 720p) | Pro ($79/mo, unlimited, 4K, AI captions)")
        results.append(f"Policies: {kb['policies']['refund']} | {kb['policies']['support']}")

    return "\n".join(results)