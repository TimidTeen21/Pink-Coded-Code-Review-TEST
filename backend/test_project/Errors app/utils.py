import logging
import sys

# Insecure logging configuration
logging.basicConfig(level=logging.DEBUG)

def log_message(message):
    # Logs user input without sanitization
    logging.info(message)

# Redundant and poorly named function
def doStuff(x, y):
    z = x + y
    return z

# Unused function
def unused_function():
    pass

# Function with too many parameters
def process_data(a, b, c, d, e, f, g, h):
    return a + b + c + d + e + f + g + h