import json
import os

def search_node_name(file_path="./nodes.json", search_name="Spreadsheet File"):
    """
    Search for a node name in a JSON file and return the corresponding information.
    
    Parameters:
        file_path (str): The path to the JSON file (default="./nodes.json").
        search_name (str): The name to search for in the JSON file (default="Spreadsheet File").
    
    Returns:
        dict or None: A dictionary containing the name, resource, and operation of the node if found, 
        or None if the node is not found.
    """
    with open(os.path.join(file_path), "r") as fr:
        nodes_json = json.load(fr)
        for item in nodes_json:
            if search_name.lower() == str(item["displayName"]).lower():
                res_list = []
                op_list = []
                for property in item['properties']:
                    if property["displayName"] == "Resource":
                        res_list += [opt["value"] for opt in property["options"]]
                    elif property["displayName"] == "Operation":
                        op_list += [opt["value"] for opt in property["options"]]
                return {
                        "name": item["name"],
                        "resource": res_list,
                        "operation": op_list
                    }
    return None
