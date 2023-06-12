import os
import argparse
import subprocess
import configparser
import re
import time
import sys
import pyautogui
import pytesseract

GITH_CONFIG_FILE = os.path.expanduser("~/.githconfig")

def clean_path(path):
    path = path.replace('"', '')
    path = path.replace("'", '')

    return path

def get_current_profile():
    config = read_gith_config()
    if config.has_option("default", "current_profile"):
        return config.get("default", "current_profile")
    return "default"

def set_current_profile(profile_name):
    config = read_gith_config()
    config.set("default", "current_profile", profile_name)
    with open(GITH_CONFIG_FILE, "w") as config_file:
        config.write(config_file)

def delete_profile(profile_name):
    config = read_gith_config()

    if not config.has_section(profile_name):
        print(f"Profile '{profile_name}' does not exist.")
        return

    config.remove_section(profile_name)

    with open(GITH_CONFIG_FILE, "w") as config_file:
        config.write(config_file)
    
    if get_current_profile() == profile_name:
        set_current_profile("default")

    print(f"Deleted profile: '{profile_name}'")

def get_repo_path():
    config = read_gith_config()
    current_profile = get_current_profile()

    if config.has_option(current_profile, "repo_path"):
        return clean_path(config.get(current_profile, "repo_path"))

    return None

def set_repo_path(repo_path):
    config = read_gith_config()
    current_profile = get_current_profile()

    if not config.has_section(current_profile):
        config.add_section(current_profile)

    # Remove existing repo_path line if present
    if config.has_option(current_profile, "repo_path"):
        config.remove_option(current_profile, "repo_path")

    repo_path = clean_path(repo_path)
    config.set(current_profile, "repo_path", str(repo_path))

    # Write the updated config
    with open(GITH_CONFIG_FILE, "w") as config_file:
        config.write(config_file)

def get_branch_name():
    config = read_gith_config()
    current_profile = get_current_profile()

    if config.has_option(current_profile, "branch_name"):
        return config.get(current_profile, "branch_name")

    return "main"

def set_branch_name(branch_name):
    config = read_gith_config()
    current_profile = get_current_profile()

    if not config.has_section(current_profile):
        config.add_section(current_profile)

    # Remove existing branch_name line if present
    if config.has_option(current_profile, "branch_name"):
        config.remove_option(current_profile, "branch_name")

    config.set(current_profile, "branch_name", str(branch_name))

    # Write the updated config
    with open(GITH_CONFIG_FILE, "w") as config_file:
        config.write(config_file)

def get_remote_name():
    config = read_gith_config()
    current_profile = get_current_profile()

    if config.has_option(current_profile, "remote_name"):
        return config.get(current_profile, "remote_name")

    return "origin"

def set_remote_name(remote_name):
    config = read_gith_config()
    current_profile = get_current_profile()

    if not config.has_section(current_profile):
        config.add_section(current_profile)

    # Remove existing branch_name line if present
    if config.has_option(current_profile, "remote_name"):
        config.remove_option(current_profile, "remote_name")

    config.set(current_profile, "remote_name", str(remote_name))

    # Write the updated config
    with open(GITH_CONFIG_FILE, "w") as config_file:
        config.write(config_file)
