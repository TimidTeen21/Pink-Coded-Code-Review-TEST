# Intentional issues:
# - Unused import (F401)
# - Undefined variable (F821)
# - Line too long (E501)

import os
import sys

def calculate():
    x = 1
    y = 2
    z = x + y + some_undefined_variable  # F821
    return z

# Very long line -----------------------------------------------------------------------------------------------------------------------------------