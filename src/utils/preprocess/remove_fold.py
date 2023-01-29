import os
from pathlib import Path
import subprocess

def remove_fold_and_file(spkid):

    receive_path = "/tmp/"
    spk_dir = os.path.join(receive_path, str(spkid))
    cmd = f"rm -rf {spk_dir}"
    subprocess.run(cmd, shell=True)
    return

# def remove_fold_and_file(spkid):

#     receive_path = "/tmp/"
#     spk_dir = os.path.join(receive_path, str(spkid))
#     cmd = f"rm -rf {spk_dir}"
#     os.system(cmd)
#     return

