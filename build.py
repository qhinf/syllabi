import os
import re
import shutil
import subprocess
import sys
import yaml

from git import Commit, Repo
from jinja2 import Environment, FileSystemLoader, select_autoescape
from mergedeep import merge, Strategy
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

def get_commit_authors(commit: Commit):
    if commit.author.name is not None:
        yield commit.author.name
    for coa in commit.co_authors:
        if coa.name is not None:
            yield coa.name

def get_repo_authors(repo: Repo):
    for commit in repo.iter_commits(repo.head):
        for author in get_commit_authors(commit):
            yield author

def get_repo_remote_url(repo: Repo):
    return repo.remote().url \
            .removesuffix(".git") \
            .replace("git@github.com:", "https://github.com/")

# Read the base configuration file into a Python dictionary
with open("_config_base.yml", mode = "r") as config_base_file:
    config_base = yaml.safe_load(config_base_file)

# Build the general content from the /content folder
def build_content(): 
    build_path = "_build/algemeen"
    repo_path = "."
    jb_path = "content"
    jb_build_path = path.join(jb_path, "_build", "html")

    repo = Repo(repo_path)

    with open(path.join(jb_path, "_config.yml"), mode = "r") as config_file:
        config = yaml.safe_load(config_file)

    authors = set(get_repo_authors(repo))

    copyright_year = repo.commit(repo.head).authored_datetime.year

    new_config = merge({}, config_base, config)

    new_config["author"] = "Q-highschool + " + ", ".join(authors)
    new_config["copyright"] = str(copyright_year)

    if not "sphinx" in new_config: new_config["sphinx"] = {}
    if not "config" in new_config["sphinx"]: new_config["sphinx"]["config"] = {}
    if not "html_context" in new_config["sphinx"]["config"]: new_config["sphinx"]["config"]["html_context"] = {}
    new_config["sphinx"]["config"]["html_context"]["book_basepath"] = f"informatie"

    if not "repository" in new_config: new_config["repository"] = {}
    new_config["repository"]["url"] = get_repo_remote_url(repo)
    new_config["repository"]["branch"] = "main"
    new_config["repository"]["path_to_book"] = "content"

    with open(path.join(jb_path, "_config_ext.yml"), mode = "w") as ref_config_ext_file:
        yaml.dump(new_config, ref_config_ext_file)

    print("[content] Starting Jupyter Book build")
    jb_result = subprocess.run([ "jupyter-book", "build", "--config", path.join(jb_path, "_config_ext.yml"), jb_path ], timeout = 2 * 60)
    if jb_result.returncode != 0:
        print("[content] Jupyter Book build failed", file = sys.stderr)
        build_success = False
    else:
        print("[content] Jupyter Book build succeeded")
        build_success = True
    
    os.remove(path.join(jb_path, "_config_ext.yml"))

    if build_success:
        print("[content] Copying HTML")
        shutil.rmtree(build_path, ignore_errors = True)
        shutil.copytree(jb_build_path, build_path)

# Create directory for the HTML build files
if path.exists("_build"):
    shutil.rmtree("_build")
shutil.copytree("static", "_build")

build_content()

modules = []
old_versions = []
build_state_dir = "_build_state"
os.makedirs(build_state_dir, exist_ok=True)

