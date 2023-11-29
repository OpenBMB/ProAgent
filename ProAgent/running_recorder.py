
import os

import time
import json
from colorama import Fore
from termcolor import colored

from ProAgent.config import CONFIG

from ProAgent.router.utils import ENVIRONMENT
from ProAgent.utils import Action
from ProAgent.loggers.logs import logger

def dump_common_things(object):
    """
    Generates a function comment for the given function body.

    Args:
        object: The object to be processed.

    Returns:
        The processed object.

    """
    if type(object) in [str,int,float, bool]:
        return object
    if type(object) == dict:
        return {dump_common_things(key): dump_common_things(value) for key,value in object.items()}
    if type(object) == list:
        return [dump_common_things(cont) for cont in object]
    method = getattr(object, 'to_json', None)
    if callable(method):
        return method()

class RunningRecoder():
    def __init__(self, record_base_dir = "./records"):
        """
        Initializes the object with the given record base directory.

        Parameters:
            record_base_dir (str): The base directory for the records. Defaults to "./records".

        Returns:
            None
        """

        self.llm_record_cache = [] # Get cached records

        self.llm_interface_id = 0
        self.llm_server_cache = [] # Runtime records
        self.tool_call_id = 0
        self.tool_call_cache = []
        self.is_cached = True # Assume to be true at first
        self.newly_start = True

        now = int(round(time.time()*1000))
        strip = time.strftime('%Y_%m_%d_%H_%M_%S',time.localtime(now/1000))

        self.record_root_dir = os.path.join(record_base_dir,strip)
        os.makedirs(self.record_root_dir,exist_ok=True)

        print(colored(f"Recorder Mode: {CONFIG.environment.name}", color='yellow'))

        for subdir_name in ["LLM_inout_pair","tool_call_logs"]:
            os.makedirs(os.path.join(self.record_root_dir,subdir_name),exist_ok=True)
            

    def save_meta(self):
        """
        Saves the meta information of the record.

        This function writes the meta information of the record to a file in the
        record root directory. The meta information includes the tool call ID and
        the LLM inference ID.

        Parameters:
            None

        Returns:
            None
        """
        with open(os.path.join(self.record_root_dir, "meta.meta"), "w", encoding="utf-8") as writer:
            tool_call_log = {
                "tool_call_id": self.tool_call_id,
                "llm_inference_id": self.llm_interface_id,
            }
            json.dump(tool_call_log,writer,indent=2, ensure_ascii=False)

    def load_from_disk(self, record_dir: str, cfg):
        """
        Load data from disk into memory cache.

        Args:
            record_dir (str): The directory path where the data is stored.
            cfg: The configuration object.

        Returns:
            None
        """
        logger.typewriter_log(
            "load from a disk record",
            Fore.RED,
            record_dir,
        )
        self.newly_start = False
        for dir_name in os.listdir(record_dir):
            if dir_name == "LLM_inout_pair":
                inout_pair_list = os.listdir(os.path.join(record_dir,dir_name))
                inout_pair_list.sort()
                for file_name in inout_pair_list:
                    with open(os.path.join(record_dir,dir_name,file_name), "r", encoding="utf-8") as reader:
                        llm_pair = json.load(reader)
                        self.llm_record_cache.append(llm_pair)
            elif dir_name == "meta.meta":
                with open(os.path.join(record_dir, "meta.meta"), "r", encoding="utf-8") as reader:
                    tool_call_log = json.load(reader)
        
    
    def regist_llm_inout(self, base_kwargs, messages, functions, function_call, stop, other_args, output_data, uuid=""):
        """
        Registers the LLM input and output data for the specified function call. 

        Args:
            base_kwargs (dict): The base keyword arguments for the function call.
            messages (list): The list of messages associated with the function call.
            functions (list): The list of functions called during the function call.
            function_call (str): The function call being registered.
            stop (bool): A flag indicating whether the function call should stop.
            other_args (list): The list of other arguments for the function call.
            output_data (Any): The output data for the function call.
            uuid (str, optional): The UUID associated with the function call. Defaults to "".

        Returns:
            None

        Raises:
            None
        """
        with open(os.path.join(self.record_root_dir, "LLM_inout_pair", f"{self.llm_interface_id:05d}.json"), "w", encoding="utf-8") as writer:
            llm_inout_record = {
                "input": {
                    "base_kwargs": dump_common_things(base_kwargs),
                    "messages":dump_common_things(messages),
                    "functions":dump_common_things(functions),
                    "function_call":dump_common_things(function_call),
                    "stop":dump_common_things(stop),
                    "other_args":dump_common_things(other_args),
                    # 'uuid': dump_common_things(uuid)
                },
                "output": dump_common_things(output_data),
                "llm_interface_id": self.llm_interface_id,
            }
            json.dump(llm_inout_record,writer,indent=2, ensure_ascii=False)
            self.llm_server_cache.append(llm_inout_record)

        self.llm_interface_id += 1
        self.save_meta()


    def query_llm_inout(self, restrict_cache_query, base_kwargs, messages, functions, function_call, stop, other_args, uuid=""):
        """
        Query the LLM server for input and output data based on the given parameters.
        
        Parameters:
        - restrict_cache_query (bool): Whether to restrict the cache query.
        - base_kwargs (dict): A dictionary of base keyword arguments.
        - messages (list): A list of messages.
        - functions (list): A list of functions.
        - function_call (dict): A dictionary representing the function call.
        - stop (bool): Whether to stop the query.
        - other_args (dict): A dictionary of other arguments.
        - uuid (str): A string representing the UUID (optional).
        
        Returns:
        - object: The output data from the LLM server, or None if not found.
        """

        
        if CONFIG.environment == ENVIRONMENT.Development or self.newly_start:
            self.is_cached = False
            return None
        elif CONFIG.environment == ENVIRONMENT.Refine:
            input_data = {
                "base_kwargs": dump_common_things(base_kwargs),
                "messages":dump_common_things(messages),
                "functions":dump_common_things(functions),
                "function_call":dump_common_things(function_call),
                "stop":dump_common_things(stop),
                "other_args":dump_common_things(other_args),
            }
            for cache in self.llm_record_cache:
                # compare user messages only
                input_data_user_messages = [item for item in input_data['messages'] if item['role'] == 'user']
                cache_data_user_messages = [item for item in cache["input"]['messages'] if item['role'] == 'user']
                if input_data_user_messages == cache_data_user_messages:
                    if restrict_cache_query and self.llm_interface_id != cache["llm_interface_id"]:
                        continue
                    logger.typewriter_log(
                        f"get a llm_server response from Record {cache['llm_interface_id']}",
                        Fore.RED,
                    )
                    self.is_cached = True
                    return cache["output"]
            self.is_cached = False
            return None
        elif CONFIG.environment == ENVIRONMENT.Production:
            if self.llm_interface_id < len(self.llm_record_cache):
                logger.typewriter_log(
                    "get a llm_server response from Record",
                    Fore.RED,
                )
                self.is_cached = True
                return self.llm_record_cache[self.llm_interface_id]['output']
            else:
                self.is_cached = False
                return None
        else:
            self.is_cached = False
            return None
            

    def regist_tool_call(self, action: Action, now_code: str):
        """
        Registers a tool call by saving the action and code to files.

        Args:
            action (Action): The action to be saved.
            now_code (str): The current code to be saved.

        Returns:
            None
        """
        with open(os.path.join(self.record_root_dir, "tool_call_logs", f"{self.tool_call_id:05d}_tool.json"), "w", encoding="utf-8") as writer:
            tool_call_log = action.to_json()
            json.dump(tool_call_log,writer,indent=2, ensure_ascii=False)
        with open(os.path.join(self.record_root_dir, "tool_call_logs", f"{self.tool_call_id:05d}_code.py"), "w", encoding="utf-8") as writer:
            writer.write(now_code)

        self.tool_call_id += 1

        self.save_meta()

    def save_markdown(self, markdown):
        """
        Save the given markdown content to a file.

        Parameters:
            markdown (str): The markdown content to be saved.

        Returns:
            None
        """
        with open(os.path.join(self.record_root_dir, f"README.md"), "w", encoding="utf-8") as writer:
            writer.write(markdown)
    
    def is_final_cache(self):
        """
        Check if the current cache is the final cache.

        Returns:
            bool: True if the current cache is the final cache, False otherwise.
        """
        return self.llm_interface_id + 1 >= len(self.llm_record_cache)