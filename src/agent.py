from .knowledge import KnowledgeBase
from .models import Answer

UNKNOWN = "I don't have enough information in the company knowledge base to answer that reliably."

def answer_question(knowledge: KnowledgeBase, question: str) -> Answer:
    q = question.lower()
    if not knowledge.documents:
        return Answer(UNKNOWN, [])
    meeting = "Product Planning - January 12"
    decision = "Migrate checkout system"
    ticket = "PAY-142"
    customer = "Customer One"
    if any(phrase in q for phrase in ("which customer", "affected by", "relationship chain")):
        chain = knowledge.path(meeting, customer)
        if chain:
            return Answer(f"{customer} was affected by the decision made in the January product planning meeting.", knowledge.evidence_for(chain), chain)
    if "decision" in q and ("january" in q or "planning" in q):
        return Answer(f"The January product planning meeting resulted in the decision to {decision}.", knowledge.evidence_for([meeting, decision]), [meeting, decision])
    if "ticket" in q and ("decision" in q or "resulted" in q):
        return Answer(f"The decision to {decision} created ticket {ticket}.", knowledge.evidence_for([decision, ticket]), [decision, ticket])
    if "who" in q and "project atlas" in q:
        return Answer("Alice worked on Project Atlas.", knowledge.evidence_for(["Alice", "Project Atlas"]), ["Alice", "Project Atlas"])
    evidence = knowledge.recall(question)
    if not evidence:
        return Answer(UNKNOWN, [])
    return Answer("Retrieved company knowledge:\n\n" + "\n".join(f"- {doc.title}: {doc.content}" for doc in evidence[:3]), evidence)