for module in os.listdir(get_repo_path()):
    module_title = module
    versions = []

    version_paths = sorted(os.listdir(get_repo_path(module)))
    latest_version = version_paths[-1] if version_paths else None
    latest_version_state_dir = path.join(build_state_dir, module)
    latest_version_file = path.join(latest_version_state_dir, "latest_version")
    latest_version_prev = None
    force_rebuild = False

    os.makedirs(latest_version_state_dir, exist_ok=True)
    # Check if the latest version has changed since last build
    if path.exists(latest_version_file):
        with open(latest_version_file, mode="r", encoding="utf-8") as f:
            latest_version_prev = f.read().strip()
        if latest_version_prev != latest_version:
            force_rebuild = True
    else:
        force_rebuild = True

    for version in version_paths:
        build_path = path.join("_build", module, version)
        repo_path = get_repo_path(module, version)
        jb_path = path.join(repo_path, "syllabus")
        jb_build_path = path.join(jb_path, "_build", "html")
        jb_build_version = path.join(jb_build_path, "version")
        slides_path = path.join(repo_path, "slides")
        slides_dist_path = path.join(slides_path, "dist")
        jb_build_slides_path = path.join(jb_build_path, "slides")

        repo = Repo(repo_path)
        
        with open(path.join(jb_path, "_config.yml"), mode = "r") as ref_config_file:
            ref_config = yaml.safe_load(ref_config_file)

        if (match := year_block_pattern.match(version)) is not None:
            version_title = f"{match.group(1)}/{match.group(2)} - Blok {match.group(3)}"
        else:
            version_title = version

        needs_build = True
        # Skip this build if the built version is the same as the current repo
        # head commit SHA, unless a newer version was added
        if path.exists(jb_build_version) and not force_rebuild:
            with open(jb_build_version, mode = "r", encoding = "utf-8") as version_file:
                if version_file.read().strip() == repo.head.commit.hexsha:
                    print(f"[{module}/{version}] Skipping build: already up to date", file = sys.stderr)
                    needs_build = False
            
        if needs_build:
            authors = set(get_repo_authors(repo))

            copyright_year = repo.commit(repo.head).authored_datetime.year

            new_ref_config = merge({}, config_base, ref_config, strategy = Strategy.TYPESAFE_ADDITIVE)

            new_ref_config["author"] = "Q-highschool + " + ", ".join(authors)
            new_ref_config["copyright"] = str(copyright_year)

            if not "sphinx" in new_ref_config: new_ref_config["sphinx"] = {}
            if not "config" in new_ref_config["sphinx"]: new_ref_config["sphinx"]["config"] = {}
            if not "myst_substitutions" in new_ref_config["sphinx"]["config"]: new_ref_config["sphinx"]["config"]["myst_substitutions"] = {}
            new_ref_config["sphinx"]["config"]["myst_substitutions"]["versie"] = version_title
            if version != version_paths[-1]:
                if not "html_theme_options" in new_ref_config["sphinx"]["config"]: new_ref_config["sphinx"]["config"]["html_theme_options"] = {}
                new_ref_config["sphinx"]["config"]["html_theme_options"]["announcement"] = \
                    f"Let op: dit is een oude versie van deze syllabus voor {version_title}."
            if not "html_context" in new_ref_config["sphinx"]["config"]: new_ref_config["sphinx"]["config"]["html_context"] = {}
            new_ref_config["sphinx"]["config"]["html_context"]["book_basepath"] = f"{module}/{version}"

            if not "repository" in new_ref_config: new_ref_config["repository"] = {}
            new_ref_config["repository"]["url"] = get_repo_remote_url(repo)
            new_ref_config["repository"]["branch"] = version
            new_ref_config["repository"]["path_to_book"] = "syllabus"

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

            # Build slides if present
            if path.exists(slides_path):
                print(f"[{module}/{version}] Installing slides dependencies")
                slides_install_result = subprocess.run(
                    ["pnpm", "install"],
                    cwd=slides_path,
                    timeout=2 * 60
                )
                if slides_install_result.returncode != 0:
                    print(f"[{module}/{version}] Slides install failed", file=sys.stderr)
                else:
                    print(f"[{module}/{version}] Building slides")
                    slides_result = subprocess.run(
                        ["pnpm", "build"],
                        cwd=slides_path,
                        timeout=2 * 60
                    )
                    if slides_result.returncode != 0:
                        print(f"[{module}/{version}] Slides build failed", file=sys.stderr)
                    elif path.exists(slides_dist_path):
                        print(f"[{module}/{version}] Copying slides")
                        shutil.rmtree(jb_build_slides_path, ignore_errors=True)
                        shutil.copytree(slides_dist_path, jb_build_slides_path)

            os.remove(path.join(jb_path, "_config_ext.yml"))

        if not needs_build or build_success:
            module_title = ref_config["title"]
            module_color = ref_config["accent_color"] if "accent_color" in ref_config else None
            module_logo = \
                path.join(module, version, "_static", path.basename(ref_config["logo"])) \
                if "logo" in ref_config \
                else None
            module_banner = None
            if "banner" in ref_config:
                banner_path = path.join("_images", path.basename(ref_config["banner"]))
                module_banner = path.join(module, version, banner_path)
                if not path.exists(path.join(jb_build_path, banner_path)):
                    banner_build_path = path.join(jb_build_path, banner_path)
                    os.makedirs(path.dirname(banner_build_path), exist_ok = True)
                    shutil.copyfile(path.join(jb_path, ref_config["banner"]), banner_build_path)
            versions.append({ "slug": version, "title": version_title })
            if version != version_paths[-1]:
                old_versions.append(f"/{module}/{version}/")

            print(f"[{module}/{version}] Copying HTML")
            shutil.rmtree(build_path, ignore_errors = True)
            shutil.copytree(jb_build_path, build_path)

    # After building all versions, update the latest_version file (outside _build)
    with open(latest_version_file, mode="w", encoding="utf-8") as f:
        f.write(latest_version if latest_version else "")

    versions.sort(key = lambda version: version["slug"], reverse = True)
    modules.append({ 
        "slug": module,
        "title": module_title,
        "color": module_color,
        "logo": module_logo,
        "banner": module_banner,
        "versions": versions
    })

