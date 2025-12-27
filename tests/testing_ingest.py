import json
from pathlib import Path
from typing import Any, Dict, List

from pyld import jsonld
from collections import Counter

## Function to load STIX bundle from a JSON file and return the objects
def load_stix_bundle(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return json.load(f).get("objects", [])

#function to tabulate counts of different object types sorted by count
def tabulate_type_counts(type_counts: Counter) -> None:
    print(f"{'Object Type':<25} {'Count':<10}")
    print("-" * 35)
    for obj_type, count in sorted(type_counts.items(), key=lambda item: item[1], reverse=True):
        print(f"{obj_type:<25} {count:<10}")





##data['type'] gives us the type of the data which is bundle
##data['id'] gives us the id of the data bundle

data=load_stix_bundle(Path("/Users/vvithala/NJSecure/orbit/data/enterprise-attack.json"))  # type: ignore

##inventory counts of different types of objects in the data and decide which are first class for our purpose.
objtype_counts = Counter(obj['type'] for obj in data)
print(len(objtype_counts))  # Number of unique object types
print(objtype_counts)



## identifying nodes in the data which are not relationships 
nodes = [obj for obj in data if obj['type'] not in {'relationship'}]
len(nodes)
#inventory counts of nodes
node_type_counts = Counter(obj['type'] for obj in nodes)
tabulate_type_counts(node_type_counts)

#list all tactics in the data
tactics = {obj['name'] for obj in data if obj['type'] == 'x-mitre-tactic'}
print(tactics)
##Tactics are 'Credential Access', 'Discovery', 'Defense Evasion', 'Exfiltration', 'Initial Access', 'Privilege Escalation',
#'Reconnaissance', 'Execution', 'Resource Development', 'Command and Control', 'Collection', 'Lateral Movement', 'Persistence', 'Impact'


##unique relationship types in the data
relationship_types = {obj['relationship_type'] for obj in data if obj['type'] == 'relationship'}
print(relationship_types)

##identify kill-chain phases inside techniques
techniques_with_kill_chain = [obj for obj in data if obj['type'] == 'attack-pattern' and 'kill_chain_phases' in obj]
##Treat technique -> tactic as an edge for kill-chain graph
kill_chain_edges = []
for technique in techniques_with_kill_chain:
    for phase in technique['kill_chain_phases']:
        kill_chain_edges.append((technique['name'], phase['phase_name']))  

kill_chain_edges[:5]  # Display first 5 edges

##Valid triples ('src_type', 'relationship_type', 'target_type') in the data
valid_triples = set()

for obj in data:
    if obj['type'] == 'relationship':
        src = next((o for o in data if o['id'] == obj['source_ref']), None)
        tgt = next((o for o in data if o['id'] == obj['target_ref']), None)
        if src and tgt:
            valid_triples.add((src['type'], obj['relationship_type'], tgt['type'])) 

len(valid_triples)  # Number of unique valid triples
list(valid_triples)[:10]  # Display first 10 valid triples

## whats in a relationship object? code to explore relationship objects
relationship_objects = [obj for obj in data if obj['type'] == 'relationship']
relationship_sample = relationship_objects[0] if relationship_objects else None
relationship_sample  # Display a sample relationship object

nodes = [obj for obj in data if obj['type'] not in {'relationship', 'bundle'}]
len(nodes)  # Number of nodes