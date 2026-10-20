import base64, json
from fabric_ontology_export import load_definition, to_mermaid, to_powerbi_relationships, to_turtle


def _b(o): return base64.b64encode(json.dumps(o).encode()).decode()

ENV = {"displayName": "t", "type": "Ontology", "definition": {"parts": [
    {"path": "EntityTypes/1/definition.json", "payload": _b({"id": 1, "name": "VBAK", "description": "Sales header",
        "keyPropertyIds": [11], "properties": [{"id": 11, "name": "VBELN", "valueType": "String"}, {"id": 12, "name": "NETWR", "valueType": "Double"}]}), "payloadType": "InlineBase64"},
    {"path": "EntityTypes/1/DataBindings/x.json", "payload": _b({"source": {"sourceTableName": "vbak"}}), "payloadType": "InlineBase64"},
    {"path": "EntityTypes/2/definition.json", "payload": _b({"id": 2, "name": "VBAP",
        "keyPropertyIds": [21, 22], "properties": [{"id": 21, "name": "VBELN", "valueType": "String"}, {"id": 22, "name": "POSNR", "valueType": "String"}]}), "payloadType": "InlineBase64"},
    {"path": "RelationshipTypes/9/definition.json", "payload": _b({"id": 9, "name": "VBAP_VBELN_VBAK", "source": {"entityTypeId": 2}, "target": {"entityTypeId": 1}}), "payloadType": "InlineBase64"},
    {"path": "definition.json", "payload": _b({}), "payloadType": "InlineBase64"},
]}}


def test_load():
    o = load_definition(ENV)
    assert set(e.name for e in o.entities.values()) == {"VBAK", "VBAP"}
    assert o.entity_by_name("VBAK").table == "vbak" and o.entity_by_name("VBAP").keys == ["VBELN", "POSNR"]
    assert len(o.relationships) == 1


def test_mermaid():
    m = to_mermaid(load_definition(ENV))
    assert "String VBELN PK" in m and "VBAP }o--|| VBAK" in m


def test_tmdl():
    t = to_powerbi_relationships(load_definition(ENV))
    assert "fromColumn: VBAP.VBELN" in t and "toColumn: VBAK.VBELN" in t


def test_turtle():
    t = to_turtle(load_definition(ENV))
    assert ":VBAK a owl:Class" in t and ":VBAK_NETWR a owl:DatatypeProperty ; rdfs:domain :VBAK ; rdfs:range xsd:double" in t
    assert ":VBAP_VBELN_VBAK a owl:ObjectProperty" in t
