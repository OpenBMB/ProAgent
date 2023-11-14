from ast import literal_eval

from ProAgent.router.utils import ENVIRONMENT


class CfgNode:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return self._str_helper(0)

def _str_helper(self, indent):
    """
    Helper function to support nested indentation for pretty printing.

    Args:
        indent (int): The current indentation level.

    Returns:
        str: The string representation of the object.
    """
    parts = []
    
    # Iterate over the attributes of the object
    for k, v in self.__dict__.items():
        if isinstance(v, CfgNode):
            parts.append("%s:\n" % k)
            parts.append(self._str_helper(indent + 1))  # Recursive call for nested objects
        else:
            parts.append("%s: %s\n" % (k, v))
    
    # Add indentation to each part
    parts = [' ' * (indent * 4) + p for p in parts]
    
    # Concatenate the parts into a single string
    return "".join(parts)

    def to_dict(self):
        """ return a dict representation of the config """
        return { k: v.to_dict() if isinstance(v, CfgNode) else v for k, v in self.__dict__.items() }

    def merge_from_dict(self, d):
        self.__dict__.update(d)

def merge_from_args(self, args):
    """
    Update the configuration from a list of strings that is expected
    to come from the command line, i.e. sys.argv[1:].

    The arguments are expected to be in the form of `--arg=value`, and
    the arg can use . to denote nested sub-attributes. Example:

    --model.n_layer=10 --trainer.batch_size=32

    Args:
        args (list): A list of strings representing command line arguments.

    Raises:
        AssertionError: If an override argument is not in the form of `--arg=value`.
        AssertionError: If the specified attribute does not exist in the config.

    """
    for arg in args:
        keyval = arg.split('=')
        assert len(keyval) == 2, "Expecting each override arg to be of form --arg=value, got %s" % arg
        key, val = keyval # unpack

        # First translate val into a python object
        try:
            val = literal_eval(val)
        except ValueError:
            pass

        # Find the appropriate object to insert the attribute into
        assert key[:2] == '--'
        key = key[2:] # strip the '--'
        keys = key.split('.')
        obj = self
        for k in keys[:-1]:
            obj = getattr(obj, k)
        leaf_key = keys[-1]

        # Ensure that this attribute exists
        assert hasattr(obj, leaf_key), f"{key} is not an attribute that exists in the config"

        # Overwrite the attribute
        print("Command line overwriting config attribute %s with %s" % (key, val))
        setattr(obj, leaf_key, val)

from .n8n_parser.knowledge import knowledge

class RPAgentConfig(CfgNode):

    @staticmethod
    def get_default_config():
        C = CfgNode()

        C.default_completion_kwargs = {
            'model': 'gpt-4-32k',
            'temperature': 0.5,
            'request_timeout':30,
            'max_tokens': 4096,
            'frequency_penalty': 0, 
            'presence_penalty': 0
        }

        C.default_knowledge = knowledge

        C.environment = ENVIRONMENT.Production

        return C
    
CONFIG = RPAgentConfig.get_default_config()