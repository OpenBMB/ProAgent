import subprocess
import tempfile
import json
import traceback
from typing import Optional
import uuid

from termcolor import colored

from ProAgent.n8n_tester.credential_loader import credentials
from ProAgent.n8n_parser.node import n8nPythonNode, n8nNodeMeta
from ProAgent.n8n_tester.pseudo_node.run_pseudo_node import run_pseudo_workflow
from ProAgent.utils import NodeType
from ProAgent.n8n_tester.prompts import success_prompt, error_prompt

class n8nRunningException(Exception):
    """封装报错类型，可以重载自己定义的错误类型，只需要说出来 error-message 比如：
    1.mainWorkflow只能由trigger调用
    2.所有action node的输入都是[{}]格式的
    """

    def __init__(self, message ):
        super().__init__(message)
        self.code_stack = []
        self.error_message = ""


    def add_context_stack(self, code_context):
        """
        Adds a code context to the code stack.

        Parameters:
            code_context (any): The code context to be added to the stack.

        Returns:
            None
        """
        self.code_stack.append(code_context)
        pass

class anonymous_class():
    def __init__(self, node: n8nPythonNode,*args, **kwargs):
        self.node = node

    def run(self, input_data, params):
        """
        Run the function with the given input data and parameters.

        Args:
            input_data (any): The input data for the function.
            params (dict): The parameters for the function.

        Returns:
            any: The output data from the function.

        Raises:
            n8nRunningException: If there is an error while running the function.
        """

        output_data, error = run_node(node=self.node, input_data=input_data)
        if error != "":
            my_error = n8nRunningException(error)
            raise my_error
        else:
            return output_data

def _get_constant_workflow(input_data):
    """
    Generates a constant workflow based on the provided input data.
    
    Parameters:
        input_data (Any): The input data to be used in the workflow.
        
    Returns:
        Dict: The generated workflow.
    """
    # node trigger
    node_trigger_id = str(uuid.uuid4())
    node_trigger = {
        "id": node_trigger_id,
        "name": "Execute Workflow Trigger",
        "type": "n8n-nodes-base.executeWorkflowTrigger",
        "typeVersion": 1,
        "position": [0, 0],
        "parameters": {}
    }
    node_trigger_name = str(node_trigger["name"])
    # node code
    node_code_id = str(uuid.uuid4())
    node_code_jsCode = f"return {json.dumps(input_data)}"
    node_code = {
        "id": node_code_id,
        "name": "Code",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [180, 0],
        "parameters": {
            "jsCode": node_code_jsCode
        }
    }
    node_code_name = str(node_code["name"])

    node_var = {
        "id": str(uuid.uuid4()),
        "name": "node_var",
        "position": [360, 0],
    }

    workflow_connection = dict({
        node_trigger_name: {
            "main": [
                [
                    {
                        "node": node_code_name,
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        node_code_name: {
            "main": [
                [
                    {
                        "node": node_var["name"],
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    })
    
    workflow_nodes = [node_trigger,node_code, node_var]

    workflow_versionId = str(uuid.uuid4())
    workflow_name = "Simple Workflow"
    workflow = {
        # "id": workflow_id,
        "versionId": workflow_versionId,
        "name": workflow_name,
        "nodes": workflow_nodes,
        "connections": workflow_connection,
        "active": False,
        "settings": {
            "executionOrder": "v1"
        },
        "tags": []
    }

    return workflow

def run_node(node: n8nPythonNode, input_data: list[dict] = [{}]) -> tuple[str, str]:
    """Execute a specified node.

    Args:
        workflow_id (Optional[str], optional): ID of the workflow in which the node is located. The workflow ID must be in your n8n workflow database. You could create a workflow and pick that id. If not provided, the default workflow will be used. Defaults to None.
        node (Optional[dict], optional): n8n node json dictionary. If not provided, the default slack send message node will be used. Defaults to None.
        input_data (list[dict], optional): Input data for the node. Defaults to [{}].

    Returns:
        tuple[str, str]: A tuple containing two strings. The first string represents the status of the node execution (e.g., "success", "failure"), and the second string provides additional information or error messages related to the execution.
    """
    # problem: execute parallelly
    constant_workflow = _get_constant_workflow(input_data=input_data)

    constant_workflow["id"] = credentials.get_workflow_id()
    node_var = constant_workflow["nodes"][-1]
    node_var["type"] = "n8n-nodes-base." + node.node_meta.integration_name

    if credentials.query(node.node_meta.integration_name) != None:
        credential_item = credentials.query(node.node_meta.integration_name)
        node_var["credentials"] = {
            credential_item["type"]: {
                "id": credential_item["id"],
                "name": credential_item["name"],
            }
        }

    param_json = {}
    for key, value in node.params.items():
        param = value.to_json()
        if param != None:
            param_json[key] = param
    
    if 'json' in input_data[0].keys():
        node_var['parameters'] = input_data[0]['json']
        node_var["parameters"].update(param_json)
    else:
        node_var["parameters"] = param_json


    node_var["parameters"]["operation"] = node.node_meta.operation_name
    node_var["parameters"]["resource"] = node.node_meta.resource_name

    if node.node_meta.integration_name == 'slack':
        node_var["parameters"]["authentication"] = "oAuth2"
        
    if node.node_meta.integration_name == 'googleSheets':
        node_var["parameters"]["operation"] = node.node_meta.operation_name
        node_var["typeVersion"] = 4
        node_var["parameters"]["columns"] = {
                    "mappingMode": "autoMapInputData",
                    "value": {},
                    "matchingColumns": [
                      "id"
                    ]
                }


    # handle workflow
    if 'pseudoNode' in node.node_json.keys() and node.node_json['pseudoNode']:
        try:
            # import pdb; pdb.set_trace()
            output = run_pseudo_workflow(input_data, constant_workflow)
            error= ""
        except BaseException as e:
            traceback.print_exc()
            print(e)
            raise e
    else:
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json")
        json.dump(constant_workflow, temp_file)
        temp_file.close()
        temp_file_path = temp_file.name
        # import pdb; pdb.set_trace()
        result = subprocess.run(["n8n", "execute", "--file", temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        # Get the standard output
        output = result.stdout.decode('utf-8')
        error = result.stderr.decode('utf-8')

    print(colored("###OUTPUT###", color="green"))
    print(colored(output, color="green"))

    print(colored("###ERROR###", color="red"))
    print(colored(error, color="red"))

    output_data = ""
    error = ""

    # check input data
    if input_data == None or len(input_data) == 0:
        warning_prompt = "WARNING: There is nothing in input_data. This may cause the failure of current node execution.\n"
        print(colored(warning_prompt, color='yellow'))
        output_data += warning_prompt

    if success_prompt in output:
        output_data = output.split(success_prompt)[-1]
    else:
        assert error_prompt in output_data
        outputs = output.split(error_prompt)
        assert len(outputs) == 2
        output_data = outputs[0]
        error = outputs[1].strip()

    if output_data != "":
        output_data = json.loads(output_data)
        output_data = output_data["data"]["resultData"]["runData"]["node_var"][0]["data"]["main"][0]
    else:
        output_data = []

    return output_data, error