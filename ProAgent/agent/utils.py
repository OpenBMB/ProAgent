'''
openai.error.InvalidRequestError: The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766 (request id: 20231114074315131365776UGar1q65)
  Unable to generate ChatCompletion response
  Exception: The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766 (request id: 20231114074315131365776UGar1q65)
'''
import os
import traceback
from typing import Dict, List, Union
import json
import uuid
from colorama import Fore
import openai
from copy import deepcopy
import requests
import tiktoken
import time
from func_timeout import func_set_timeout
import func_timeout
import random
from ProAgent.config import CONFIG

from ProAgent.loggers.logs import logger
from ProAgent.running_recorder import RunningRecoder
from ProAgent.utils import LLMStatusCode


def _chat_completion_request_atomic(**json_data):
    """
    Creates a chat completion request with the given JSON data.
    
    Args:
        **json_data: The JSON data for the chat completion request.
        
    Returns:
        The response from the OpenAI ChatCompletion API.
    """
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    openai.api_base = os.environ.get('OPENAI_API_BASE')
    response = openai.ChatCompletion.create(
                **json_data,
            )
    return response

@func_set_timeout(60)
def _chat_completion_request_without_retry(default_completion_kwargs, messages, functions=None,function_call=None, stop=None,restrict_cache_query=True ,recorder:RunningRecoder=None, **args):
    """
    Executes a chat completion request without retry.

    Args:
        default_completion_kwargs (dict): The default completion keyword arguments.
        messages (list): The list of messages.
        functions (list, optional): The list of functions.
        function_call (str, optional): The function call.
        stop (str, optional): The stop string.
        restrict_cache_query (bool, optional): Whether to restrict cache query.
        recorder (RunningRecoder, optional): The recorder object.
        **args: Additional keyword arguments.

    Returns:
        tuple: A tuple containing the response and the LLMStatusCode.

    Raises:
        Exception: If an exception occurs during the execution.
    """
    for message in messages:
        if "content" not in message.keys():
            message["content"] = ""

    json_data = default_completion_kwargs
    json_data["messages"] = messages

    json_data.update(args)
    if stop is not None:
        json_data.update({"stop": stop})
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})

    try:

        if recorder:
            response = recorder.query_llm_inout(restrict_cache_query=restrict_cache_query,
                                                base_kwargs = default_completion_kwargs,
                                                messages=messages, 
                                                functions=functions, 
                                                function_call=function_call, 
                                                stop = stop,
                                                other_args = args,
                                                )
        else:
            response = None

        if response == None:
            response = _chat_completion_request_atomic(**json_data)
            response = json.loads(str(response))

        if recorder:
            recorder.regist_llm_inout(base_kwargs = default_completion_kwargs,
                                    messages=messages, 
                                    functions=functions, 
                                    function_call=function_call, 
                                    stop = stop,
                                    other_args = args,
                                    output_data = response)
        
        return response, LLMStatusCode.SUCCESS
    
    except Exception as e:
        traceback.print_exc()
        logger.info("Unable to generate ChatCompletion response")
        logger.info(f"Exception: {e}")
        if recorder:
            recorder.regist_llm_inout(base_kwargs = default_completion_kwargs,
                                    messages=messages, 
                                    functions=functions, 
                                    function_call=function_call, 
                                    stop = stop,
                                    other_args = args,
                                    output_data=f"Exception: {e}")
        return e, LLMStatusCode.ERROR

def _chat_completion_request(**args):
    """
    Generates a chat completion request with the given arguments and attempts to retrieve the completed output.

    Args:
        **args: Additional keyword arguments for the chat completion request.

    Returns:
        The completed output if the request is successful, otherwise None.
    """

    for i in range(3):
        if i > 0:
            logger.info(f"LLM retry for the {i+1}'th time")

        try:
            output, output_code = _chat_completion_request_without_retry(**args)
            if output_code == LLMStatusCode.SUCCESS:
                return output
        except func_timeout.exceptions.FunctionTimedOut: #TLE
            logger.info(f"LLM response time out")
            continue
