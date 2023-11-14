from typing import List, Dict
from dataclasses import dataclass, field
from enum import Enum, unique
from copy import deepcopy
import json

from ProAgent.utils import NodeType, ToolCallStatus, RunTimeStatus, TestResult
from ProAgent.n8n_parser.parameters import *

@dataclass
class n8nNodeMeta():
    node_type: NodeType = NodeType.action
    integration_name: str = ""
    resource_name: str = ""
    operation_name: str = ""
    operation_description: str = ""

    def to_action_string(self):
        """
        Generates a string representation of the action performed by the node.
        
        Returns:
            str: The string representation of the action.
        """
        output = f"{self.node_type.name}(resource={self.resource_name}, operation={self.operation_name})"
        if self.operation_description != "":
            output += f": {self.operation_description}"
        return output
    
@dataclass
class n8nPythonNode():
    """将n8n node转化为一个python-function
    """
    node_id: int = 1
    node_meta: n8nNodeMeta = field(default_factory=n8nNodeMeta())
    node_comments: str = ""
    note_todo: List[str] = field(default_factory=lambda: [])
    node_json: dict = field(default_factory=lambda: {})
    params: Dict[str, n8nParameter] = field(default_factory=lambda: {})

    implemented: bool = False
    
    last_runtime_info: TestResult = field(default_factory= lambda: TestResult())

    def get_name(self):
        """
        Returns a string representing the name of the node.
        
        Parameters:
            self (Node): The Node object.
        
        Returns:
            str: The name of the node, which is a combination of the node type and the node ID.
        """
        return f"{self.node_meta.node_type.name}_{self.node_id}"

    def get_runtime_description(self) -> str:
        """
        Get the information about the last runtime of the Workflow.

        Returns:
            str: The description of the last runtime.

        """
        if self.last_runtime_info == RunTimeStatus.DidNotImplemented:
            return f"This {self.node_meta.node_type} has not been implemented"

    def update_implement_info(self):
        if len(self.params) == 0:
            self.implemented = True
            return
        for key, value in self.params.items():
            if value.data_is_set:
                self.implemented = True
                return


    def print_self_clean(self):
        """Returns a multiline text."""
        lines = []
        input_data = "input_data: List[Dict] =  [{...}]" if self.node_meta.node_type == NodeType.action else ""
        define_line = f"def {self.get_name()}({input_data}):"
        lines.append(define_line)
        param_json = {}
        for key, value in self.params.items():
            param = value.to_json()
            if param != None:
                param_json[key] = param


        param_str = json.dumps(param_json, indent = 2, ensure_ascii=False)
        param_str = param_str.splitlines(True)
        param_str = [line.strip("\n") for line in param_str]
        prefix = "  params = "
        param_str[0] = prefix + param_str[0]
        if not self.implemented:
            if len(self.params) > 0:
                param_str[0] += "  # to be Implemented"
            else:
                param_str[0] += "  # This function doesn't need spesific param"
        for i in range(1, len(param_str)):
            param_str[i] = " "*len(prefix) + param_str[i]
        lines.extend(param_str)

        lines.append(f"  function = transparent_{self.node_meta.node_type.name}(integration=\"{self.node_meta.integration_name}\", resource=\"{self.node_meta.resource_name}\", operation=\"{self.node_meta.operation_name}\")")
    
        if self.node_meta.node_type == NodeType.action:
            lines.append( "  output_data = function.run(input_data=input_data, params=params)")
        else:
            lines.append( "  output_data = function.run(input_data=None, params=params)")

        lines.append("  return output_data")

        return lines 
    

    def print_self(self):
        """Returns a multiline text."""
        lines = []
        input_data = "input_data: List[Dict] =  [{...}]" if self.node_meta.node_type == NodeType.action else ""
        define_line = f"def {self.get_name()}({input_data}):"
        lines.append(define_line)
        if self.node_comments != "" or self.note_todo != []:
            lines.append(f"  \"\"\"")
        if self.node_comments != "":
            lines.append(f"  comments: {self.node_comments}")
        
        if self.note_todo != []:
            lines.append(f"  TODOs: ")
            for todo in self.note_todo:
                lines.append(f"    - {todo}")
        lines.append(f"  \"\"\"")
        
        param_json = {}
        for key, value in self.params.items():
            param = value.to_json()
            if param != None:
                param_json[key] = param


        param_str = json.dumps(param_json, indent = 2, ensure_ascii=False)
        param_str = param_str.splitlines(True)
        param_str = [line.strip("\n") for line in param_str]
        prefix = "  params = "
        param_str[0] = prefix + param_str[0]
        if not self.implemented:
            if len(self.params) > 0:
                param_str[0] += "  # to be Implemented"
            else:
                param_str[0] += "  # This function doesn't need spesific param"
        for i in range(1, len(param_str)):
            param_str[i] = " "*len(prefix) + param_str[i]
        lines.extend(param_str)

        lines.append(f"  function = transparent_{self.node_meta.node_type.name}(integration=\"{self.node_meta.integration_name}\", resource=\"{self.node_meta.resource_name}\", operation=\"{self.node_meta.operation_name}\")")
    
        if self.node_meta.node_type == NodeType.action:
            lines.append( "  output_data = function.run(input_data=input_data, params=params)")
        else:
            lines.append( "  output_data = function.run(input_data=None, params=params)")

        lines.append("  return output_data")

        return lines 
    
    def parse_parameters(self, param_json: dict) -> (ToolCallStatus, str):
        """
        Parses the input parameters and checks if they conform to the expected format.
        Args:
            param_json (dict): The input parameters in JSON format.
        Returns:
            tuple: A tuple containing the status of the tool call and a JSON string
                representing the result.
        Raises:
            TypeError: If the input parameter is not of type dict.
        """
        new_params = deepcopy(self.params)
        for key in new_params:
            new_params[key].refresh()

        tool_call_result = []

        if not isinstance(param_json, dict):
            tool_status = ToolCallStatus.ParamTypeError
            return tool_status, json.dumps({"error": f"Parameter Type Error: The parameter is expected to be a json format string which can be parsed as dict type. However, you are giving string parsed as {type(param_json)}", "result": "Nothing happened.", "status": tool_status.name})

        for key in param_json.keys():
            if key not in new_params.keys():
                tool_status = ToolCallStatus.UndefinedParam
                return tool_status, json.dumps({"error": f"Undefined input parameter \"{key}\" for {self.get_name()}.Supported parameters: {list(new_params.keys())}", "result": "Nothing happened.", "status": tool_status.name})
            if type(param_json[key]) == str and (len(param_json[key]) == 0):
                tool_status = ToolCallStatus.RequiredParamUnprovided
                return tool_status, json.dumps({"error": f"input parameter is null, \"{key}\" for {self.get_name()}. You should put something in it.", "result": "Nothing happened.", "status": tool_status.name})
            parse_status, parse_output = new_params[key].parse_value(param_json[key])
            if parse_status != ToolCallStatus.ToolCallSuccess:
                tool_status = parse_status
                return tool_status, json.dumps({"error": f"{parse_output}", "result": "Nothing Happened", "status": tool_status.name})
            tool_call_result.append(parse_output)

        self.params = new_params
        tool_status = ToolCallStatus.ToolCallSuccess

        self.update_implement_info()
        return tool_status, json.dumps({"result": tool_call_result, "status": tool_status.name})

