"""Function param descriptions: 
This function doesn't need params

This function has been executed for 0 times. Last execution:
1.Status: DidNotBeenCalled
2.Input: 
[]

3.Output:
[]
"""
def trigger_0():
  """
  comments: 当用户手动触发时，启动工作流程
  TODOs: 
    - 实现触发器的参数设置
  """
  params = {}
  function = transparent_trigger(integration="manualTrigger", resource="default", operation="default")
  output_data = function.run(input_data=None, params=params)
  return output_data



"""Function param descriptions: 
0 params["documentId"]: dict{"mode":enum(str),"values":any} = {'mode': 'list', 'value': ''}, Required: Document . "mode" should be one of ['url', 'id']: 
  0.0 params["documentId"]["value"](when "mode"="url"): string: By URL
  0.1 params["documentId"]["value"](when "mode"="id"): string: By ID
1 params["sheetName"]: dict{"mode":enum(str),"values":any} = {'mode': 'list', 'value': ''}, Required: Sheet . "mode" should be one of ['url', 'id']: 
  1.0 params["sheetName"]["value"](when "mode"="url"): string: By URL
  1.1 params["sheetName"]["value"](when "mode"="id"): string: By ID
2 params["filtersUI"]: dict[str,list[dict[str,any]]] = {}: Filters(Add Filter) . properties description:
  ...hidden...
3 params["options"]: dict = {}: Options(Add Option) . properties description:
  ...hidden...

This function has been executed for 0 times. Last execution:
1.Status: DidNotBeenCalled
2.Input: 
[]

3.Output:
[]
"""
def action_0(input_data: List[Dict] =  [{...}]):
  """
  comments: 从Google Sheets中读取业务流数据，其中documentId和sheetName都是通过URL给出的。
  TODOs: 
    - 测试此功能
  """
  params = {
             "documentId": {
               "mode": "url",
               "value": "https://docs.google.com/spreadsheets/d/1_B038J1f3VW94z179OagFwEtnr3k5mTyXKBTPI2Fw-U/edit#gid=1759497495"
             },
             "sheetName": {
               "mode": "url",
               "value": "https://docs.google.com/spreadsheets/d/1_B038J1f3VW94z179OagFwEtnr3k5mTyXKBTPI2Fw-U/edit#gid=1759497495"
             }
           }
  function = transparent_action(integration="googleSheets", resource="sheet", operation="read")
  output_data = function.run(input_data=input_data, params=params)
  return output_data



"""Function param descriptions: 
0 params["select"]: enum[string] = "", Required: Send Message To(Select...) . Available values:
  0.0 value=="channel": Channel
  0.1 value=="user": User
1 params["channelId"]: dict{"mode":enum(str),"values":any} = {'mode': 'list', 'value': ''}, Required: Channel. The Slack channel to send to(Select a channel...) . "mode" should be one of ['id', 'name', 'url']: 
  1.0 params["channelId"]["value"](when "mode"="id"): string: By ID(C0122KQ70S7E)
  1.1 params["channelId"]["value"](when "mode"="name"): string: By Name(#general)
  1.2 params["channelId"]["value"](when "mode"="url"): string: By URL(https://app.slack.com/client/TS9594PZK/B0556F47Z3A)
2 params["user"]: dict{"mode":enum(str),"values":any} = {'mode': 'list', 'value': ''}: User(Select a user...) . "mode" should be one of ['id', 'username']: 
  ...hidden...
3 params["messageType"]: enum[string] = "text": Message Type. Whether to send a simple text message, or use Slack’s Blocks UI builder for more sophisticated messages that include form fields, sections and more . Available values:
  3.0 value=="text": Simple Text Message. Supports basic Markdown
  3.1 value=="block": Blocks. Combine text, buttons, form elements, dividers and more in Slack 's visual builder
  3.2 value=="attachment": Attachments
4 params["text"]: string = "": Notification Text. Fallback text to display in slack notifications. Supports <a href="https://api.slack.com/reference/surfaces/formatting">markdown</a> by default - this can be disabled in "Options".
5 params["blocksUi"]: string = "", Required: Blocks. Enter the JSON output from Slack's visual Block Kit Builder here. You can then use expressions to add variable content to your blocks. To create blocks, use <a target='_blank' href='https://app.slack.com/block-kit-builder'>Slack's Block Kit Builder</a>
6 params["attachments"]: list[dict] = [{}]: Attachments(Add attachment item) . properties description:
  ...hidden...
7 params["otherOptions"]: dict = {}: Options. Other options to set(Add options) . properties description:
  ...hidden...

This function has been executed for 0 times. Last execution:
1.Status: DidNotBeenCalled
2.Input: 
[]

3.Output:
[]
"""
def action_1(input_data: List[Dict] =  [{...}]):
  """
  comments: 向Slack的#general频道发送消息
  TODOs: 
    - 测试此功能
  """
  params = {
             "select": "channel",
             "channelId": {
               "mode": "name",
               "value": "#general"
             }
           }
  function = transparent_action(integration="slack", resource="message", operation="post")
  output_data = function.run(input_data=input_data, params=params)
  return output_data



