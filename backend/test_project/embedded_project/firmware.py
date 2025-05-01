# Intentional issues:
# - Missing docstring (C0114)
# - Unused variable (W0612)

def read_sensor():
    value = 42  # W0612
    return 3.14

class MotorController:
    def __init__(self):
        self.speed = 0