modules.sort(key = lambda module: module["title"])

jinja_env = Environment(loader = FileSystemLoader("templates"), autoescape = select_autoescape())

# Create the index page
index_template = jinja_env.get_template("index.html")
print(f"[index] Writing index.html")
with open(path.join("_build", "index.html"), mode = "w") as index_file:
    index_file.write(index_template.render(modules = modules))

# Create a robots.txt file to disallow crawling of old versions
print(f"[index] Writing robots.txt")
with open(path.join("_build", "robots.txt"), mode = "w") as robots_file:
    robots_file.write("User-agent: *\n")
    for old_module_version in old_versions:
        robots_file.write(f"Disallow: {old_module_version}\n")

# Create a module index for each module
module_index_template = jinja_env.get_template("module_index.html")
for module in modules:
    print(f"[{module['slug']}] Writing index.html")
    with open(path.join("_build", module["slug"], "index.html"), mode = "w") as module_index_file:
        module_index_file.write(module_index_template.render(module = module))

# Configure redirects for old paths
redirects = [
    { "original": "/informatie/code-stelen-van-het-internet-of-leerling", "to": "/algemeen/informatie/code-stelen.html" },
    { "original": "/informatie/meerdere-bestanden-inleveren", "to": "/algemeen/informatie/meerdere-bestanden-inleveren.html" },
    { "original": "/modules/python", "to": "/basis_programmeren" },
    { "original": "/modules/basis-van-computing-science", "to": "/basis_cs" },
    { "original": "/modules/webdesign", "to": "/webdesign" },
    { "original": "/modules/processing", "to": "/processing" },
    { "original": "/modules/databases-and-sql", "to": "/databases" },
    # TODO { "original": "/modules/databases-and-sql/sql-inleveropdracht", "to": "/" },
    { "original": "/modules/security", "to": "/security" },
    { "original": "/modules/artificiele-intelligentie", "to": "/ai" },
    { "original": "/modules/linux-and-servers", "to": "/linux_servers" },
    #TODO { "original": "/modules/linux-and-servers/handleiding-ssh", "to": "/" },
    { "original": "/modules/javascript", "to": "/javascript" },
    { "original": "/modules/project", "to": "/project" },
    { "original": "/modules/pythonplus", "to": "/pythonplus" },
    { "original": "/modules/computer_arch", "to": "/computer_arch" },
]

redirect_template = jinja_env.get_template("redirect.html")
for redirect in redirects:
    print(f"[redirects] Writing redirect for {redirect['original']}")
    
    dest_folder = path.join("_build", redirect["original"].strip("/"))
    # Add the appropriate number of .. based on the original location, so that
    # this also works when hosted under eg. qhinf.github.io/syllabi (so it
    # doesn't redirect to qhinf.github.io/basis_cs but to
    # qhinf.github.io/syllabi/basis_cs)
    redirect_url = "/".join(len(redirect["original"].strip("/").split("/")) * [ ".." ]) + redirect["to"]

    os.makedirs(dest_folder, exist_ok = True)
    with open(path.join(dest_folder, "index.html"), mode = "w") as redirect_index_file:
        redirect_index_file.write(redirect_template.render(redirect_url = redirect_url))
