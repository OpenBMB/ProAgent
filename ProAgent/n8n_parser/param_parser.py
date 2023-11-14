from enum import Enum, unique

from ProAgent.n8n_parser.node import n8nPythonNode
from ProAgent.n8n_parser.parameters import *


def parse_display_options(display_options, node: n8nPythonNode) -> bool:
    """
    Check if the given display options should be parsed for the given n8nPythonNode.

    Args:
        display_options (dict): The display options to be parsed.
        node (n8nPythonNode): The n8nPythonNode to be checked against.

    Returns:
        bool: True if the display options should be parsed, False otherwise.
    """
    if "show" in display_options.keys():
        if "resource" in display_options["show"]:
            if node.node_meta.resource_name not in display_options["show"]["resource"]:
                return False
        if "operation" in display_options["show"]:
            if node.node_meta.operation_name not in display_options["show"]["operation"]:
                return False
    else:
        return False
    return True

def parse_properties(node: n8nPythonNode):
    """
    This function parses the properties of a given node and returns a dictionary with parameter descriptions for the model.
    Args:
        node (n8nPythonNode): The node object containing the properties to parse.
    Returns:
        dict: A dictionary containing the parameter descriptions.
    """
    node_json = node.node_json
    parameter_descriptions = {}

    for content in node_json["properties"]:
        assert type(content) == dict
        parameter_name = content["name"]

        if parameter_name in ["resource", "operation", "authentication"]:
            continue
        
        if "displayOptions" in content.keys() and (parse_display_options(content["displayOptions"], node) == False):
            continue

        parameter_type = content["type"]

        new_param = visit_parameter(content)
        if new_param != None:
            parameter_descriptions[parameter_name] = new_param
    return parameter_descriptions


    