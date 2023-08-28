import os
import shutil
import subprocess
import sys
import yaml

from git import Repo
from mergedeep import merge
from os import path

def get_repo_path(module: str | None = None, version: str | None = None) -> str:
    syllabi_folder = "syllabi"
    if module is None:
        return syllabi_folder
    elif version is None:
        return path.join(syllabi_folder, module)
    else:
        return path.join(syllabi_folder, module, version)

# Create directory for the HTML build files
os.makedirs("_build", exist_ok = True)

# Read the base configuration file into a Python dictionary
with open("_config_base.yml", mode = "r") as config_base_file:
    config_base = yaml.safe_load(config_base_file)

for module in os.listdir(get_repo_path()):
    for version in os.listdir(get_repo_path(module)):
        repo_path = get_repo_path(module, version)
        jb_path = path.join(repo_path, "syllabus")
        repo = Repo(repo_path)

        authors = { 
            commit.author.name 
            for commit in repo.iter_commits(repo.head) 
            if commit.author.name is not None 
        }

        copyright_year = repo.commit(repo.head).authored_datetime.year

        with open(path.join(jb_path, "_config.yml"), mode = "r") as ref_config_file:
            ref_config = yaml.safe_load(ref_config_file)
        
        new_ref_config = merge({}, config_base, ref_config)

        new_ref_config["author"] = "Q-highschool + " + ", ".join(authors)
        new_ref_config["copyright"] = copyright_year

        new_ref_config["html"]["baseurl"] = f"/{module}/{version}"

        # new_ref_config["repository"]["url"] = syllabus_info["repo"]
        # new_ref_config["repository"]["branch"] = rev
        
        with open(path.join(jb_path, "_config_ext.yml"), mode = "w") as ref_config_ext_file:
            yaml.dump(new_ref_config, ref_config_ext_file)

        print(f"[{module}/{version}] Starting Jupyter Book build")
        jb_result = subprocess.run([ "jupyter-book", "build", "--config", path.join(jb_path, "_config_ext.yml"), jb_path ], timeout = 2 * 60)
        if jb_result.returncode != 0:
            print(f"[{module}/{version}] Jupyter Book build failed", file = sys.stderr)
        else:
            print(f"[{module}/{version}] Jupyter Book build succeeded, copying HTML files")
            shutil.rmtree(path.join("_build", module, version), ignore_errors = True)
            shutil.copytree(path.join(jb_path, "_build", "html"), path.join("_build", module, version))

        os.remove(path.join(jb_path, "_config_ext.yml"))
