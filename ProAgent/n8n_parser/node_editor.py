
import json
import os
node_json_path = "./pseudo_nodes_json/ai.json"
nodes_json_path = "nodes.json"

# print(test[1560:1570])

with open(os.path.join(node_json_path), "r", encoding="utf-8") as fr: 
    node_json:dict = json.load(fr)

with open(os.path.join(nodes_json_path), "r", encoding="utf-8") as fr:
    nodes_json:list = json.load(fr)

for integration_json in nodes_json:
    name = integration_json["name"].split(".")[-1]
    if name not in node_json['name']:
        continue
    nodes_json.remove(integration_json)

nodes_json.append(node_json)

with open(os.path.join(nodes_json_path), "w", encoding="utf-8") as fw:
    json.dump(nodes_json, fw, indent=4)