def find_sln_file(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.sln'):
                return os.path.join(root, file)
    return None

def ocr_text(region):
    # Take a screenshot of the specified region
    screenshot = pyautogui.screenshot(region=region)

    # Perform OCR on the screenshot
    text = pytesseract.image_to_string(screenshot)

    return text.strip()


def vs_has_distributed_option(search_region):
    # Specify the text to search for
    target_text = "Distributed"
    
    # Perform OCR on the specified region
    extracted_text = ocr_text(search_region)
    
    # Check if the target text is present in the extracted text
    if target_text.lower() in extracted_text.lower():
        return True
    else:
        return False


def open_visual_studio_distributed_build():
    build_dir = os.path.join(get_repo_path(), 'build')
    sln_file = find_sln_file(build_dir)

    if sln_file:
        # Open the solution file in Visual Studio
        os.startfile(sln_file)

        # Wait for Visual Studio to open and the solution to load
        time.sleep(20)

        screenWidth, screenHeight = pyautogui.size()
        distributedSearchRegion = (0, 0, screenWidth, screenHeight)

        pyautogui.moveTo(screenWidth*0.5, screenHeight*.9)

        # Send keyboard shortcuts to select release configuration
        pyautogui.hotkey('alt')
        time.sleep(1)
        pyautogui.hotkey('b')
        time.sleep(1)

        hasDistributedOption = vs_has_distributed_option(distributedSearchRegion)

        pyautogui.press("up")
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(1)
        pyautogui.press("down")
        time.sleep(1)
        pyautogui.press("down")
        time.sleep(1)
        pyautogui.press("escape")
        time.sleep(1)
        pyautogui.press("escape")
        time.sleep(1)
        pyautogui.press("escape")
        time.sleep(1)

        # Send keyboard shortcuts to start distributed build
        pyautogui.hotkey('alt')
        time.sleep(1)
        pyautogui.hotkey('b')
        time.sleep(1)

        if hasDistributedOption:
            pyautogui.press("down")
            time.sleep(1)
            pyautogui.press("down")
            time.sleep(1)
            pyautogui.press("down")
            time.sleep(1)

        pyautogui.press("enter")
        time.sleep(1)

        print("Visual Studio build opened and distributed build configuration selected.")
    else:
        print("Error: No .sln file found in the build directory.")

def run_command(command, timeout=30, max_retries=5):
    retries = 0

    while retries <= max_retries:
        output = ""
        process = subprocess.Popen(command, stderr=subprocess.PIPE)
        start_time = time.time()
        out = ""

        while time.time() - start_time < timeout and (process.poll() is None or out != b''):
            out = process.stderr.read(1)
            if out == b'' and process.poll() != None:
                break
            if out != '':
                output += out.decode()
                sys.stdout.write(out.decode())
                sys.stdout.flush()

        if time.time() - start_time >= timeout:
            if (retries + 1) < max_retries:
                retries += 1
                print(f"Command timed out. (Attempt {retries}) Retrying...")
                continue
            else:
                break
        
        return output
            
    print(f"Command failed after {max_retries} retries.")
    return "!*FAILURE!*"

def get_git_command(args):
    repo_path = get_repo_path()
    return ["git", "-C", repo_path] + args

def run_git_command(args, timeout=80, max_retries=5, printOutput=True):
    git_command = get_git_command(args)
    
    output = run_command(git_command, timeout, max_retries)
    if (output == "!*FAILURE!*"):
        return False
    
    if "CONFLICT" in output:
        return False

    return True

def get_current_branch_name():
    repo_path = get_repo_path()
    if not repo_path:
        return None

    try:
        git_command = ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"]
        result = subprocess.run(git_command, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    
    return None

def clean_submodules():
    # Get the list of submodules
    result = subprocess.run(['git', 'submodule', '--quiet', 'foreach', 'echo $path'], capture_output=True, text=True)
    submodule_paths = result.stdout.strip().split('\n')

    # Clean each submodule
    for path in submodule_paths:
        submodule_dir = path.strip()
        if os.path.exists(submodule_dir):
            subprocess.run(['git', 'clean', '-ffdx'], cwd=submodule_dir)
            subprocess.run(['git', 'restore', '--staged', '.'], cwd=submodule_dir)
            subprocess.run(['git', 'checkout', '.'], cwd=submodule_dir)

def clean_non_git_files():
    clean_command = get_git_command(["clean", "-ffdx"])

    process = subprocess.Popen(clean_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)

    # Read the stdout and stderr streams line by line
    stdout, stderr = process.communicate()
    for line in stdout.splitlines():
        print(line)
        # Check if the prompt "Would you like to try again (y/n)" is present
        if "(y/n)" in line:
            # Automatically send "n" as the response
            process.stdin.write("n\n")
            process.stdin.flush()
    
    # Wait for the process to finish
    process.wait()

    clean_submodules()

def commit_command(message):
    run_git_command(["add", "."])
    run_git_command(["commit", "-m", clean_path(message)])

def push_command(force):
    remote_name = get_remote_name()
    branch_name = get_current_branch_name()

    if force:
        run_git_command(["push", remote_name, branch_name, "-f"])
    else:
        run_git_command(["push", remote_name, branch_name])

def fetch_command(rebase=False):
    main_branch = get_branch_name()
    fetch_branch = get_current_branch_name()
    remote_name = get_remote_name()
    passed = False

    print(f"Checking out main branch: {main_branch}")
    passed = run_git_command(["checkout", main_branch])
    if not passed:
        return

    print(f"\nRunning 'git remote prune {remote_name}'")
    run_git_command(["remote", "prune", remote_name], 35, 1)

    print(f"\nFetching latest changes for branch: {main_branch}")
    run_git_command(["fetch", remote_name, main_branch], 20)
    passed = run_git_command(["fetch", remote_name, main_branch])
    if not passed:
        return

    print(f"\nResetting branch: {main_branch} to {remote_name}/{main_branch}")
    passed = run_git_command(["reset", "--hard", f"{remote_name}/{main_branch}"])
    if not passed:
        return

    print(f"\nChecking out the fetch branch: {fetch_branch}")
    passed = run_git_command(["checkout", fetch_branch])

    if rebase:
        print(f"\nRebasing branch to {main_branch}")
        passed = run_git_command(["rebase", main_branch])
    else:
        print(f"\nMerging {main_branch} into {fetch_branch}")
        passed = run_git_command(["merge", main_branch])

    if not passed:
        print("Could not rebase branch, there were conflicts")
        return

    print("\nInitializing and updating submodules")
    run_git_command(["submodule", "update", "--init", "--recursive"])
    passed = run_git_command(["submodule", "update", "--init", "--recursive"])
    if not passed:
        return

    print("\nCleaning non-git files")
    clean_non_git_files()

def fetch_branch_command(fetch_branch):
    remote_name = get_remote_name()
    
    print(f"Fetching fetch branch: {fetch_branch}")
    run_git_command(["fetch", remote_name, fetch_branch], 20)
    passed = run_git_command(["fetch", remote_name, fetch_branch])
    if not passed:
        return
    
    print(f"\nChecking out fetch branch: {fetch_branch}")
    run_git_command(["checkout", fetch_branch])

    print(f"\nResetting fetch branch to remote fetch branch {fetch_branch}")
    run_git_command(["reset", "--hard", f"{remote_name}/{fetch_branch}"])

    print("\nUpdating submodules with `git submodule update --init --recursive")
    run_git_command(["submodule", "update", "--init", "--recursive"])
    passed = run_git_command(["submodule", "update", "--init", "--recursive"])

def branch_command(branch_name):
    main_branch = get_branch_name()
    remote_name = get_remote_name()
    passed = False

    print(f"Checking out main branch: {main_branch}")
    passed = run_git_command(["checkout", main_branch])
    if not passed:
        return

    print(f"\nRunning 'git remote prune {remote_name}'")
    run_git_command(["remote", "prune", remote_name], 35, 1)

    print(f"\nFetching latest changes for branch: {main_branch}")
    run_git_command(["fetch", remote_name, main_branch])
    passed = run_git_command(["fetch", remote_name, main_branch])
    if not passed:
        return

    print(f"\nResetting branch: {main_branch} to {remote_name}/{main_branch}")
    passed = run_git_command(["reset", "--hard", f"{remote_name}/{main_branch}"])
    if not passed:
        return

    print(f"\nCreating and checking out new branch: {branch_name}")
    run_git_command(["branch", "-D", branch_name], 20, 1, False)
    passed = run_git_command(["checkout", "-b", branch_name])
    if not passed:
        return

    print("\nInitializing and updating submodules")
    run_git_command(["submodule", "update", "--init", "--recursive"])
    passed = run_git_command(["submodule", "update", "--init", "--recursive"])
    if not passed:
        return

    print("\nCleaning non-git files")
    clean_non_git_files()

def remove_duplicate_sections(file_path):
    pattern = r"\[.*\]"

    with open(file_path, 'r') as f:
        lines = f.readlines()

    with open(file_path, 'w') as f:
        section_names = set()
        for line in lines:
            if re.match(pattern, line):
                section_name = line.strip()
                if section_name in section_names:
                    continue  # Skip duplicate section
                else:
                    section_names.add(section_name)
            f.write(line)

def read_gith_config():
    config = configparser.ConfigParser()
    if os.path.exists(GITH_CONFIG_FILE):
        remove_duplicate_sections(GITH_CONFIG_FILE)

        try:
            config.read(GITH_CONFIG_FILE)
        except configparser.MissingSectionHeaderError:
            # Handle improperly formatted .githconfig file
            print(f"Invalid .githconfig file. Creating a new one with default section headers.")
            with open(GITH_CONFIG_FILE, "w") as config_file:
               config.write(config_file)
    else:
        # Create the .githconfig file with a default section header
        config.add_section("default")
        with open(GITH_CONFIG_FILE, "w") as config_file:
            config.write(config_file)

    return config

def add_profile(profile_name, copy=False):
    config = read_gith_config()

    if config.has_section(profile_name):
        print(f"Profile '{profile_name}' already exists.")
        return

    config.add_section(profile_name)

    if copy:
        current_profile = get_current_profile()
        if config.has_section(current_profile):
            options = config.options(current_profile)
            for option in options:
                if option.find("current_profile") == -1:
                    value = config.get(current_profile, option)
                    config.set(profile_name, option, value)

    with open(GITH_CONFIG_FILE, "w") as config_file:
        config.write(config_file)

    set_current_profile(profile_name)
    print(f"Added new profile: '{profile_name}'")

def switch_profile(profile_name, delete=False):
    config = read_gith_config()

    if not config.has_section(profile_name):
        print(f"Profile '{profile_name}' does not exist.")
        return

    if delete:
        delete_profile(profile_name)
    else:
        set_current_profile(profile_name)
        print(f"Switched to profile: '{profile_name}'")

def add_shortcut(shortcut_name, shortcut_command):
    config = read_gith_config()
    current_profile = get_current_profile()

    if not config.has_section(current_profile):
        config.add_section(current_profile)

    config.set(current_profile, shortcut_name, shortcut_command)

    with open(GITH_CONFIG_FILE, "w") as config_file:
        config.write(config_file)

    print(f"Added shortcut '{shortcut_name}' to profile '{current_profile}'")

# Function to replace variables in the command
def replace_variables(command):
    count = 0
    while command.find("!*") != -1 and count < 20:
        count += 1
        if command.find("!*repo_path") != -1:
            command = command.replace("!*repo_path", get_repo_path())

    return command

def execute_shortcut(shortcut_name):
    config = read_gith_config()
    current_profile = get_current_profile()

    if not config.has_section(current_profile) or not config.has_option(current_profile, shortcut_name):
        print(f"No shortcut found for '{shortcut_name}' in profile '{current_profile}'")
        return

    shortcut_command = config.get(current_profile, shortcut_name)
    shortcut_command = replace_variables(shortcut_command)
    print(f"\nExecuting shortcut '{shortcut_name}': {shortcut_command}")
    os.system(shortcut_command)

def shortcut_command(shortcut_name, shortcut_command=None):
    if shortcut_command is not None:
        add_shortcut(shortcut_name, shortcut_command)
    else:
        execute_shortcut(shortcut_name)
    
def print_status(all=None):
    repo_path = get_repo_path()
    branch_name = get_branch_name()
    current_profile = get_current_profile()
    remote_name = get_remote_name()

    if not repo_path:
        repo_path = "Not set"

    print(f"Current Profile: {current_profile}")
    print(f"Current Repository: {repo_path}")
    print(f"Main Branch: {branch_name}")
    print(f"Remote Name: {remote_name}")

    if (all == None):
        return

    config = read_gith_config()
    profiles = config.sections()

    print("\nShortcuts in current profile:")
    if config.has_section(current_profile):
        shortcuts = config.items(current_profile)
        for shortcut_name, shortcut_command in shortcuts:
            if shortcut_name not in ["repo_path", "branch_name", "current_profile"]:
                print(f"{shortcut_name}: {shortcut_command}")

    print("\nAll profiles:")
    for profile in profiles:
        print(profile)

def init_arg_parser():
    parser = argparse.ArgumentParser(prog="gith", description="Git Helper")
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    repo_parser = subparsers.add_parser("repo", aliases=["r"], help="Set or update the repository path")
    repo_parser.add_argument("directory", help="Path to the git repository")

    status_parser = subparsers.add_parser("status", aliases=["s"], help="Show the status of the current profile ---- gith status [all]  ---- display all info")
    status_parser.add_argument("all", nargs="?", default=None, help="Print shortcuts and all profiles")

    command_parser = subparsers.add_parser("command", aliases=["c"], help="Run a git command in the repo directory")
    command_parser.add_argument("git_args", nargs=argparse.REMAINDER, help="Git command and arguments")

    subparsers.add_parser("sub-init", aliases=["su"], help="Initialize and update Git submodules recursively")

    subparsers.add_parser("clean", aliases=["cl"], help="Clean non-git files (-ffdx)")

    commit_parser = subparsers.add_parser("commit", aliases=["co"], help="Method which takes a commit message, adds untracked changes and commits ---- gith commit $commit_message")
    commit_parser.add_argument("message", help="Commit message")

    push_parser = subparsers.add_parser("push", aliases=["p"], help="Command to push to main branch ---- gith push [force] ---- force push")
    push_parser.add_argument("force", nargs="?", default=False, help="Force push")

    fetch_parser = subparsers.add_parser("fetch", aliases=["f"], help="Fetch latest main and clean non-git files ---- gith fetch [rebase]  ----  rebase instead of merge")
    fetch_parser.add_argument("rebase", nargs="?", default=False, help="Rebase instead of merge")

    fetch_branch_parser = subparsers.add_parser("fetch-branch", aliases=["fb"], help="Fetch remote branch and checkout that branch, also clean non-git files")
    fetch_branch_parser.add_argument("branch", help="Name of remote branch")

    mainbranch_parser = subparsers.add_parser("main-branch", aliases=["mb"], help="Set the main branch name")
    mainbranch_parser.add_argument("branch", help="Name of the main branch")

    remotename_parser = subparsers.add_parser("remote", aliases=["re"], help="Switch to using a different remote (origin by default)")
    remotename_parser.add_argument("remotename", help="Name of the remote")

    branch_parser = subparsers.add_parser("branch", aliases=["b"], help="Create and switch to a new branch")
    branch_parser.add_argument("name", help="Name of the new branch")

    shortcut_parser = subparsers.add_parser("shortcut", aliases=["sc"], help="Add or execute a shortcut ---- Specify a name and command to save, or just a name to run")
    shortcut_parser.add_argument("shortcut_name", help="Name of the shortcut")
    shortcut_parser.add_argument("shortcut_command", nargs="?", default=None, help="Command associated with the shortcut")

    addprofile_parser = subparsers.add_parser("add-profile", aliases=["ap"], help="Add a new profile ---- gith addprofile [copy]  ----  copy current profile")
    addprofile_parser.add_argument("copy", nargs="?", default=False, help="Copy current profile")
    addprofile_parser.add_argument("name", help="Name of the profile")

    switchprofile_parser = subparsers.add_parser("profile", aliases=["pr"], help="Switch to a different profile ---- gith profile [delete]  ----  delete profile")
    switchprofile_parser.add_argument("delete", nargs="?", default=False, help="Delete a profile")
    switchprofile_parser.add_argument("name", help="Name of the profile")

    subparsers.add_parser("explorer", aliases=["e"], help="Open a file explorer in the repo directory")

    subparsers.add_parser("build", help="Build VS solution in current repo for Release and Distributed, if option is present")

    return parser

def main():
    parser = init_arg_parser()
    args = parser.parse_args()

    if args.command == "repo" or args.command == "r":
        set_repo_path(args.directory)
        print(f"Repository path set to: {args.directory}")
    elif args.command == "status" or args.command == "s":
        print_status(args.all)
    elif args.command == "command" or args.command == "c":
        run_git_command(args.git_args)
    elif args.command == "sub-init" or args.command == "su":
        run_git_command(["submodule", "update", "--init", "--recursive"])
        run_git_command(["submodule", "update", "--init", "--recursive"])
    elif args.command == "clean" or args.command == "cl":
        clean_non_git_files()
    elif args.command == "main-branch" or args.command == "mb":
        set_branch_name(args.branch)
        print(f"Main branch set to: {args.branch}")
    elif args.command == "remote" or args.command == "re":
        set_remote_name(args.remotename)
        print(f"Remote set to: {args.remotename}")
    elif args.command == "commit" or args.command == "co":
        commit_command(args.message)
    elif args.command == "push" or args.command == "p":
        push_command(args.force)
    elif args.command == "fetch" or args.command == "f":
        fetch_command(args.rebase)
    elif args.command == "fetch-branch" or args.command == "fb":
        fetch_branch_command(args.branch)
    elif args.command == "branch" or args.command == "b":
        branch_command(args.name)
    elif args.command == "shortcut" or args.command == "sc":
        shortcut_command(args.shortcut_name, args.shortcut_command)
    elif args.command == "add-profile" or args.command == "ap":
        add_profile(args.name, args.copy)
    elif args.command == "profile" or args.command == "pr":
        switch_profile(args.name, args.delete)
    elif args.command == "explorer" or args.command == "e":
        repo_path = get_repo_path()
        os.system(f"explorer {repo_path}")
    elif args.command == "build":
        open_visual_studio_distributed_build()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
