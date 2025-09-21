from typing import Type

from virtue_code_eval.code_tasks.base_task import Task

from .generation.insecure_code import CybersecevalAutocomplete, CybersecevalInstruct
from .generation.malicious_code import (
    CybersecevalAutonomousUplift,
    CybersecevalMitre,
    RedcodeGen,
)
from .generation.secodeplt import (
    SecodepltPythonAutocomplete,
    SecodepltArvoAutocomplete,
    SecodepltAutocompleteCursor,
    SecodepltPythonInstruct,
    SecodepltInstructCursor,
    SecodepltJulietAutocomplete,
    SecodepltJulietPatch
)
from .generation.secodeplt.text_to_code.helpfulness import SecodepltAttackHelpfulness
from .generation.tool_abuse import CybersecevalInterpreter
from .reasoning.exploitation import CybersecevalCanaryExploit


def _auto_register_tasks() -> dict[str, Type[Task]]:
    """Automatically register all Task subclasses using their TASK_FULL_NAME"""
    registry = {}

    # Get all imported classes in the current module
    import sys
    current_module = sys.modules[__name__]

    for name in dir(current_module):
        obj = getattr(current_module, name)
        # Check if it's a Task subclass (but not the base Task class itself)
        if (isinstance(obj, type) and
                issubclass(obj, Task) and
                obj is not Task and
                hasattr(obj, 'TASK_FULL_NAME')):
            registry[obj.TASK_FULL_NAME] = obj

    return registry


# Combine manual and auto-registered tasks
SAFETY_TASK_REGISTRY: dict[str, Type[Task]] = {
    **_auto_register_tasks()
}
