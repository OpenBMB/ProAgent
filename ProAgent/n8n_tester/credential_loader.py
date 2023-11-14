import os
import json
from typing import Dict, Any

class Credentials():
    def __init__(self, base_file_path= "./ProAgent/n8n_tester/credentials"):
        """
        Initializes the object with the given base file path. If no base file path is provided,
        the default path "./ProAgent/n8n_tester/credentials" will be used.

        Parameters:
            base_file_path (str): The base file path to the credentials directory. Defaults to
                                  "./ProAgent/n8n_tester/credentials".

        Return:
            None
        """
        with open(os.path.join(base_file_path,"c.json"),"r") as reader:
            credential_data = json.load(reader)
            self.credential_data: Dict[str,Any] = {}
            for item in credential_data:
                item_info = {
                    "name": item["name"],
                    "id": item["id"],
                    "type": item["type"],
                }
                for node_type in item["nodesAccess"]:
                    node_type_name = node_type["nodeType"].split(".")[-1]
                    if self.credential_data.get(node_type_name,-1) == -1:
                        self.credential_data[node_type_name] = []
                    self.credential_data[node_type_name].append(item_info)
        with open(os.path.join(base_file_path,"w.json"),"r") as reader:
            workflow_data = json.load(reader)
            self.workflow_id = workflow_data[0]["id"]
                
    def get_workflow_id(self) -> str:
        """
        Get the workflow ID.
        :return: The workflow ID.
        :rtype: str
        """
        return self.workflow_id

    def query(self, node_type):
        """
        Retrieves the last element of the credential data associated with the given node type.

        Parameters:
            node_type (str): The type of node.

        Returns:
            The last element of the credential data associated with the given node type, or None if the node type is not found.
        """
        if self.credential_data.get(node_type,-1) == -1:
            return None
        return self.credential_data[node_type][-1]
 
credentials = Credentials()