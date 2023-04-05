import clog

errors = 0

def error(msg):
    global errors
    errors += 1
    clog.error(msg)

def errorp(msg):
    """only prints the error without clog.error"""
    global errors
    errors += 1
    print(msg)

def fail(code=0):
    print("Compilation terminated due to previous error(s).")
    exit(code)
