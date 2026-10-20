"""fabric-ontology-export: read a Fabric IQ Ontology definition and export it to other formats."""
from .core import Ontology, load_definition, to_mermaid, to_powerbi_relationships, to_turtle

__all__ = ["Ontology", "load_definition", "to_mermaid", "to_powerbi_relationships", "to_turtle"]
__version__ = "0.1.0"
