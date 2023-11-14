
import json
import re
import subprocess
import tempfile

from termcolor import colored
from ProAgent.n8n_tester.pseudo_node.templates import format_replace_exp_workflow, format_return_data
from ProAgent.n8n_tester.prompts import success_prompt, error_prompt

def format_expression(expression):
    """
    Replaces occurrences of a specific pattern in the given expression.

    Args:
        expression (str): The expression to be formatted.

    Returns:
        str: The formatted expression with the pattern replaced.

    """
    pattern = r'\{\{\s?\$(.*?)\s?\}\}'
    def replace_match(match):
        match_content = match.group(1)
        return f'${{$input.item.{match_content}}}'

    formatted_expression = re.sub(pattern, replace_match, expression)
    return formatted_expression

def replace_single_exp(data_item:dict, expression:str) -> str:
    """
    Replaces a single expression in the given data item.

    Parameters:
    - `data_item` (dict): The data item in which the expression should be replaced.
    - `expression` (str): The expression to be replaced.

    Returns:
    - `str`: The modified expression.

    Raises:
    - `BaseException`: If an error occurs during the execution of the expression substitution workflow.

    Description:
    - If the `expression` starts with '=', it is formatted and then used to create a replace expression workflow.
    - The workflow is written to a temporary JSON file and executed using the `n8n` command-line tool.
    - The output of the execution is parsed to extract the modified expression.
    - If the execution is successful and the modified expression is not empty, it is returned.
    - If the execution is not successful or the modified expression is empty, a `BaseException` is raised.
    - If the `expression` does not start with '=', it is returned as is.
    """
    if expression.startswith('='):

        expression = format_expression(expression[1:])
        
        # substitute workflow (data_item, expression)
        replace_exp_workflow = format_replace_exp_workflow(data_item, expression)

        temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json")
        json.dump(replace_exp_workflow, temp_file)
        temp_file.close()
        temp_file_path = temp_file.name
        result = subprocess.run(["n8n", "execute", "--file", temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        output = result.stdout.decode('utf-8')

        print(colored(output, color='green'))

        if success_prompt in output:
            output_data = output.split(success_prompt)[-1]
            if output_data != "":
                output_data = json.loads(output_data)
                output_data = output_data["data"]["resultData"]["runData"]["node_var"][0]["data"]["main"][0]
                return output_data[0]['json']['formatted']
            else:
                raise BaseException()
        else:
            raise BaseException()
        
    return expression

def replace_exp_recursive(data_item: dict, expression_dict: dict) -> dict:
    """
    Recursively replaces expressions in a data_item dictionary with corresponding values.

    Args:
        data_item (dict): The dictionary containing the data items.
        expression_dict (dict): The dictionary containing the expressions to replace.

    Returns:
        dict: A new dictionary with replaced expressions.

    """

    return_dict = {}
    for key in expression_dict.keys():
            expression_value = expression_dict[key]                
            if type(expression_value) == dict:
                return_dict[key] = replace_exp_recursive(data_item, expression_value)
            elif type(expression_value) == str:
                output = replace_single_exp(data_item, expression_value)
                return_dict[key] = output
    return return_dict

def replace_exp(input_data:list, expression_dict:dict) -> list:
    """
    Replace the json expressions in the input data.
    
    Parameters:
    - input_data (list): The list of input data.
    - expression_dict (dict): The dictionary of json expressions.

    Returns:
    - list: The list of results after replacing json expressions.
    """
    return_list = []
    for data_item in input_data:
        return_single_dict = replace_exp_recursive(data_item, expression_dict)
        return_list.append(return_single_dict)
    return return_list

def fill_return_data(output_data:list) -> str:
    """
    Generate the function comment for the given function body in a markdown code block with the correct language syntax.

    Args:
        output_data (list): The list of output data.

    Returns:
        str: The formatted return data.
    """
    return format_return_data(output_data)