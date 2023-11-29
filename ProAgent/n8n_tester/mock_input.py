import os
from tqdm import tqdm
import json
import atexit
from collections import defaultdict

from ProAgent.n8n_parser.node import n8nPythonNode
from ProAgent.n8n_parser.workflow import n8nPythonWorkflow

class MockInput():
    def __init__(self, mock_pair_dir = "./ProAgent/n8n_tester/mock_pairs", persist_on_destruction=False):
        """
        Initializes the class instance.

        Parameters:
            mock_pair_dir (str): The directory path where the mock pairs are stored. Defaults to "./ProAgent/n8n_tester/mock_pairs".
            persist_on_destruction (bool): Flag indicating whether to persist the mock data on destruction. Defaults to False.
        """
        self.mock_pair_dir = mock_pair_dir
        atexit.register(self._flash)
        self.persist_on_destruction = persist_on_destruction
        # self.mock_data = {}
        self.mock_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [{}])))
        
        for file_name in tqdm(os.listdir(self.mock_pair_dir),desc="loading all MockInput from Disk"):
            assert file_name.endswith(".json")
            integration_name = file_name.split(".")[0]
            with open(os.path.join(self.mock_pair_dir, file_name), "r", encoding="utf-8") as reader:
                json_data_for_integration = json.load(reader)
                if self.mock_data.get(integration_name, -1) == -1:
                    self.mock_data[integration_name] = {}

                for resource_name, json_data_for_resource in json_data_for_integration.items():
                    if self.mock_data[integration_name].get(resource_name, -1) == -1:
                        self.mock_data[integration_name][resource_name] = {}
                    for operation_name, json_data_for_operation in json_data_for_resource.items():
                        if self.mock_data[integration_name][resource_name].get(operation_name, -1) == -1:
                            self.mock_data[integration_name][resource_name][operation_name] = []
                            for data_pair in json_data_for_operation:
                                self.mock_data[integration_name][resource_name][operation_name].append(data_pair)

    def _flash(self):
        """
        Persists the mock input dictionary if self.persist_on_destruction is True.
        
        This function iterates over the items in the `self.mock_data` dictionary and
        writes each item to a JSON file in the `self.mock_pair_dir` directory. The
        JSON files are named after the corresponding integration.
        
        Parameters:
            None
        
        Returns:
            None
        """
        if not self.persist_on_destruction:
            return
        
        print("persisting mock input dictionary")
        for integration, val in self.mock_data.items():
            try:
                with open(os.path.join(self.mock_pair_dir, integration + '.json'), "w", encoding="utf-8") as writer:
                    json.dump(val, writer, indent=4)
            except Exception as e:
                print(e)

    def get_node_example_input(self, target_node: n8nPythonNode, top_k: int = 2) -> list:
        """
        Generate the example input for a given n8nPythonNode.

        Args:
            target_node (n8nPythonNode): The target node for which to generate the example input.
            top_k (int, optional): The number of example inputs to generate. Defaults to 2.

        Returns:
            list: A list of example inputs for the target node.
        """

        integration_name, resource_name, operation_name = target_node.node_meta.integration_name, target_node.node_meta.resource_name, target_node.node_meta.operation_name
        return self.mock_data[integration_name][resource_name][operation_name]

    def register_node_example_input(self, target_node: n8nPythonNode, target_input):
        """
        Register an example input for a given target node.

        Args:
            target_node (n8nPythonNode): The target node to register the example input for.
            target_input: The example input to register.

        Returns:
            None
        """

        integration_name, resource_name, operation_name = target_node.node_meta.integration_name, target_node.node_meta.resource_name, target_node.node_meta.operation_name
        if self.mock_data[integration_name][resource_name][operation_name] == [{}]:
            self.mock_data[integration_name][resource_name][operation_name] = []
        self.mock_data[integration_name][resource_name][operation_name].append(target_input)
