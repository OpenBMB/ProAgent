import json


mock_function_call_list = [
    ("function_define",{
    "functions": [
      {
        "integration_name": "webhook",
        "resource_name": "default",
        "operation_name": "default",
        "comments": "This is the entry point of the workflow, the workflow will be executed when the user clicks the button",
        "TODO": [
          "According to the UI description, this trigger may not need any parameters to fill in"
        ]
      },
      {
        "integration_name": "n8nTrainingCustomerDatastore",
        "resource_name": "default",
        "operation_name": "getOnePerson",
        "comments": "Use this action to simulate the operation of obtaining model version information",
        "TODO": [
          "After implementing this action, you need to check the data format of the model version information to prepare for the implementation of the workflow"
        ]
      },
      {
        "integration_name": "slack",
        "resource_name": "message",
        "operation_name": "post",
        "comments": "Use this action to send model version information and self-introduction to the #general channel of slack",
        "TODO": [
          "After implementing this action, you need to check the data format required for sending information to prepare for the implementation of the workflow"
        ]
      }
    ]
  }),
    ("function_rewrite_params",{
        "function_name": "action_1",
        "params": json.dumps(
            {
             "select": "channel",
             "channelId": {
               "mode": "name",
               "value": "#general"
             },
             "messageType": "text",
             "text": "Hello everyone, I'm ChatGPT"
           }
        ),
        "comments": "This is the trigger point of the workflow, the workflow will be executed when the user clicks a button",
        "TODO": [
        "Execute this trigger and then check the output to see if it meets our expectations"
        ]
  }),
    ("function_rewrite_params",{
        "function_name": "trigger_0",
        "params": json.dumps(
            {
              "httpMethod": "GET",
             "path": "/trigger",
             "responseMode": "onReceived",
             "responseData": "allEntries"
           }
        ),
        "comments": "This is the trigger point of the workflow, the workflow will be executed when the user sends a get request",
        "TODO": [
        "Execute this trigger and then check the output to see if it meets our expectations"
        ]
  }),
    ("workflow_implment",{
        "workflow_name": "mainWorkflow",
        "code": """
def mainWorkflow(trigger_input: [{...}]):
  \"\"\"
  comments: You need to give comments when implementing mainWorkflow
  TODOs: 
    - first define some actions
    - define a trigger
    - then implement this
  \"\"\"
  print("Please call Workflow-implement first")
  print(trigger_input)
  subworkflow_auto(trigger_input)
  print(trigger_input)
  subworkflow_auto(trigger_input)
  print(trigger_input)
  trigger_input.append({})
  subworkflow_auto(trigger_input)
  assert False, "nmsl"
""",
  }),
    ("workflow_implment",{
        "workflow_name": "subworkflow_auto",
        "code": """
def subworkflow_auto(father_input):
  output = subworkflow_hihihi(father_input)
  father_input.append({})
  return output
""",
  }),
    ("workflow_implment",{
        "workflow_name": "subworkflow_hihihi",
        "code": """
def subworkflow_hihihi(father_input):
  print("hihihi")
  if len(father_input) > 1:

    return action_1(father_input)
  return father_input
""",
  })
]