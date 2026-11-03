from app.ai.agent import write_reply, write_reply_async
from app.ai.classifier import classify, classify_async
from app.ai.rules import CUSTOMER_STEPS, resolve_issue
from app.ai.schemas import AgentReply, Classification, Decision


def decide(thread: str, has_attachments: bool = False) -> Decision:
    """Run the AI steps for one email thread. The models propose, this function decides."""
    classification = classify(thread)
    decision = _early_decision(classification, has_attachments)
    if decision is not None:
        return decision
    return _finish_decision(classification, write_reply(thread, classification.section))


async def decide_async(thread: str, has_attachments: bool = False) -> Decision:
    """Run the pipeline on the current event loop for concurrent evaluations."""
    classification = await classify_async(thread)
    decision = _early_decision(classification, has_attachments)
    if decision is not None:
        return decision
    answer = await write_reply_async(thread, classification.section)
    return _finish_decision(classification, answer)


def _escalate(classification: Classification, reason: str, proposed_action: str | None = None) -> Decision:
    return Decision(
        action="escalate",
        section=classification.section,
        reply=classification.acknowledgement,
        reason=reason,
        proposed_action=proposed_action,
    )


def _early_decision(classification: Classification, has_attachments: bool) -> Decision | None:
    if has_attachments:
        return _escalate(classification, "The email has attachments")
    if classification.needs_human:
        return _escalate(classification, classification.reason)
    return None


def _finish_decision(classification: Classification, answer: AgentReply) -> Decision:
    if answer.action == "escalate":
        return _escalate(classification, answer.reasoning)
    if not answer.enough_information:
        return _escalate(classification, "The knowledge base does not answer this")
    if answer.issue:
        step = resolve_issue(answer.issue)
        if step not in CUSTOMER_STEPS:
            return _escalate(classification, f"Next step: {step}", proposed_action=step)
    if answer.promises_an_action:
        return _escalate(classification, "The reply promises an action")

    return Decision(
        action="reply",
        section=classification.section,
        reply=answer.reply,
        reason=answer.reasoning,
    )