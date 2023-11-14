
import json
from ProAgent.config import CONFIG

from ProAgent.agent.utils import _chat_completion_request


def run_ai_completion(params_list:list) -> str:
    """
    Generates a function comment for the given function body.
    
    Args:
        params_list (list): A list of parameters.
        
    Returns:
        str: The function comment in markdown format.
    """
    return_list = []
    completion_kwargs = CONFIG.default_completion_kwargs
    for params in params_list:
        messages = params['messages']
        if isinstance(messages, str):
            messages_json = json.loads(messages)
        elif isinstance(messages, list):
            messages_json = messages
        result = _chat_completion_request(messages=messages_json,
                                            functions=None,
                                            default_completion_kwargs=completion_kwargs,
                                            recorder=None)
        content = result["choices"][0]["message"]['content']
        return_list.append(
            {
                "json": {
                    'choices':[
                        {
                            'text': content
                        }
                    ]
                },
                "pairedItem": {
                    "item": 0
                }
            })
    return return_list
