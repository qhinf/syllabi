import os
import shutil
import subprocess
import sys
import yaml

from git import Repo
from mergedeep import merge
from os import path

def get_main_repo_path(syllabus_name):
    return path.join("_source", "_git", syllabus_name)

def get_rev_repo_folder(syllabus_name):
    return path.join("_source", "revisions", syllabus_name)

def get_rev_repo_path(syllabus_name, rev):
    return path.join(get_rev_repo_folder(syllabus_name), rev)

# Create directories for the source repositories and the build HTML files
os.makedirs(get_main_repo_path(""), exist_ok = True)
os.makedirs(get_rev_repo_folder(""), exist_ok = True)
os.makedirs("_build", exist_ok = True)

# Read the syllabi.yml file into a Python dictionary
with open("syllabi.yml", mode = "r") as syllabi_file:
    syllabi = yaml.safe_load(syllabi_file)

# Read the base configuration file into a Python dictionary
with open("_config_base.yml", mode = "r") as config_base_file:
    config_base = yaml.safe_load(config_base_file)

# Clean up existing repositories that are no longer in the syllabi.yml file
for existing_syllabus in os.listdir(get_main_repo_path("")):
    if existing_syllabus not in syllabi["syllabi"]:
        print(f"[{existing_syllabus}] Removing discarded syllabus repository")
        shutil.rmtree(get_main_repo_path(existing_syllabus))

for existing_syllabus in os.listdir(get_rev_repo_folder("")):
    if existing_syllabus not in syllabi["syllabi"]:
        print(f"[{existing_syllabus}] Removing discarded syllabus revisions")
        shutil.rmtree(get_rev_repo_folder(existing_syllabus))
    else:
        for existing_revision in os.listdir(get_rev_repo_folder(existing_syllabus)):
            if existing_revision not in syllabi["syllabi"][existing_syllabus]["revisions"]:
                print(f"[{existing_syllabus}/{existing_revision}] Removing discarded revision")
                shutil.rmtree(get_rev_repo_path(existing_syllabus, existing_revision))

for syllabus, syllabus_info in syllabi["syllabi"].items():
    # Clone the repository into the _source directory as a bare repository
    main_repo_path = get_main_repo_path(syllabus)
    if path.isdir(main_repo_path):
        print(f"[{syllabus}] Opening existing repository")
        main_repo = Repo(main_repo_path)
        print(f"[{syllabus}] Fetching updates")
        main_repo_fetch_results = main_repo.remotes.origin.fetch("*:*")
        for fetch_info in main_repo_fetch_results:
            print(f"[{syllabus}] Fetched {fetch_info.name}")
    else:
        print(f"[{syllabus}] Cloning repository")
        main_repo = Repo.clone_from(syllabus_info["repo"], main_repo_path, multi_options = [ "--bare" ])

    # Create a directory for clones at each revision (branch or tag)
    os.makedirs(get_rev_repo_folder(syllabus), exist_ok = True)

    # Then for each revision, create a local clone which is checked out at that
    # branch or tag. Git objects are shared from the bare repository to safe
    # disk space.
    for rev, rev_info in syllabus_info["revisions"].items():
        rev_alias = rev_info["alias"] if rev_info is not None and "alias" in rev_info else rev
        rev_repo_path = get_rev_repo_path(syllabus, rev_alias)
        rev_jb_path = path.normpath(
            path.join(
                rev_repo_path, 
                rev_info["jb_path"] if rev_info is not None and "jb_path" in rev_info else "syllabus"
            )
        )

        if path.isdir(rev_repo_path):
            print(f"[{syllabus}/{rev_alias}] Opening existing repository")
            rev_repo = Repo(rev_repo_path)
            print(f"[{syllabus}/{rev_alias}] Pulling updates")
            rev_repo_pull_results = rev_repo.remotes.origin.pull(f"{rev}:{rev}")
            for pull_info in rev_repo_pull_results:
                print(f"[{syllabus}/{rev_alias}] Pulled {pull_info.name}")
        else:
            print(f"[{syllabus}/{rev_alias}] Cloning repository")
            rev_repo = main_repo.clone(path.abspath(rev_repo_path), multi_options = [ "--local", "--shared", "--no-checkout" ])
        print(f"[{syllabus}/{rev_alias}] Checking out revision {rev}")
        rev_repo.git.checkout(rev)

        authors = { 
            commit.author.name 
            for commit in rev_repo.iter_commits(rev_repo.head) 
            if commit.author.name is not None 
        }

        copyright_year = rev_repo.commit(rev_repo.head).authored_datetime.year

        with open(path.join(rev_jb_path, "_config.yml"), mode = "r") as ref_config_file:
            ref_config = yaml.safe_load(ref_config_file)
        
        new_ref_config = merge({}, config_base, ref_config)

        new_ref_config["author"] = ", ".join(authors)
        new_ref_config["copyright"] = copyright_year

        new_ref_config["html"]["baseurl"] = f"/{syllabus}/{rev_alias}"

        new_ref_config["repository"]["url"] = syllabus_info["repo"]
        new_ref_config["repository"]["branch"] = rev
        
        with open(path.join(rev_jb_path, "_config_ext.yml"), mode = "w") as ref_config_ext_file:
            yaml.dump(new_ref_config, ref_config_ext_file)

        print(f"[{syllabus}/{rev_alias}] Starting Jupyter Book build")
        jb_result = subprocess.run([ "jupyter-book", "build", "--config", path.join(rev_jb_path, "_config_ext.yml"), rev_jb_path ], timeout = 2 * 60)
        if jb_result.returncode != 0:
            print(f"[{syllabus}/{rev_alias}] Jupyter Book build failed", file = sys.stderr)
        else:
            print(f"[{syllabus}/{rev_alias}] Jupyter Book build succeeded, copying HTML files")
            shutil.rmtree(path.join("_build", syllabus, rev_alias), ignore_errors = True)
            shutil.copytree(path.join(rev_jb_path, "_build", "html"), path.join("_build", syllabus, rev_alias))

        os.remove(path.join(rev_jb_path, "_config_ext.yml"))
