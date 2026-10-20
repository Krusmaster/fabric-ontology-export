"""Parse a Fabric IQ Ontology item definition (the envelope from Get Item Definition or from
sap-ontology) and export it as Mermaid, Power BI relationship TMDL snippets, or RDF/Turtle.

Format caveat: the Ontology item is in preview. The parser is tolerant — it reads what it finds
under EntityTypes/*/definition.json and RelationshipTypes/*/definition.json and ignores the rest.
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Entity:
    id: int
    name: str
    namespace: str = ""
    description: str = ""
    keys: list[str] = field(default_factory=list)
    properties: dict[str, str] = field(default_factory=dict)   # name -> valueType
    table: str | None = None                                    # bound lakehouse table, if any


@dataclass
class Relationship:
    id: int
    name: str
    source: int
    target: int


@dataclass
class Ontology:
    name: str
    entities: dict[int, Entity] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)

    def entity_by_name(self, name: str) -> Entity:
        return next(e for e in self.entities.values() if e.name == name)


def _parts(env: dict) -> dict[str, dict]:
    out = {}
    for p in env.get("definition", {}).get("parts", []):
        if p.get("payloadType", "InlineBase64") == "InlineBase64":
            try:
                out[p["path"]] = json.loads(base64.b64decode(p["payload"]))
            except Exception:
                continue
    return out


def load_definition(src: str | Path | dict) -> Ontology:
    env = src if isinstance(src, dict) else json.loads(Path(src).read_text(encoding="utf-8"))
    parts = _parts(env)
    onto = Ontology(name=env.get("displayName", "ontology"))

    for path, obj in parts.items():
        seg = path.split("/")
        if seg[0] == "EntityTypes" and seg[-1] == "definition.json":
            props = {p["name"]: p.get("valueType", "String") for p in obj.get("properties", [])}
            pid = {p["id"]: p["name"] for p in obj.get("properties", [])}
            keys = [pid[k] for k in obj.get("keyPropertyIds", []) if k in pid]
            onto.entities[obj["id"]] = Entity(obj["id"], obj["name"], obj.get("namespace", ""),
                                              obj.get("description", ""), keys, props)
    for path, obj in parts.items():
        seg = path.split("/")
        if seg[0] == "EntityTypes" and len(seg) >= 4 and seg[2] == "DataBindings":
            eid = int(seg[1])
            if eid in onto.entities:
                onto.entities[eid].table = obj.get("source", {}).get("sourceTableName")
        if seg[0] == "RelationshipTypes" and seg[-1] == "definition.json":
            onto.relationships.append(Relationship(obj["id"], obj["name"],
                                                   obj["source"]["entityTypeId"], obj["target"]["entityTypeId"]))
    return onto


def to_mermaid(onto: Ontology) -> str:
    lines = ["erDiagram"]
    for e in onto.entities.values():
        lines.append(f"    {e.name} {{")
        for n, t in e.properties.items():
            pk = " PK" if n in e.keys else ""
            lines.append(f"        {t} {n}{pk}")
        lines.append("    }")
    for r in onto.relationships:
        a, b = onto.entities[r.source].name, onto.entities[r.target].name
        lines.append(f'    {a} }}o--|| {b} : "{r.name}"')
    return "\n".join(lines)


def to_powerbi_relationships(onto: Ontology) -> str:
    """TMDL relationship snippets (many-to-one from source key to target key, first key column)."""
    out = []
    for r in onto.relationships:
        s, t = onto.entities[r.source], onto.entities[r.target]
        if not t.keys:
            continue
        col = t.keys[0]
        if col not in s.properties:
            continue
        out.append(f"relationship {r.name}\n\tfromColumn: {s.name}.{col}\n\ttoColumn: {t.name}.{col}\n\tcrossFilteringBehavior: oneDirection\n")
    return "\n".join(out)


_XSD = {"String": "xsd:string", "BigInt": "xsd:long", "Double": "xsd:double",
        "Boolean": "xsd:boolean", "DateTime": "xsd:dateTime", "Object": "xsd:string"}


def to_turtle(onto: Ontology, base: str = "http://example.org/ontology/") -> str:
    lines = [f"@prefix : <{base}> .", "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
             "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
             "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .", ""]
    for e in onto.entities.values():
        lines.append(f":{e.name} a owl:Class ;")
        lines.append(f'    rdfs:label "{e.name}"' + (f' ;\n    rdfs:comment "{e.description}"' if e.description else "") + " .")
        for n, t in e.properties.items():
            lines.append(f":{e.name}_{n} a owl:DatatypeProperty ; rdfs:domain :{e.name} ; rdfs:range {_XSD.get(t, 'xsd:string')} .")
        lines.append("")
    for r in onto.relationships:
        a, b = onto.entities[r.source].name, onto.entities[r.target].name
        lines.append(f":{r.name} a owl:ObjectProperty ; rdfs:domain :{a} ; rdfs:range :{b} .")
    return "\n".join(lines)
