import re

with open("platform-new/src/routes/fleet-guardian.tsx", "r") as f:
    code = f.read()

target = """                <MiniSpark seed={a.current_soh} />"""
replacement = """                <MiniSpark seed={a.current_soh * 100} />"""

if target in code:
    code = code.replace(target, replacement)
else:
    print("Target not found!")

with open("platform-new/src/routes/fleet-guardian.tsx", "w") as f:
    f.write(code)

