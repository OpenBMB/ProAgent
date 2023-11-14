from dataclasses import dataclass,field
import re
from typing import List

from ProAgent.utils import WorkflowType, TestResult

@dataclass
class n8nPythonWorkflow():
    workflow_name: str = ""
    workflow_type: WorkflowType = WorkflowType.Main
    implement_code: str = ""
    implement_code_clean: str = ""

    last_runtime_info: TestResult = field(default_factory= lambda: TestResult())

    def print_self_clean(self):
        """
        Cleans the implement code by removing single-line comments and multi-line comments.

        Returns:
            str: The cleaned implement code.
        """
        implement_code_clean = self.implement_code
        implement_code_clean = re.sub(r'""".*?"""', '', implement_code_clean, flags=re.DOTALL)
        return implement_code_clean

    def print_self(self):
        """
        Print the value of the `implement_code` attribute of the current instance.

        Returns:
            The value of the `implement_code` attribute.
        """
        return self.implement_code

    def print_self_old(self):
        """
        Generates the function comment for the given function body.

        Args:
            self (object): The current instance of the class.
        
        Returns:
            list: The lines of the generated function comment.
        """
        lines = []
        name = "mainWorkflow" if self.workflow_type == WorkflowType.Main else f"subworkflow_{self.workflow_id}"
        input_name = "trigger_input" if self.workflow_type == WorkflowType.Main else f"father_workflow_input"
        line1 = f"def {name}({input_name}: [{{...}}]):"
        lines.append(line1)
        if self.comments != "" or self.TODOS != []:
            lines.append(f"  \"\"\"")
        if self.comments != "":
            lines.append(f"  comments: {self.comments}")
        
        if self.TODOS != []:
            lines.append(f"  TODOs: ")
            for todo in self.TODOS:
                lines.append(f"    - {todo}")
        lines.append(f"  \"\"\"")

        if self.implement_code != "":
            lines.append(self.implement_code)
        else:
            lines.append("  raise NotImplementedError")

        return lines