"""Function param descriptions: 
0 params["sendTo"]: string = "", Required: To. The email addresses of the recipients. Multiple addresses can be separated by a comma. e.g. jay@getsby.com, jon@smith.com.(info@example.com)
1 params["subject"]: string = "", Required: Subject(Hello World!)
2 params["emailType"]: enum[string] = "text", Required: Email Type  You can't use expression.. Available values:
  2.0 value=="text": Text
  2.1 value=="html": HTML
3 params["message"]: string = "", Required: Message
4 params["options"]: dict = {}: Options(Add Option) . properties description:
  ...hidden...

This function has been executed for 0 times. Last execution:
1.Status: DidNotBeenCalled
2.Input: 
[]

3.Output:
[]
"""
def action_2(input_data: List[Dict] =  [{...}]):
  """
  comments: 向Gmail发送邮件，邮件的收件人、主题和内容都是通过输入数据给出的。
  TODOs: 
    - 测试此功能
  """
  params = {
             "sendTo": "={{$json['sendTo']}}",
             "subject": "={{$json['subject']}}",
             "message": "={{$json['message']}}"
           }
  function = transparent_action(integration="gmail", resource="message", operation="send")
  output_data = function.run(input_data=input_data, params=params)
  return output_data



"""Function param descriptions: 
0 params["messages"]: string = "", Required: messages. Set system and user prompts here. An Example:{"messages": [{"role": "system","content": "Please say hello to user."}, {"role": "user","content": "Hello!"}]}

This function has been executed for 0 times. Last execution:
1.Status: DidNotBeenCalled
2.Input: 
[]

3.Output:
[]
"""
def action_3(input_data: List[Dict] =  [{...}]):
  """
  comments: 使用AI生成邮件内容
  TODOs: 
    - 实现动作的参数设置
  """
  params = {}  # to be Implemented
  function = transparent_action(integration="aiCompletion", resource="default", operation="default")
  output_data = function.run(input_data=input_data, params=params)
  return output_data



"""

This function has been executed for 1 times. Last execution:
1.Status: ErrorRaisedHere
2.Input: 
None

3.Output:
[]
"""
def mainWorkflow(trigger_input: [{...}]):
  """
  comments: 当用户手动触发时，从Google Sheets中读取业务流数据，计算业务流的利润，并判断业务流的类型，给业务经理发送盈利或亏损信息。
  TODOs: 
    - 测试此工作流程
  """
  # 从Google Sheets中读取业务流数据
  business_flow_data = action_0(trigger_input)
  # 计算业务流的利润
  for data in business_flow_data:
    data['json']['profit'] = data['json']['sales'] - data['json']['cost']
  # 判断业务流的类型，并给业务经理发送盈利或亏损信息
  for data in business_flow_data:
    business_type = action_3([{'json': {'messages': [{'role': 'user', 'content': 'Please determine whether the following business flow belongs to to B(to Business) or to C(to Client)? ' + data['json']['Description']}]}}])[0]['json']['choices'][0]['text']
    if 'to B' in business_type:
      # 如果业务流类型为to B，向Slack的#general频道发送消息
      message = {'json': {'text': '业务流' + data['json']['name'] + '的利润为' + str(data['json']['profit'])}}
      action_1([message])
    elif 'to C' in business_type:
      # 如果业务流类型为to C，向该业务流经理发送一则提醒邮件
      message = {'json': {'messages': [{'role': 'user', 'content': '业务流' + data['json']['name'] + '的利润为' + str(data['json']['profit']) + '请给客户经理写一封邮件。'}]}}
      email_content = action_3([message])
      email = {'json': {'sendTo': data['json']['manager'], 'subject': '业务流利润提醒', 'message': email_content[0]['json']['choices'][0]['text']}}
      action_2([email])
  return business_flow_data



"""

The directly running result for now codes with print results are as following:


Note: if there is 'KeyError' in the error message, it may be due to the wrong usage of output data. The output data info may help you: 
[Output Data Info]

------------------------
In Function: mainWorkflow
      print("Please call Workflow-implement first")
-->   raise NotImplementedError
------------------------
NotImplementedError: 

You can also see the runnning result for all functions in there comments.
"""