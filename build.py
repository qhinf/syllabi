import os
import re
import shutil
import subprocess
import sys
import yaml

from git import Repo
from jinja2 import Environment, FileSystemLoader, select_autoescape
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
    
year_block_pattern = re.compile(r"(\d{2})(\d{2})-(\d)")

# Create directory for the HTML build files
if path.exists("_build"):
    shutil.rmtree("_build")
shutil.copytree("static", "_build")

# Read the base configuration file into a Python dictionary
with open("_config_base.yml", mode = "r") as config_base_file:
    config_base = yaml.safe_load(config_base_file)

modules = []
for module in os.listdir(get_repo_path()):
    module_title = module
    versions = []

    for version in os.listdir(get_repo_path(module)):
        build_path = path.join("_build", module, version)
        repo_path = get_repo_path(module, version)
        jb_path = path.join(repo_path, "syllabus")
        jb_build_path = path.join(jb_path, "_build", "html")
        jb_build_version = path.join(jb_build_path, "version")

        repo = Repo(repo_path)
        
        with open(path.join(jb_path, "_config.yml"), mode = "r") as ref_config_file:
            ref_config = yaml.safe_load(ref_config_file)

        if (match := year_block_pattern.match(version)) is not None:
            version_title = f"{match.group(1)}/{match.group(2)} - Blok {match.group(3)}"
        else:
            version_title = version

        needs_build = True
        # Skip this build if the built version is the same as the current repo
        # head commit SHA
        if path.exists(jb_build_version):
            with open(jb_build_version, mode = "r", encoding = "utf-8") as version_file:
                if version_file.read().strip() == repo.head.commit.hexsha:
                    print(f"[{module}/{version}] Skipping build: already up to date", file = sys.stderr)
                    needs_build = False
            
        if needs_build:
            authors = { 
                commit.author.name 
                for commit in repo.iter_commits(repo.head) 
                if commit.author.name is not None 
            }

            copyright_year = repo.commit(repo.head).authored_datetime.year

            new_ref_config = merge({}, config_base, ref_config)

            new_ref_config["author"] = "Q-highschool + " + ", ".join(authors)
            new_ref_config["copyright"] = str(copyright_year)

            new_ref_config["html"]["baseurl"] = f"/{module}/{version}"

            new_ref_config["sphinx"]["config"]["myst_substitutions"]["versie"] = version_title

            # new_ref_config["repository"]["url"] = syllabus_info["repo"]
            # new_ref_config["repository"]["branch"] = rev

            with open(path.join(jb_path, "_config_ext.yml"), mode = "w") as ref_config_ext_file:
                yaml.dump(new_ref_config, ref_config_ext_file)

            print(f"[{module}/{version}] Starting Jupyter Book build")
            jb_result = subprocess.run([ "jupyter-book", "build", "--config", path.join(jb_path, "_config_ext.yml"), jb_path ], timeout = 2 * 60)
            if jb_result.returncode != 0:
                print(f"[{module}/{version}] Jupyter Book build failed", file = sys.stderr)
                build_success = False
            else:
                print(f"[{module}/{version}] Jupyter Book build succeeded")
                build_success = True
                # Write the commit SHA to detect unchanged syllabi
                with open(jb_build_version, mode = "w", encoding = "utf-8") as version_file:
                    version_file.write(repo.head.commit.hexsha)
            
            os.remove(path.join(jb_path, "_config_ext.yml"))

        if not needs_build or build_success:
            print(f"[{module}/{version}] Copying HTML")
            shutil.rmtree(build_path, ignore_errors = True)
            shutil.copytree(jb_build_path, build_path)

        module_title = ref_config["title"]
        versions.append({ "slug": version, "title": version_title })

    versions.sort(key = lambda version: version["slug"], reverse = True)
    modules.append({ "slug": module, "title": module_title, "versions": versions })

modules.sort(key = lambda module: module["title"])

jinja_env = Environment(loader = FileSystemLoader("templates"), autoescape = select_autoescape())

index_template = jinja_env.get_template("index.html")
print(f"[index] Writing index.html")
with open(path.join("_build", "index.html"), mode = "w") as index_file:
    index_file.write(index_template.render(modules = modules))

module_index_template = jinja_env.get_template("module_index.html")
for module in modules:
    print(f"[{module['slug']}] Writing index.html")
    with open(path.join("_build", module["slug"], "index.html"), mode = "w") as module_index_file:
        module_index_file.write(module_index_template.render(module = module))
