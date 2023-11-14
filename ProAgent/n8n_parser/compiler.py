import omegaconf
import json
from typing import List, Dict
from copy import deepcopy

from termcolor import colored
from ProAgent.router.utils import ENVIRONMENT

from ProAgent.utils import NodeType, ToolCallStatus, Action, WorkflowType, TestResult, RunTimeStatus, TestDataType
from ProAgent.n8n_parser.node import n8nPythonNode, n8nNodeMeta
from ProAgent.n8n_parser.workflow import n8nPythonWorkflow
from ProAgent.n8n_parser.param_parser import parse_properties
from ProAgent.n8n_tester.run_code import n8nPythonCodeRunner
from ProAgent.n8n_parser.intrinsic_functions import mainWorkflow_code
from ProAgent.loggers.logs import print_action_base, print_action_tool
from ProAgent.running_recorder import RunningRecoder
from ProAgent.config import CONFIG



class Compiler():
    """和nodes.json交互，同时存储目前所有的数据结构
    """


    def __init__(self, cfg: omegaconf.DictConfig, recorder: RunningRecoder):
        """
        Initializes the class with the given configuration and recorder.

        Parameters:
            cfg (omegaconf.DictConfig): The configuration object.
            recorder (RunningRecoder): The recorder object.

        Returns:
            None
        """
        self.cfg = cfg
        self.recorder = recorder

        self.nodes: List[n8nPythonNode] = []
        self.trigger_id = 0
        self.action_id = 0
        self.workflows: Dict[n8nPythonWorkflow] = {}
        self.mainWorkflow: n8nPythonWorkflow = n8nPythonWorkflow(
            implement_code = mainWorkflow_code
        )
        self.resolve()

        self.code_runner = n8nPythonCodeRunner()
        self.code_runner.flash( 
            main_workflow = self.mainWorkflow,
            workflows=self.workflows,
            nodes = self.nodes
        )
        self.update_runtime()


    def resolve_integration(self, integration_json):
        """
        Generates a function comment for the given function body.
        
        Args:
            integration_json (dict): A dictionary containing information about the integration.
        
        Returns:
            dict: A dictionary containing the resolved integration data.
        
        Raises:
            AssertionError: If the target resource name is not found in the integration data.
        """
        integration_name = integration_json["name"].split(".")[-1]
        integration_data = {}
        no_resource = True
        no_operation = True
        for property in integration_json["properties"]:
            if property["name"] == "resource":
                for resource in property["options"]:
                    integration_data[resource["value"]] = {}
                no_resource = False
                break

        if no_resource:
            integration_data["default"] = {}
        

        for property in integration_json["properties"]:
            if property["name"] == "operation":
                target_resource_name = "default"
                if "displayOptions" in property.keys():
                    assert "show" in property["displayOptions"].keys() and "resource" in property["displayOptions"]["show"].keys()
                    assert len(property["displayOptions"]["show"]["resource"]) == 1
                    target_resource_name = property["displayOptions"]["show"]["resource"][0]

                    assert target_resource_name in integration_data.keys(), f"{target_resource_name} in {integration_data.keys()}"

                target_resource = integration_data[target_resource_name]
                for operation in property["options"]:
                    operation_name = operation["value"]
                    operation_description = ""
                    if "description" in operation.keys():
                        operation_description = operation["description"]
                    node_type = NodeType.trigger if "trigger" in integration_name.lower() or "webhook" in integration_name.lower() else NodeType.action
                    target_resource[operation_name] = n8nNodeMeta(
                                                                node_type=node_type,
                                                                integration_name=integration_name,
                                                                resource_name=target_resource_name,
                                                                operation_name=operation_name,
                                                                operation_description=operation_description
                                                            )
                    no_operation = False

        if no_operation:
            assert no_resource
            node_type = NodeType.trigger if "trigger" in integration_name.lower() or "webhook" in integration_name.lower() else NodeType.action
            integration_data["default"]["default"] = n8nNodeMeta(
                                                                node_type=node_type,
                                                                integration_name=integration_name,
                                                                resource_name="default",
                                                                operation_name="default",
                                                                operation_description=""
                                                            )

        return integration_data

    def print_flatten_tools(self):
        """
        Generates a function comment for the given function body in a markdown code block with the correct language syntax.

        Returns:
            str: The function comment in markdown format.
        """
        output_description_list = []
        for k1, integration_name in enumerate(list(self.flattened_tools.keys())):
            operation_counter = 1
            data = self.flattened_tools[integration_name]["data"]
            des = self.flattened_tools[integration_name]["meta"]["description"]
            if integration_name in CONFIG.default_knowledge.keys():
                print(colored(f"{integration_name} knowledge is found!", color='light_yellow'))
                des += CONFIG.default_knowledge[integration_name]

            output_description_list.append(f"{k1+1}.integration={integration_name}: {des}")
            for k2,resource in enumerate(list( data.keys())):
                for k3, operation in enumerate(list(data[resource].keys())):
                    new_line = f"  {k1+1}.{operation_counter}: " + data[resource][operation].to_action_string()
                    operation_counter += 1
                    output_description_list.append(new_line)
        
        return "\n".join(output_description_list)



    def resolve(self):
        """
        Resolves the data from the configuration file.

        This function reads the configuration file and resolves the data based on the provided white list and available integrations. It populates the `json_data` list with the integration JSON objects that match the white list. For each integration JSON, it calls the `resolve_integration` function to further resolve the integration data. It also creates a flattened representation of the tools and their metadata in the `flattened_tools` dictionary. If a tool is marked as a pseudoNode, it prints a message indicating that it is being loaded. Finally, it calls the `print_flatten_tools` function and returns the output.

        Parameters:
        None

        Returns:
        None
        """
        self.json_data = []
        self.flattened_tools = {}
        white_list = self.cfg.parser.nodes_whtie_list
        available_integrations = [item.split(".")[0] for item in self.cfg.parser.nodes_whtie_list]
        with open(self.cfg.parser.nodes_json_path, "r", encoding="utf-8") as reader:
            integrations = json.load(reader)
            for integration_json in integrations:
                name = integration_json["name"].split(".")[-1]
                if name not in available_integrations:
                    continue
                self.json_data.append(integration_json)
                integration_data = self.resolve_integration(integration_json=integration_json)
                index = available_integrations.index(name)
                full_tool = white_list[index]
                splits = full_tool.split(".")
                if len(splits) > 1:
                    for key in list(integration_data.keys()):
                        if key != splits[1]:
                            integration_data.pop(key)
                    if len(splits) == 3:
                        for action in list(integration_data[splits[1]].keys()):
                            if action != splits[2]:
                                integration_data[splits[1]].pop(action)

                integration_description = integration_json["description"] if "description" in integration_json.keys() else ""
                self.flattened_tools[name] = {
                    "data": integration_data,
                    "meta": {
                        "description": integration_description,
                        "node_json": integration_json,
                    },
                    "pseudoNode": integration_json['pseudoNode'] if "pseudoNode" in integration_json.keys() else False
                }
                if self.flattened_tools[name]['pseudoNode']:
                    print(colored(f"load pseudoNode {name}", color='cyan'))
        out = self.print_flatten_tools()



    def update_runtime(self):
        """
        Updates the runtime by flashing the code and running it.

        Parameters:
            self (object): An instance of the class.
        
        Returns:
            None
        """
        self.code_runner.flash( 
            main_workflow = self.mainWorkflow,
            workflows=self.workflows,
            nodes = self.nodes
        )
        self.code_runner.run_code()

    def tool_call_handle(self, content:str, tool_name:str, tool_input:dict) -> Action:
        """
        Handles a tool call by executing the specified tool with the given content, tool name, and tool input.

        Args:
            content (str): The content to be processed by the tool.
            tool_name (str): The name of the tool to be executed.
            tool_input (dict): The input parameters for the tool.

        Returns:
            Action: An Action object representing the result of the tool call.
        """
        action = Action(
            content=content,
            tool_name=tool_name,
        )
        for react_key in ["thought","plan","criticism"]:
            if react_key in tool_input.keys():
                action.__setattr__(react_key, tool_input[react_key])
                tool_input.pop(react_key)

        action.tool_input = tool_input
        print_action_base(action)



        tool_status_code = ToolCallStatus.ToolCallSuccess
        tool_output = ""
        if tool_name == "function_define":
            tool_status_code, tool_output = self.handle_function_define(tool_input=tool_input)
        elif tool_name == "function_rewrite_params":
            tool_status_code, tool_output = self.handle_rewrite_params(tool_input=tool_input)
        elif tool_name == "workflow_implment":
            tool_status_code, tool_output = self.handle_workflow_implement(tool_input=tool_input)
        elif tool_name == "ask_user_help":
            tool_status_code, tool_output = self.ask_user_help(tool_input=tool_input)
        elif tool_name == "task_submit":
            tool_status_code, tool_output = self.task_submit(tool_input=tool_input)
        else:
            tool_status_code = ToolCallStatus.NoSuchTool
            tool_output = json.dumps({"error": f"No such action {tool_name}", "result": "Nothing Happened", "status": tool_status_code.name}, ensure_ascii=False)

        action.tool_output = tool_output
        action.tool_output_status = tool_status_code

        print_action_tool(action)

        if CONFIG.environment == ENVIRONMENT.Production:
            if self.recorder.is_final_cache():
                self.update_runtime()
            pass
        else:
            if tool_status_code == ToolCallStatus.ToolCallSuccess:
                self.update_runtime()

        self.recorder.regist_tool_call(
            action=action,
            now_code=self.code_runner.print_code()
        )
    
        return action

    def handle_workflow_implement(self, tool_input) -> (ToolCallStatus, str):
        """
        Handles the implementation of a workflow.

        Parameters:
            tool_input (dict): A dictionary containing the tool input. It should have the following keys:
                - "workflow_name" (str): The name of the workflow to implement.
                - "code" (str): The code for the implementation.

        Returns:
            (ToolCallStatus, str): A tuple containing the tool call status and a JSON string.
                - ToolCallStatus (enum): The tool call status, indicating the success or failure of the operation.
                - str: A JSON string containing the result of the operation.

        Raises:
            None
        """
        workflow_name = tool_input["workflow_name"]
        implement_code = tool_input["code"]

        if workflow_name == "mainWorkflow":
            self.mainWorkflow.implement_code = implement_code
            return ToolCallStatus.ToolCallSuccess, json.dumps({"result": "mainWorkflow has been re-implemented","status": ToolCallStatus.ToolCallSuccess.name})
        else:
            if workflow_name in self.workflows.keys():
                self.workflows[workflow_name].implement_code = implement_code
                return ToolCallStatus.ToolCallSuccess, json.dumps({"result": f"{workflow_name} has been re-implemented","status": ToolCallStatus.ToolCallSuccess.name})
            else:
                self.workflows[workflow_name] = n8nPythonWorkflow(
                    workflow_name=workflow_name,
                    workflow_type=WorkflowType.Sub,
                    implement_code=implement_code
                )
                return ToolCallStatus.ToolCallSuccess, json.dumps({"result": f"{workflow_name} has been added","status": ToolCallStatus.ToolCallSuccess.name})


    def handle_function_test(self, tool_input) -> (ToolCallStatus, str):
        """
        Handles the function test.

        Args:
            self: The object instance.
            tool_input: The input data for the function test.

        Returns:
            A tuple containing the tool call status and a string.

        Raises:
            NotImplementedError: If the 'use_mock_input' flag is set to True.

        Comment:
            - Performs runtime format check for the input data.
            - Expects the input data to be a non-empty list of JSON objects.
            - Each item in the list should be a dictionary with the key 'json'.

        """
        function_name = tool_input["target_function_name"]
        use_mock_input = tool_input["use_mock_input"]
        if use_mock_input:
            raise NotImplementedError
        else:
            input_data = tool_input["input_data"]
        
        if type(input_data) != [] or len(input_data) == 0:
            output_status = ToolCallStatus.InputTypeError
            return output_status, json.dumps({"error": f"Input must be a list of json(len>0), got {input_data}", "result":"Nothing Happened", "status": output_status.name})
        for k, cont in enumerate(input_data):
            if type(cont) != dict or "json" not in cont.keys():
                output_status = ToolCallStatus.InputTypeError
                return output_status, json.dumps({"error": f"Error of item {k}: all the items in the list must be a dict with key \"json\", got {cont}", "result":"Nothing Happened", "status": output_status.name})


    def handle_rewrite_params(self, tool_input) -> (ToolCallStatus, str):
        """
        Handle the rewriting of parameters for a given tool input.
        
        Args:
            tool_input (dict): The input data for the tool.
        
        Returns:
            tuple: A tuple containing the ToolCallStatus enum value and a string.
                   - The ToolCallStatus indicates the status of the tool call.
                   - The string contains the output of the tool call.
        """
        function_name = tool_input["function_name"]
        available_names = [node.get_name() for node in self.nodes]
        if function_name not in available_names:
            output_status = ToolCallStatus.NoSuchFunction
            return output_status, json.dumps({"ERROR": f"Undefined Function {function_name}. Available functions = {available_names}.", "result": "Nothing happened.", "status": output_status.name})
        
        for node in self.nodes:
            if node.get_name() == function_name:
                try:
                    params = json.loads(tool_input["params"], strict = False)
                except:
                    output_status = ToolCallStatus.InputCannotParsed
                    return output_status, json.dumps({"ERROR": f"\"params\" field can't be parsed to json.", "result": "Nothing Happened", "status": output_status.name})

                param_rewrite_status, output_str = node.parse_parameters(params)
                if param_rewrite_status != ToolCallStatus.ToolCallSuccess:
                    return param_rewrite_status, output_str

                node.note_todo = tool_input["TODO"]
                node.node_comments = tool_input["comments"]
                return param_rewrite_status, output_str
        assert False

    

    def handle_function_define(self, tool_input) -> (ToolCallStatus, str):
        """
        Handles the definition of a function.

        Args:
            tool_input (dict): The input data for the function definition.

        Returns:
            Tuple[ToolCallStatus, str]: A tuple containing the tool call status and the tool call result.

        Raises:
            AssertionError: If the "functions" key is not present in `tool_input`.
        """
        assert "functions" in tool_input.keys()
        tool_call_status = []
        tool_call_result = []
        for k, transparent_function in enumerate(tool_input["functions"]):
            integration_name = transparent_function["integration_name"]
            resource_name = transparent_function["resource_name"]
            operation_name = transparent_function["operation_name"]
            comments = transparent_function["comments"].strip()
            TODO = transparent_function["TODO"]



            if integration_name not in self.flattened_tools.keys():
                tool_call_status.append(ToolCallStatus.NoSuchFunction)
                tool_call_result.append(f"function {k} defined FAILED: not such integration {integration_name}")
                continue
            if resource_name not in self.flattened_tools[integration_name]["data"].keys():
                tool_call_status.append(ToolCallStatus.NoSuchFunction)
                tool_call_result.append(f"function {k} defined FAILED: not such resource {integration_name}->{resource_name}")
                continue
            if operation_name not in self.flattened_tools[integration_name]["data"][resource_name].keys():
                tool_call_status.append(ToolCallStatus.NoSuchFunction)
                tool_call_result.append(f"function {k} defined FAILED: not such operation {integration_name}->{resource_name}->{operation_name}")
                continue
            
            node_type = self.flattened_tools[integration_name]["data"][resource_name][operation_name].node_type
            if node_type == NodeType.action:
                node_id = self.action_id
                self.action_id += 1
            else:
                node_id = self.trigger_id
                self.trigger_id += 1
            new_node = n8nPythonNode(
                            node_id= node_id,
                            node_meta=deepcopy(self.flattened_tools[integration_name]["data"][resource_name][operation_name]),
                            node_comments=comments,
                            note_todo=TODO,
                            node_json=self.flattened_tools[integration_name]["meta"]["node_json"],
                        )
            new_node.params = parse_properties(new_node)
            new_node.update_implement_info()
            self.nodes.append(new_node)

            tool_call_status.append(ToolCallStatus.ToolCallSuccess)
            tool_call_result.append(f"function_{k} defined SUCCESS: {integration_name}->{resource_name}->{operation_name}")



        final_status = ToolCallStatus.NoSuchFunction
        if ToolCallStatus.ToolCallSuccess in tool_call_status:
            final_status = ToolCallStatus.ToolCallPartlySuccess
        if ToolCallStatus.NoSuchFunction not in tool_call_status:
            final_status = ToolCallStatus.ToolCallSuccess

        tool_call_result = {
            "result": tool_call_result,
            "status": final_status.name,
        }
        return final_status, json.dumps(tool_call_result)

    def ask_user_help(self, tool_input):
            """
            Asks the user for help and returns the result and status of the tool call.

            Args:
                tool_input (Any): The input to be passed to the tool.

            Returns:
                Tuple[ToolCallStatus, str]: A tuple containing the final status of the tool call and the JSON-encoded tool call result.
            """

            final_status = ToolCallStatus.ToolCallSuccess

            tool_call_result = {
                "result": "" if (CONFIG.environment == ENVIRONMENT.Production and not self.recorder.is_final_cache()) else input(),
                "status": final_status.name,
            }

            return final_status, json.dumps(tool_call_result)
    
    def task_submit(self, tool_input):
        """
        Submits a task with the given tool input.

        Args:
            tool_input (dict): The input data for the tool.

        Returns:
            tuple: A tuple containing the final status of the tool call and the JSON-encoded result of the tool call.
        """

        final_status = ToolCallStatus.ToolCallSuccess

        tool_call_result = {
            "result": "successfully save to markdown",
            "status": final_status.name,
        }

        self.recorder.save_markdown(tool_input['result'])

        return final_status, json.dumps(tool_call_result)