
import json


mock_function_call_list = [
    ("function_define",{
    "functions": [
      {
        "integration_name": "webhook",
        "resource_name": "default",
        "operation_name": "default",
        "comments": "这是workflow的入口，用户点击按钮时候会执行workflow",
        "TODO": [
          "根据ui的描述，这个触发器可能没有参数需要填写"
        ]
      },
      {
        "integration_name": "n8nTrainingCustomerDatastore",
        "resource_name": "default",
        "operation_name": "getOnePerson",
        "comments": "用这个action模拟获取模型版本信息的操作",
        "TODO": [
          "实现这个action后，需要查看模型版本信息的数据格式，为实现workflow作准备"
        ]
      },
      {
        "integration_name": "slack",
        "resource_name": "message",
        "operation_name": "post",
        "comments": "用这个action向slack的#general频道发送模型版本信息和自我介绍",
        "TODO": [
          "实现这个action后，需要查看发送信息需要的数据格式，为实现workflow作准备"
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
             "text": "大家好，我是ChatGPT"
           }
        ),
        "comments": "这是workflow的触发点，当用户点击一个按钮时会执行workflow",
        "TODO": [
        "执行这个触发器，然后检查输出，看看是否符合我们的预期"
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
        "comments": "这是workflow的触发点，当用户发送 get 请求时会执行workflow",
        "TODO": [
        "执行这个触发器，然后检查输出，看看是否符合我们的预期"
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