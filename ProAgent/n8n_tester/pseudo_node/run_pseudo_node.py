import json
from ProAgent.agent.gpt4_function import OpenAIFunction
from ProAgent.agent.utils import _chat_completion_request, _chat_completion_request_without_retry
from ProAgent.config import CONFIG
from ProAgent.n8n_parser.workflow import n8nPythonWorkflow
from ProAgent.n8n_parser.node import n8nPythonNode
from ProAgent.n8n_tester.pseudo_node.ai_node import run_ai_completion
from ProAgent.n8n_tester.pseudo_node.utils import fill_return_data, replace_exp

agent = OpenAIFunction()

def run_pseudo_workflow(input_data: list, constant_workflow: n8nPythonWorkflow) -> str:
    """
    Run a pseudo workflow using the provided input data and constant workflow.

    Args:
        input_data (list): The input data for the pseudo workflow.
        constant_workflow (n8nPythonWorkflow): The constant workflow to be used.

    Returns:
        str: The final return data of the pseudo workflow.
    """
    # import pdb; pdb.set_trace()
    node_var:n8nPythonNode = constant_workflow['nodes'][-1]
    params_raw = node_var['parameters']

    # params_list = replace_exp(input_data, params_raw)
    params_list = [params_raw]

    if node_var['type'].split('.')[-1] == 'aiCompletion':
        return_list = run_ai_completion(params_list)
    else:
        return_list = []
    final_return_data = fill_return_data(return_list)

    return final_return_data
