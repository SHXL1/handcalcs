#    Copyright 2020 Connor Ferster

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import sys
from . import handcalcs as hand
from . import sympy_kit as s_kit

try: 
    from IPython.core.magic import (Magics, magics_class, cell_magic, register_cell_magic)
    from IPython import get_ipython
    from IPython.core.magics.namespace import NamespaceMagics
    from IPython.display import Latex, Markdown, display
    from IPython.utils.capture import capture_output
except ImportError:
    pass


try:
    _nms = NamespaceMagics()
    _Jupyter = get_ipython()
    _nms.shell = _Jupyter.kernel.shell
    cell_capture = capture_output(stdout=True, stderr=True, display=True)
except AttributeError:
    raise ImportError("handcalcs.render is intended for a Jupyter environment."
    " Use 'from handcalcs import handcalc' for the decorator interface.")

def parse_line_args(line: str) -> dict:
    """
    Returns a dict that represents the validated arguments
    passed in as a line on the %%render or %%tex cell magics.
    """
    valid_args = ["parameters", "long", "short", "symbolic", "sympy"]
    line_parts = line.split()
    precision = 3
    parsed_args = {"override": "", "precision": 3}
    for arg in line_parts:
        for valid_arg in valid_args:
            if arg.lower() in valid_arg: 
                parsed_args.update({"override": valid_arg})
                break
        try:
            precision = int(arg)
            parsed_args.update({"precision": precision})
        except ValueError:
            pass
    return parsed_args


@register_cell_magic
def render(line, cell):
    # Retrieve var dict from user namespace
    var_list = _nms.who_ls()
    var_dict = {v: _nms.shell.user_ns[v] for v in var_list}

    line_args = parse_line_args(line)
    if line_args["override"] == "sympy":
        cell = s_kit.convert_sympy_cell_to_py_cell(cell, var_dict)
    
    # Run the cell
    with cell_capture:
        exec_result = _nms.shell.run_cell(cell)

    if not exec_result.success:
        return None


    # Retrieve updated variables (after .run_cell(cell))
    var_list = _nms.who_ls()
    var_dict = {v: _nms.shell.user_ns[v] for v in var_list}

    # Do the handcalc conversion
    renderer = hand.LatexRenderer(cell, var_dict)
    latex_code = renderer.render()

    # Display, but not as an "output"
    display(Latex(latex_code))


@register_cell_magic
def tex(line, cell):
    # Run the cell
    _nms.shell.run_cell(cell)
    
    # Retrieve variables from the local namespace
    var_list = _nms.who_ls()
    var_dict = {v: _nms.shell.user_ns[v] for v in var_list}

    # Do the handcalc conversion
    renderer = hand.LatexRenderer(cell, var_dict)
    latex_code = renderer.render()

    # Display, but not as an "output"
    print(latex_code)

def load_ipython_extension(ipython):
    """This function is called when the extension is
    loaded. It accepts an IPython InteractiveShell
    instance. We can register the magic with the
    `register_magic_function` method of the shell
    instance."""
    ipython.register_magic_function(render, 'cell')
