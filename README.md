# fabric-ontology-export

**The problem.** A Fabric IQ ontology is useful inside Fabric — Copilot, Data Agents, IQ queries.
Outside Fabric it is a JSON envelope nobody can read. The architect wants a diagram for the
review. The Power BI developer wants the relationships without redrawing them. The knowledge-graph
team wants RDF. Today each of them rebuilds the same model by hand.

**What this does.** Reads the ontology item definition (the envelope from *Get Item Definition*,
or straight from [sap-ontology](https://github.com/Krusmaster/sap-ontology)) and exports it:

```
fabric-ontology-export ontology.json --format mermaid   # ER diagram, with keys marked
fabric-ontology-export ontology.json --format tmdl      # Power BI relationship snippets
fabric-ontology-export ontology.json --format turtle    # RDF/OWL for graph tooling
```

```
relationship VBAP_VBELN_VBAK
	fromColumn: VBAP.VBELN
	toColumn: VBAK.VBELN
	crossFilteringBehavior: oneDirection
```

The parser is tolerant of the preview format: it reads `EntityTypes/*/definition.json`,
`DataBindings` and `RelationshipTypes` and ignores the rest.

## Install

```
pip install git+https://github.com/Krusmaster/fabric-ontology-export
```

## Works on

| Platform | Status |
| --- | --- |
| Fabric | yes — input is a Fabric IQ ontology definition |
| Databricks / Snowflake | not applicable as input; the RDF/Mermaid/TMDL outputs are platform-neutral |
| Local Python | yes |

## License

MIT
