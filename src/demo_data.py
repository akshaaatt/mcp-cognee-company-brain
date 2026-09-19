from .models import Relationship, SourceDocument

def load_demo() -> tuple[list[SourceDocument], list[Relationship]]:
    docs = [
        SourceDocument("meeting-jan-12", "meeting", "Product Planning - January 12", "The Product Planning - January 12 meeting discussed Project Atlas. The meeting resulted in the decision to Migrate checkout system.", {"origin": "demo", "source_name": "january-planning.md"}),
        SourceDocument("decision-checkout", "decision", "Migrate checkout system", "Decision: Migrate checkout system. This decision created ticket PAY-142.", {"origin": "demo", "source_name": "checkout-decision.md"}),
        SourceDocument("ticket-pay-142", "ticket", "PAY-142", "PAY-142 migrates the checkout system for Project Atlas and affects Customer One.", {"origin": "demo", "source_name": "tickets.json"}),
        SourceDocument("project-atlas", "project", "Project Atlas", "Project Atlas is a checkout modernization project. Alice works on Project Atlas.", {"origin": "demo", "source_name": "projects.md"}),
        SourceDocument("person-alice", "person", "Alice", "Alice is an engineer working on Project Atlas.", {"origin": "demo", "source_name": "people.md"}),
        SourceDocument("customer-one", "customer", "Customer One", "Customer One is affected by the checkout migration work.", {"origin": "demo", "source_name": "customers.md"}),
    ]
    links = [
        Relationship("Alice", "works on", "Project Atlas"),
        Relationship("Project Atlas", "discussed in", "Product Planning - January 12"),
        Relationship("Product Planning - January 12", "resulted in", "Migrate checkout system"),
        Relationship("Migrate checkout system", "created", "PAY-142"),
        Relationship("PAY-142", "affects", "Customer One"),
    ]
    return docs, links
