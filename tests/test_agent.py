from src.agent import UNKNOWN, answer_question
from src.knowledge import KnowledgeBase

def test_empty_knowledge_is_honest():
    assert answer_question(KnowledgeBase(), "Anything?").text == UNKNOWN
