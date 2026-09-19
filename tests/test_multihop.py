from src.agent import answer_question
from src.demo_data import load_demo
from src.knowledge import KnowledgeBase

def test_january_meeting_reaches_customer():
    kb = KnowledgeBase(); docs, links = load_demo(); kb.ingest(docs, links)
    answer = answer_question(kb, "Which customer was affected by the decision made in the January product planning meeting?")
    assert "Customer One" in answer.text
    assert answer.chain == ["Product Planning - January 12", "Migrate checkout system", "PAY-142", "Customer One"]
