
import json


def format_replace_exp_workflow(data_item: dict, expression: str):
    """
    Generates a workflow for replacing an expression with a formatted value.

    Args:
        data_item (dict): The data item to be formatted.
        expression (str): The expression to be replaced with the formatted value.

    Returns:
        dict: The generated workflow for replacing the expression.

    Example:
        format_replace_exp_workflow(
            {
                "name": "John",
                "age": 30
            },
            "Hello, {name}! You are {age} years old."
        )

    This function takes a data item and an expression as input and generates a workflow
    that replaces the expression with a formatted value. The data_item parameter is a
    dictionary containing the data to be formatted. The expression parameter is a string
    representing the expression to be replaced.

    The function returns a dictionary representing the generated workflow for replacing
    the expression. This workflow is used to execute the workflow trigger, perform code
    execution, and assign the formatted value to a variable.

    The example demonstrates how to use this function to generate a workflow that
    replaces the expression "{name}" with the value "John" and the expression "{age}"
    with the value "30" in the string "Hello, {name}! You are {age} years old.".
    """
    replace_exp_workflow = {
        "meta": {
        "instanceId": "c14b6327b27c1dfe99ed7d452fafcd4d8e371aa8906a65b2508cc554e201c539"
        },
        "nodes": [
            {
                "id": "64074a51-e223-4f81-9343-12f8e6d0e536",
                "name": "Execute Workflow Trigger",
                "type": "n8n-nodes-base.executeWorkflowTrigger",
                "typeVersion": 1,
                "position": [
                    0,
                    0
                ],
                "parameters": {}
            },
            {
                "parameters": {
                "jsCode": f"return [{json.dumps(data_item)}]"
                },
                "id": "5b7fc8cc-50d0-48d4-bdf1-7e55d0b29521",
                "name": "Code",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [
                -60,
                820
                ]
            },
            {
                "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": "$input.item.json = {\n  formatted:`" + expression + "`\n}\n\nreturn $input.item;"
                },
                "id": "2326a464-286f-46d4-8059-1b510bbd1654",
                "name": "node_var",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [
                120,
                800
                ]
            }
        ],
        "connections": {
            "Execute Workflow Trigger": {
                "main": [
                    [
                        {
                            "node": "Code",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Code": {
                "main": [
                    [
                        {
                            "node": "node_var",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": False,
        "settings": {
            "executionOrder": "v1"
        },
        "tags": [],
        "id": "ovm4ntEU37IYs7PI"
    }
    return replace_exp_workflow
def format_return_data(return_list:list) -> str:
    """
    Generate the formatted return data for the given return list.

    Parameters:
        return_list (list): A list containing the data to be formatted.

    Returns:
        str: The formatted return data.

    """

    return_data_template = \
    '''
Execution was successful:
====================================
    {
    "data": {
        "startData": {},
        "resultData": {
        "runData": {
            "Execute Workflow Trigger": [
            {
                "startTime": 1697883465922,
                "executionTime": 0,
                "source": [],
                "executionStatus": "success",
                "data": {
                "main": [
                    [
                    {
                        "json": {},
                        "pairedItem": {
                        "item": 0
                        }
                    }
                    ]
                ]
                }
            }
            ],
            "Code": [
            {
                "startTime": 1697883465923,
                "executionTime": 11,
                "source": [
                {
                    "previousNode": "Execute Workflow Trigger"
                }
                ],
                "executionStatus": "success",
                "data": {
                "main": [
                    [
                    {
                        "json": {},
                        "pairedItem": {
                        "item": 0
                        }
                    }
                    ]
                ]
                }
            }
            ],
            "node_var": [
            {
                "startTime": 1697883465934,
                "executionTime": 48,
                "source": [
                {
                    "previousNode": "Code"
                }
                ],
                "executionStatus": "success",
                "data": {
                "main": [
                    {return_list}
                ]
                }
            }
            ]
        },
        "lastNodeExecuted": "node_var"
        },
        "executionData": {
        "contextData": {},
        "nodeExecutionStack": [],
        "waitingExecution": {},
        "waitingExecutionSource": {}
        }
    },
    "mode": "cli",
    "startedAt": "2023-10-21T10:17:45.909Z",
    "stoppedAt": "2023-10-21T10:17:45.982Z",
    "status": "running",
    "finished": true
    }
    '''

    return_data = return_data_template.replace("{return_list}", json.dumps(return_list))
    return return_data