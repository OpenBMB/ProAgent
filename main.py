import hydra
import omegaconf
import logging
from colorama import Fore, Style
import json

from mock_agent import mock_function_call_list

from ProAgent.loggers.logs import logger
from ProAgent.n8n_parser.compiler import Compiler
from ProAgent.handler.ReACT import ReACTHandler
from ProAgent.utils import userQuery
from ProAgent.running_recorder import RunningRecoder


@hydra.main(config_path="ProAgent/configs", config_name="generate_n8n_query")
def main(cfg: omegaconf.DictConfig):
    """
    The main function that runs the ReACTHandler.

    Args:
        cfg (omegaconf.DictConfig): The configuration object.
        
    Returns:
        None
    """
    
    recorder = RunningRecoder()

    record_dir = None
    record_dir = "./apa_case"

    if record_dir != None:
        recorder.load_from_disk(record_dir, cfg) 


    # commercial
    query = userQuery(
        task = "Whenever I trigger the Manual Trigger, execute the workflow, and read the business flow data from googleSheets, which contains cost and sales. Calculate the profit of the business flow (= sales - cost), and based on the descriptions of the business flow, let the first aiCompletion determine the business flow type (to B or to C), and send profit or loss information to the business manager. If the business flow type is to B (to Business), send a message to slack. If the business flow type is to C (to Client), send a reminder email to the business flow manager, with the content generated by the second aiCompletion.",
        additional_information=[
            "1. All thoughts and comments should be in Chinese for me to understand.\n",
            "2.1 The documentId(url) of Google Sheet is: https://docs.google.com/spreadsheets/d/1_B038J1f3VW94z179OagFwEtnr3k5mTyXKBTPI2Fw-U/edit#gid=1759497495\n",
            "2.2 The sheetName(url) of Google is: https://docs.google.com/spreadsheets/d/1_B038J1f3VW94z179OagFwEtnr3k5mTyXKBTPI2Fw-U/edit#gid=1759497495\n"
            "3.1 Use ai node1 to determine if there is a business flow, you can use the aiCompletion node (remember to adjust the Prompt!), if the ai's answer contains 'to B', then the business flow type is to B, if it contains 'to C', then the business flow type is to C.\n"
            "4.1 Choose #general for the Slack Channel.\n",
            "4.2 Use ai node2 to generate the email content.\n"
        ],
        refine_prompt=""
    )

    compiler = Compiler(cfg, recorder)

    handler = ReACTHandler(cfg=cfg,
                            query=query,
                            compiler=compiler,
                            recorder=recorder)
    handler.run()

if __name__ == "__main__":
    main()