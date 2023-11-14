
mainWorkflow_code = """
def mainWorkflow(trigger_input: [{...}]):
  \"\"\"
  comments: You need to give comments when implementing mainWorkflow
  TODOs: 
    - first define some actions
    - define a trigger
    - then implement this
  \"\"\"
  print("Please call Workflow-implement first")
  raise NotImplementedError
"""

def get_intrinsic_functions():
    """
    Return a list of intrinsic functions.

    This function returns a list of intrinsic functions that can be used in the workflow. The list includes functions for defining new functions, rewriting function parameters, implementing workflows, and asking for user help. Each function has a name, description, and parameters.

    Returns:
        list: A list of intrinsic functions.

    """

    node_define_function = {
        "name": "function_define",
        "description": "define a list of functions, each one must specify the given (integration-resource-action)",
        "parameters": {
            "type": "object",
            "properties":{
                "thought": {
                    "type": "string",
                    "description": "Why you choose this function",
                },
                "plan": {
                    "type": "array",
                    "description": "What will you do in the following steps",
                    "items": {
                        "type":"string",
                    }
                },
                "criticism": {
                    "type": "string",
                    "description": "What main weakness does the current plan have",
                },
                "functions": {
                    "type": "array",
                    "description": "the newly defined functions.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "integration_name": {
                                "type": "string",
                            },
                            "resource_name": {
                                "type": "string",
                            },
                            "operation_name": {
                                "type": "string",
                            },
                            "comments": {
                                "type": "string",
                                "description": "This will be shown to the user, how will you use this node in the workflow"
                            },
                            "TODO": {
                                "type": "array",
                                "description": "The function didn't have implemented yet. List what you will do to further implement, test and refine this function",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": ["integration_name", "resource_name", "operation_name", "comments", "TODO"],
                    }
                }
            },
            "required": ["thought", "plan", "criticism","functions"],
        },
    }

    node_rewrite_param_function = {
        "name": "function_rewrite_params",
        "description": "Give params of a already defined function with the provided param descriptions, This will overwrite now params",
        "parameters":{
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "Why you choose this function",
                },
                "plan": {
                    "type": "array",
                    "description": "What will you do in the following steps",
                    "items": {
                        "type":"string",
                    }
                },
                "criticism": {
                    "type": "string",
                    "description": "What main weakness does the current plan have",
                },
                "function_name": {
                    "type": "string",
                    "description": "Such as 'Action_x' or 'Trigger_x'. Must be a already defined function.",
                },
                "params": {
                    "type": "string",
                    "description": "The json object of the input params. The field descriptions should refer to the Function defination in the code",
                },
                "comments": {
                    "type": "string",
                    "description": "This will be shown to the user, how will you use this node in the workflow"
                },
                "TODO": {
                    "type": "array",
                    "description": "What will you do to further implement, test and refine this function",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["thought", "plan", "criticism", "function_name", "params", "comments", "TODO"],
        }
    }

    workflow_implement_function = {
        "name": "workflow_implment",
        "description": "Implement a workflow, directly write the output of the workflow, staring with \"def mainWorkflow...\" or \"def subworkflow_xxx...\"",
        "parameters": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "Why you choose this function",
                },
                "plan": {
                    "type": "array",
                    "description": "What will you do in the following steps",
                    "items": {
                        "type":"string",
                    }
                },
                "criticism": {
                    "type": "string",
                    "description": "What main weakness does the current plan have",
                },
                "workflow_name": {
                    "type": "string",
                    "description": "the newly implemented workflow. If this workflow exists, we will overwrite it. All names must be \"mainWorkflow\" or \"subworkflow_x\"",
                },
                "code": {
                    "type": "string",
                    "description": "Write the python code of the workflow. We will check you have \"comments\" and \"TODOs\". Input of mainWorkflow should always be trigger_input, Input of subworkflows should always be father_workflow_input",
                }
            },
            "required": ["thought", "plan", "criticism", "workflow_name", "code"],
        }
    }


    ask_user_help_function = {
        "name": "ask_user_help",
        "description": "Call this function when you think you can't solve some problems. You can ask user for help.",
        "parameters": {
            "type": "object",
            "properties": {
                "problems": {
                    "type": "string",
                    "description": "Tell what problem you are confronted with to user and ask for help."
                }
            },
        },
    }

    task_submit_function = {
        "name": "task_submit",
        "description": "Call this function when you think you have finished the task. User will give you some feedback that can help you make your workflow better.",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "Tell what you have done to user. Use Markdown format."
                }
            },
        },
    }

    change_pin_data_function = {

    }

    return [node_define_function, node_rewrite_param_function, workflow_implement_function, ask_user_help_function, task_submit_function]