from copy import deepcopy
from typing import List, Dict
import json
from ProAgent.frontend.highlight_code import highlight_code
from ProAgent.running_recorder import RunningRecoder

from ProAgent.handler import react_prompt
from ProAgent.utils import userQuery, Action
from ProAgent.agent.gpt4_function import OpenAIFunction
from ProAgent.n8n_parser.compiler import Compiler
from ProAgent.loggers.logs import logger
from ProAgent.n8n_parser.intrinsic_functions import get_intrinsic_functions
from ProAgent.config import CONFIG

class ReACTHandler():
    def __init__(self, cfg, query:userQuery, compiler: Compiler, recorder: RunningRecoder):
        """
        Initializes a new instance of the class.

        Args:
            cfg (type): The cfg parameter description.
            query (userQuery): The query parameter description.
            compiler (Compiler): The compiler parameter description.
            recorder (RunningRecoder): The recorder parameter description.
        
        Attributes:
            messages (List[Dict]): The messages attribute description.
            actions (List[Action]): The actions attribute description.
        """
        self.query = query
        self.refine_prompt = query.refine_prompt
        self.cfg = cfg
        self.compiler = compiler
        self.recorder = recorder
        self.messages: List[Dict] = []
        self.actions: List[Action] = []
    def run(self):
        """
        Runs the main loop for the program.

        This function continuously executes a loop that performs the following steps:
        1. Appends system prompts to the list of messages.
        2. Replaces placeholders in a specific prompt and appends it to the list of messages.
        3. Appends assistant messages and function outputs to the list of messages.
        4. Prints highlighted code.
        5. Replaces placeholders in the user prompt and appends it to the list of messages.
        6. Retrieves intrinsic functions.
        7. Parses messages using an OpenAIFunction agent.
        8. Handles tool calls using the compiler.
        9. Appends the parsed message and action to the list of messages and actions, respectively.

        This function does not have any parameters and does not return anything.

        Note: This function runs indefinitely until interrupted.
        """
        while True:
            messages = []
            messages.append({"role":"system","content": deepcopy(react_prompt.system_prompt_1)})
            messages.append({"role":"system","content": deepcopy(react_prompt.system_prompt_2)})

            specific_prompt = deepcopy(react_prompt.system_prompt_3)
            specific_prompt = specific_prompt.replace("{{user_query}}", self.query.print_self())
            specific_prompt = specific_prompt.replace("{{flatten_tools}}", self.compiler.print_flatten_tools())
            messages.append({"role":"system","content": specific_prompt})

            # cut some messages down, only allow for last_num messages
            last_num = 3
            for k, (assistant_message, parsed_action) in enumerate(zip(self.messages, self.actions)):
                if k < len(self.messages) - last_num:
                    continue
                messages.append(assistant_message)
                messages.append({
                    "role":"function",
                    "name": parsed_action.tool_name,
                    "content": parsed_action.tool_output,
                })
            

            user_prompt = deepcopy(react_prompt.user_prompt)

            refine_prompt = ""
            if len(self.refine_prompt) > 0:
                refine_prompt = f"The user have some additional requirements to your work. Please refine your work based on the following requirements:\n ```\n{deepcopy(self.refine_prompt)}```\n"

            user_prompt = user_prompt.replace("{{refine_prompt}}", refine_prompt)

            # print highlighted code
            highlighted_code = highlight_code(self.compiler.code_runner.print_clean_code(indent=4))
            user_prompt_colored = user_prompt.split("{{now_codes}}")
            user_prompt_colored = highlighted_code.join(user_prompt_colored)
            logger.typewriter_log(user_prompt_colored)

            user_prompt = user_prompt.replace("{{now_codes}}", self.compiler.code_runner.print_code())

            messages.append({"role":"user","content": user_prompt})
            
            functions = get_intrinsic_functions()

            agent = OpenAIFunction()
            content, function_name, function_arguments, message = agent.parse(messages=messages,
                                                            functions=functions,
                                                            default_completion_kwargs=CONFIG.default_completion_kwargs,
                                                            recorder=self.recorder)
            action = self.compiler.tool_call_handle(content, function_name, function_arguments)
            self.messages.append(message)
            self.actions.append(action)
            # exit()