# %%

import subprocess
from pathlib import Path

time_dict_conv = {}
time_dict_noconv = {}

p = Path(".")

for filename in p.glob("*.py"):
    cmd = f"python {filename}"
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True
    )  # type: ignore
    out, err = p.communicate()
    Path(filename)
    result = out.decode().split("\n")[0]
    print(f"{filename.stem}: {result}")

    if "noconv" in filename.stem:
        time_dict_noconv[filename.stem.split("_")[0]] = float(result)
    else:
        time_dict_conv[filename.stem.split("_")[0]] = float(result)
