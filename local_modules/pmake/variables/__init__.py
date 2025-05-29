'''
This represents variables that can be used in pmake.yml file.
'''
from .variable_core import Variables
from .variable_core import VarError
from .variables import add_cmdline_variable
from .variables import add_builtin_variable
from .variables import define_local_variable

from .variables import scope_push
from .variables import scope_pop

from .variables import expand_text
from .variables import reduce_text
