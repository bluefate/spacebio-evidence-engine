"""Experimental gazetteer for graph extraction (issue #74). Not a production ontology."""

from __future__ import annotations

# Longer phrases first so "skeletal muscle" wins over "muscle".
GAZETTEER: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("Organism", "human", "human", ("astronauts", "astronaut", "human")),
    ("Organism", "mouse", "mouse", ("mice", "mouse", "murine")),
    ("Organism", "rat", "rat", ("rats", "rat")),
    (
        "AnatomicalStructure",
        "skeletal muscle",
        "",
        ("skeletal muscle", "skeletal muscles"),
    ),
    ("AnatomicalStructure", "soleus", "", ("soleus",)),
    ("CellType", "myeloid", "", ("myeloid",)),
    (
        "Exposure",
        "hindlimb unloading",
        "",
        ("hindlimb unloading", "hindlimb suspension"),
    ),
    ("Exposure", "spaceflight", "", ("spaceflight", "iss")),
    ("Exposure", "microgravity", "", ("microgravity", "simulated microgravity")),
    ("Exposure", "radiation", "", ("radiation",)),
    (
        "Intervention",
        "exercise preconditioning",
        "",
        ("exercise preconditioning",),
    ),
    ("Assay", "proteomics", "", ("proteome", "proteomics")),
    ("Outcome", "atrophy", "", ("atrophy",)),
    ("Outcome", "infiltration", "", ("infiltration",)),
)
