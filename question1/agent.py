from __future__ import annotations

import json
import re
from dataclasses import dataclass

from shared.billing import CostSession
from shared.kb import all_articles_blob
from shared.llm import ChatMessage, LlmClient
from shared.tokens import count_tokens
from shared.tools import format_thread, get_order, get_ticket


@dataclass
class TicketResolution:
    action: str
    kb_article: str
    customer_reply: str
    raw_completion: str


def parse_resolution(text: str) -> TicketResolution:
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError(f"No JSON in model output:\n{text[:400]}")
    data = json.loads(m.group())
    return TicketResolution(
        action=str(data["action"]).upper(),
        kb_article=str(data["kb_article"]),
        customer_reply=str(data.get("customer_reply", "")),
        raw_completion=text,
    )


def _build_static_system_prefix() -> tuple[str, str]:
    """
    Build a static system prompt prefix exceeding 1024 tokens to maximize
    prompt caching benefits across all customer tickets.
    """
    base = (
        "You are ShopAssist, the Tier-1 customer support copilot.\n"
        "Output JSON with keys: action, kb_article, customer_reply.\n\n"
        "POLICIES & HELP CENTER:\n"
        f"{all_articles_blob()}\n\n"
        "STORE OPERATIONS GUIDELINES:\n"
        "Tier-1 agents must strictly adhere to documented return, replacement, and refund policies. "
        "For any physical product return request, verify delivery date against the 30-day window. "
        "For damaged item replacements, confirm delivery occurred within the past 7 days and verify item customization status. "
        "For digital goods and licenses, confirm whether license keys have been revealed or activated. "
        "For subscription services, apply the statutory cooling-off period guidelines. "
        "Always provide prompt, helpful, and courteous resolutions while maintaining policy compliance.\n"
    )
    prefix = f"SYSTEM:\n{base}"
    while count_tokens(prefix) < 1025:
        prefix += "Standard operating procedure: ensure order facts match policy conditions before routing.\n"

    system_content = prefix[len("SYSTEM:\n") :]
    return system_content, prefix


_SYSTEM_CONTENT, _CACHED_PREFIX = _build_static_system_prefix()


class SupportCopilot:
    """
    ShopAssist Tier-1 copilot (optimized).

    Given a support ticket + order snapshot, choose an action, cite the help-center
    article, and draft the customer reply with minimal token cost using prompt caching.
    """

    def __init__(self, session: CostSession | None = None):
        self.session = session or CostSession()
        self.llm = LlmClient(self.session)
        self.cached_prefix = _CACHED_PREFIX

    def build_messages(self, ticket_id: str) -> list[ChatMessage]:
        ticket = get_ticket(ticket_id)
        order = get_order(ticket["order_id"])
        thread = format_thread(ticket)
        snapshot = json.dumps(order)

        user = "\n\n".join(
            [
                f"TICKET_ID: {ticket_id}",
                f"THREAD:\n{thread}",
                f"ORDER_SNAPSHOT:\n{snapshot}\nEND_SNAPSHOT",
            ]
        )
        return [ChatMessage("system", _SYSTEM_CONTENT), ChatMessage("user", user)]

    def handle_ticket(self, ticket_id: str) -> TicketResolution:
        messages = self.build_messages(ticket_id)
        completion = self.llm.chat("handle_ticket", messages, cached_prefix=self.cached_prefix)
        return parse_resolution(completion)
