from concurrent.futures import process
import os
import clog
import subprocess as sp
import sys

def test(filename):
    split_text = os.path.splitext(filename)
    extless = split_text[0]
    
    if split_text[-1] == ".as":
        stdout = []
        stderr = []
        clog.log(f"Compiling to tests/{extless}.asb")
        
        proc = sp.run([sys.executable, 
                        f"main.py", f"tests/{filename}", f"tests/{extless}.asb"],
                        capture_output=True)
        
        [stdout.append(a.decode("utf-8") + "\n") for a in proc.stdout.splitlines()]
        [stderr.append(a.decode("utf-8") + "\n") for a in proc.stderr.splitlines()]
        
        ret = proc.returncode
        
        clog.log(f"Running tests/{extless}.asb")
        proc = sp.run(["C:\\Users\\gamed\\Documents\\projs\\alphassembly\\Alphassembly\\Alphassembly\\bin\\Release\\net6.0\\Alphassembly.exe", 
                       f"tests\\{extless}.asb"],
                      capture_output=True)
        
        [stdout.append(a.decode("utf-8") + "\n") for a in proc.stdout.splitlines()]
        [stderr.append(a.decode("utf-8") + "\n") for a in proc.stderr.splitlines()]
        ret = proc.returncode if ret == 0 else ret
        
        with open(f"tests/{extless}.txt", "w") as log:
            if not ret == 0:
                log.write(f"This test failed with exit code: {ret}\n\n")
            else:
                log.write(f"This test succeded with exit code: {ret}\n\n")
            log.write("stdout:\n")
            log.writelines(stdout)
            log.write("\nstderr:\n")
            log.writelines(stderr)
        
        if ret != 0:
            clog.error(f"Test of {filename} failed with exit code: {ret}")
            return ret
        
    return 0

errors = 0
for file in os.listdir("tests"):
    if test(file) != 0:
        errors += 1

msg = " errors" if errors >= 2 or errors == 0 else " error"
print(f"\nTesting ended with {errors}" + msg)

if errors != 0:
    print("See text files in the tests directory to see what caused the error(s)")
    