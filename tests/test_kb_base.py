from research_town.kb_base import BaseKnowledgeBase

def test_get_data():
    kb = BaseKnowledgeBase()
    data = kb.get_data(10, "Machine Learning")
    assert data is not None
    assert len(data) <= 10 and len(data) > 0