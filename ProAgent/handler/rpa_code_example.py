from transparent_server import transparent_action, tranparent_trigger

# Specific_params: After you give function_define, we will provide json schemas of specific_params here.
# Avaliable_datas: All the avaliable Datas: data_1, data_2...
# Pinned_data_ID: All the input data you pinned and there execution result
# ID=1, output: xxx
# ID=3, output: xxx
# Runtime_input_data: The runtime input of this function(first time)
# Runtime_output_data: The corresponding output
def action_1(input_data: [{...}]):
    # comments: some comments to users. Always give/change this when defining and implmenting
    # TODOS:
    # 1. I will provide the information in runtime
    # 2. I will test the node
    # 3. ...Always give/change this when defining and implmenting
    specific_params = {
        "key_1": value_1,
        "key_2": [
            {
                "subkey_2": value_2,
            }
        ],
        "key_3": {
            "subkey_3": value_3,
        },
        # You will implement this after function-define
    }
    function = transparent_action(integration=xxx, resource=yyy, operation=zzz)
    output_data = function.run(input_data=input_data, params=params)
    return output_data

def action_2(input_data: [{...}]): ...
def action_3(input_data: [{...}]): ...
def action_4(input_data: [{...}]): ...

# Specific_params: After you give function_define, we will provide json schemas of specific_params here.
# Trigger function has no input, and have the same output_format. So We will provide You the exmaple_output once you changed the code here.
def trigger_1(): 
    # comments: some comments to users. Always give/change this when defining and implmenting
    # TODOS:
    # 1. I will provide the information in runtime
    # 2. I will test the node
    # 3. ...Always give/change this when defining and implmenting
    specific_params = {
        "key_1": value_1,
        "key_2": [
            {
                "subkey_2": value_2,
            }
        ],
        "key_3": {
            "subkey_3": value_3,
        },
        # You will implement this after function-define
    }
    function = transparent_trigger(integration=xxx, resource=yyy, operation=zzz)
    output_data = function.run(input_data=input_data, params=params)
    return output_data

def trigger_2(input_data: [{...}]): ...
def trigger_3(input_data: [{...}]): ...

# subworkflow inputs the same json-schema, can be called by another workflow.
def subworkflow_1(father_workflow_input: [{...}]): ...
def subworkflow_2(father_workflow_input: [{...}]): ...

# If you defined the trigger node, we will show you the mocked trigger input here.
# If you have implemented the workflow, we will automatically run the workflow for all the mock trigger-input and tells you the result.
def mainWorkflow(trigger_input: [{...}]): 
    # comments: some comments to users. Always give/change this when defining and implmenting
    # TODOS:
    # 1. I will provide the information in runtime
    # 2. I will test the node
    # 3. ...Always give/change this when defining and implmenting

    # some complex logics here
    output_data = trigger_input
    
    return output_data