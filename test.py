def bad_function():
    x = 1
    y = 2
    return x + y  # unused variable y

if __name__ == "__main__":
    bad_function()
