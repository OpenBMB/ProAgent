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
        task = "每当我触发Manual Trigger时，执行workflow，从 googleSheets 中读取业务流数据，里面有成本和销售额。计算业务流的利润（= 销售额 - 成本），并根据业务流的 descriptions，让 第一个 aiCompletion 判断业务流的类型（to B or to C），给业务经理发送盈利或亏损信息。若业务流类型为to B(to Business)，则发送消息到 slack。若业务流类型为to C（to Client），向该业务流经理发送一则提醒邮件，内容用 第二个 aiCompletion 生成。",
        additional_information=[
            "1. 所有的thought、comments都要用中文，让我看明白。\n",
            "2.1 Google Sheet的documentId(url)为：https://docs.google.com/spreadsheets/d/1_B038J1f3VW94z179OagFwEtnr3k5mTyXKBTPI2Fw-U/edit#gid=1759497495\n",
            "2.2 Google sheetName(url)为https://docs.google.com/spreadsheets/d/1_B038J1f3VW94z179OagFwEtnr3k5mTyXKBTPI2Fw-U/edit#gid=1759497495\n"
            "3.1 使用 ai node1 判断是否存在业务流，你可以使用aiCompletion node（注意调整 Prompt!)，如果 ai 的回答中包含 'to B'，则业务流类型是to B，如果包含 'to C'，则业务流类型是to C。\n"
            "4.1 Slack Channel 选择 #general.\n",
            "4.2 邮件内容使用 ai node2 生成。\n"
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