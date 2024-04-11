import os
import argparse
import subprocess
import configparser
import re
from typing import IO, NoReturn

GITH_CONFIG_FILE = os.path.expanduser("~/.githconfig")
SHORTCUT_PREFIX = "^#short"

# ======= Custom Classes =======
class CustomArgumentParser(argparse.ArgumentParser):
    def print_usage(self, file: IO[str] | None = None) -> None:
        pass

    def error(self, message: str) -> NoReturn:
        pass

    def format_help(self) -> str:
        formatter = self._get_formatter()

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            if action_group.title == "Commands":
                formatter.start_section(action_group.title)
                formatter.add_text(action_group.description)
                formatter.add_arguments(action_group._group_actions)
                formatter.end_section()


        # determine help from format above
        return formatter.format_help()
# ------- End Custom Classes -------

# ======= Configuration File Functions =======
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
# ------- End Configuration File Functions -------

# ======= Helpers =======
def run_git_command(args, timeout=50, max_retries=3):
    args = ["git"] + args
    output = run_command(args, timeout, max_retries)
    if (output == "^#FAILURE^#"):
        return False
    
    if "CONFLICT" in output:
        print("Error: a conflict occured during git command execution, please resolve before proceeding")
        return False

    return True

def run_command(command, max_time=50, max_retries=3):
    retries = 0

    while retries <= max_retries:
        output = ""

        try:
            subprocess.run(command, cwd=get_repo_path(), universal_newlines=True, timeout=max_time)
        except subprocess.TimeoutExpired:
            if (retries + 1) < max_retries:
                retries += 1
                print(f"\n\nCommand timed out. (Attempt {retries}) Retrying...")
                continue
            else:
                break
        
        return output
            
    print(f"Command failed after {max_retries} retries.")
    return "^#FAILURE^#"

def get_git_command(args):
    repo_path = get_repo_path()
    return ["git", "-C", repo_path] + args

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

def get_status_files():
    # Logic to only add non-submodule changes
    repo_path = get_repo_path()
    status_command = ["git", "status"]

    status_files = subprocess.Popen(status_command, cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    status_files, stderr = status_files.communicate()
    if status_files is not None:
        status_files = status_files.decode()
        status_files = status_files.replace("modified:", "")
        status_files = status_files.split('\n')

        return_files = []
        for file in status_files:
            file = file.lstrip()
            file_path = os.path.join(get_repo_path(), file)

            if os.path.isfile(file_path):
                return_files.append(file_path)

        return return_files
    
    return []

def add_without_submodules():
    status_files = get_status_files()

    for file in status_files:
        run_git_command(["add", file])

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

# Function to replace variables in the shortcut command
def replace_variables(command):
    count = 0
    while command.find("^#") != -1 and count < 20:
        count += 1
        if command.find("^#repo_path") != -1:
            command = command.replace("^#repo_path", get_repo_path())

    return command
# ------- End Helpers -------

# ======= Commands =======
def submodule_command():
    run_git_command(["submodule", "sync"])
    run_git_command(["submodule", "update", "--init", "--recursive"], 550, 0)
    return run_git_command(["submodule", "update", "--init", "--recursive"], 20, 1)

def commit_command(message):
    add_without_submodules()
            
    run_git_command(["commit", "-m", clean_path(message)])

def push_command(force):
    remote_name = get_remote_name()
    branch_name = get_current_branch_name()

    if force:
        run_git_command(["push", remote_name, branch_name, "-f"])
    else:
        run_git_command(["push", remote_name, branch_name])

def fetch_command(rebase):
    main_branch = get_branch_name()
    fetch_branch = get_current_branch_name()
    remote_name = get_remote_name()
    passed = False

    status_file_count = len(get_status_files())

    if status_file_count > 0:
        print("Stashing local changes")
        add_without_submodules()
        run_git_command(["stash"])

    print(f"\nChecking out main branch: {main_branch}")
    passed = run_git_command(["checkout", main_branch])
    if not passed:
        print(f"Error: unable to checkout branch '{main_branch}'")
        return

    print(f"\nRunning 'git remote prune {remote_name}'")
    run_git_command(["remote", "prune", remote_name], 35, 1)

    print(f"\nFetching latest changes for branch: {main_branch}")
    run_git_command(["fetch", remote_name, main_branch], 550, 0)
    passed = run_git_command(["fetch", remote_name, main_branch], 50, 0)
    if not passed:
        print(f"Error: Unable to fetch branch '{main_branch}' at remote '{remote_name}'")
        return

    print(f"\nResetting branch: {main_branch} to {remote_name}/{main_branch}")
    passed = run_git_command(["reset", "--hard", f"{remote_name}/{main_branch}"])
    if not passed:
        print("Error: Unable to reset branch")
        return

    print(f"\nChecking out the fetch branch: {fetch_branch}")
    passed = run_git_command(["checkout", fetch_branch])

    if rebase:
        print(f"\nRebasing branch to {main_branch}")
        passed = run_git_command(["rebase", main_branch], 300, 0)
    else:
        print(f"\nMerging {main_branch} into {fetch_branch}")
        passed = run_git_command(["merge", main_branch], 300, 0)
    
    if status_file_count > 0:
        print("\nAuto merging stashed changes")
        passed = run_git_command(["stash", "pop"])

        if not passed:
            print("Could not auto merge stashed changes, aborting fetch")
            print("Error: Unable to auto merge stashed changes")
            return

    print("\nInitializing and updating submodules")
    passed = submodule_command()
    if not passed:
        print("Error: Unable to update submodules")
        return

    print("\nCleaning non-git files")
    clean_non_git_files()

def fetch_branch_command(fetch_branch):
    remote_name = get_remote_name()
    
    print(f"Fetching fetch branch: {fetch_branch}")
    run_git_command(["fetch", remote_name, fetch_branch], 550, 0)
    passed = run_git_command(["fetch", remote_name, fetch_branch], 50, 0)
    if not passed:
        print(f"Error: unable to fetch branch '{fetch_branch}'")
        return
    
    print(f"\nChecking out fetch branch: {fetch_branch}")
    run_git_command(["checkout", fetch_branch])

    print(f"\nResetting fetch branch to remote fetch branch {fetch_branch}")
    run_git_command(["reset", "--hard", f"{remote_name}/{fetch_branch}"])

    print("\nUpdating submodules with `git submodule update --init --recursive")
    passed = submodule_command()

    print("\nCleaning non-git files")
    clean_non_git_files()

def branch_command(branch_name):
    main_branch = get_branch_name()
    remote_name = get_remote_name()
    passed = False

    print(f"Checking out main branch: {main_branch}")
    passed = run_git_command(["checkout", main_branch])
    if not passed:
        print(f"Error: unable to checkout branch '{main_branch}'")
        return

    print(f"\nRunning 'git remote prune {remote_name}'")
    run_git_command(["remote", "prune", remote_name], 35, 1)

    print(f"\nFetching latest changes for branch: {main_branch}")
    run_git_command(["fetch", remote_name, main_branch], 550, 0)
    passed = run_git_command(["fetch", remote_name, main_branch], 50, 0)
    if not passed:
        print(f"Error: Unable to fetch branch '{main_branch}' at remote '{remote_name}'")
        return

    print(f"\nResetting branch: {main_branch} to {remote_name}/{main_branch}")
    passed = run_git_command(["reset", "--hard", f"{remote_name}/{main_branch}"])
    if not passed:
        print("Error: Unable to reset branch")
        return

    print(f"\nCreating and checking out new branch: {branch_name}")
    run_git_command(["branch", "-D", branch_name], 20, 1)
    passed = run_git_command(["checkout", "-b", branch_name])
    if not passed:
        print("Error: unable to create new branch")
        return

    print("\nInitializing and updating submodules")
    passed = submodule_command()
    if not passed:
        print("Error: failed to update submodules")
        return

    print("\nCleaning non-git files")
    clean_non_git_files()

def add_profile_command(profile_name, copy):
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

def switch_profile_command(profile_name, delete=False):
    config = read_gith_config()

    if not config.has_section(profile_name):
        print(f"Profile '{profile_name}' does not exist.")
        return

    if delete:
        delete_profile(profile_name)
    else:
        set_current_profile(profile_name)
        print(f"Switched to profile: '{profile_name}'")

def add_shortcut_command(shortcut_name, shortcut_command, current=False):
    config = read_gith_config()
    current_profile = "default"

    if current:
        current_profile = get_current_profile()

        if current_profile == "default":
            print("Error: Cannot create a profile specific shortcut when using the default profile, run the `add-profile` command then try again")
            return

    if not config.has_section(current_profile):
        config.add_section(current_profile)

    full_shortcut_name = SHORTCUT_PREFIX + shortcut_name

    config.set(current_profile, full_shortcut_name, shortcut_command)

    with open(GITH_CONFIG_FILE, "w") as config_file:
        config.write(config_file)

    print(f"Added shortcut '{shortcut_name}' to profile '{current_profile}'")

def remove_shortcut_command(shortcut_name, current=False):
    config = read_gith_config()
    current_profile = "default"

    if current:
        current_profile = get_current_profile()

        if current_profile == "default":
            print("\nError: Cannot delete a profile specific shortcut when using the default profile")
            return
        
    full_shortcut_name = SHORTCUT_PREFIX + shortcut_name
    
    if not config.has_section(current_profile) or not config.has_option(current_profile, full_shortcut_name):
        print(f"\nError: No shortcut found for '{shortcut_name}' in profile '{current_profile}'")
        return
    
    config.remove_option(current_profile, full_shortcut_name)

    with open(GITH_CONFIG_FILE, "w") as config_file:
        config.write(config_file)

    print(f"\nRemoved shortcut {shortcut_name} from profile {current_profile}")

def execute_shortcut_command(shortcut_name, printError=True):
    config = read_gith_config()
    current_profile = get_current_profile()
    full_shortcut_name = SHORTCUT_PREFIX + shortcut_name

    if not config.has_section(current_profile) or not config.has_option(current_profile, full_shortcut_name):
        current_profile = "default"
        if not config.has_section(current_profile) or not config.has_option(current_profile, full_shortcut_name):
            if printError:
                print(f"\nError: No shortcut found for '{shortcut_name}' in profile '{current_profile}'")
            return False

    shortcut_command = config.get(current_profile, full_shortcut_name)
    shortcut_command = shortcut_command.replace(SHORTCUT_PREFIX, "")
    shortcut_command = replace_variables(shortcut_command)
    print(f"\nExecuting shortcut '{shortcut_name}': {shortcut_command}")
    os.system(shortcut_command)

    return True
    
def print_status_command(all):
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

    if (all == False):
        return

    config = read_gith_config()
    profiles = config.sections()

    if config.has_section("default"):
        print("\nGlobal Shortcuts:")
        config_items = config.items("default")
        for item_name, value in config_items:
            if SHORTCUT_PREFIX in item_name:
                shortcut_name = item_name.replace(SHORTCUT_PREFIX, "")
                print(f"{shortcut_name}: {value}")


    if config.has_section(current_profile) and current_profile != "default":
        print("\nShortcuts in current profile:")
        config_items = config.items(current_profile)
        for item_name, value in config_items:
            if SHORTCUT_PREFIX in item_name:
                shortcut_name = item_name.replace(SHORTCUT_PREFIX, "")
                print(f"{shortcut_name}: {value}")

    print("\nAll profiles:")
    for profile in profiles:
        print(profile)
# ------- End Commands -------

# ======= Main Logic and Argument Parsing =======
def init_arg_parser():
    parser = CustomArgumentParser(prog="gith", description="Git Helper")
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    repo_parser = subparsers.add_parser("repo", aliases=["r"], help="Set or update the repository path")
    repo_parser.add_argument("directory", nargs="?", default=os.getcwd(), help="Path to the git repository")

    status_parser = subparsers.add_parser("status", aliases=["s"], help="Show the status of the current profile ---- gith status [all]  ---- display all info")
    status_parser.add_argument("all", nargs="?", default="", help="Print shortcuts and all profiles")

    command_parser = subparsers.add_parser("command", aliases=["c"], help="Run a shell command in the repo directory")
    command_parser.add_argument("command_args", nargs=argparse.REMAINDER, help="Command and arguments")

    subparsers.add_parser("sub-init", aliases=["su"], help="Initialize and update Git submodules recursively")

    subparsers.add_parser("clean", aliases=["cl"], help="Clean non-git files (-ffdx)")

    commit_parser = subparsers.add_parser("commit", aliases=["co"], help="Method which takes a commit message, adds untracked changes and commits ---- gith commit $commit_message")
    commit_parser.add_argument("message", help="Commit message")

    push_parser = subparsers.add_parser("push", aliases=["p"], help="Command to push to main branch ---- gith push [force] ---- force push")
    push_parser.add_argument("force", nargs="?", default="", help="Force push")

    fetch_parser = subparsers.add_parser("fetch", aliases=["f"], help="Fetch latest main and clean non-git files ---- gith fetch [rebase]  ----  rebase instead of merge")
    fetch_parser.add_argument("rebase", nargs="?", default="", help="Rebase instead of merge")

    fetch_branch_parser = subparsers.add_parser("fetch-branch", aliases=["fb"], help="Fetch remote branch and checkout that branch, also clean non-git files")
    fetch_branch_parser.add_argument("branch", help="Name of remote branch")

    mainbranch_parser = subparsers.add_parser("main-branch", aliases=["mb"], help="Set the main branch name")
    mainbranch_parser.add_argument("branch", help="Name of the main branch")

    remotename_parser = subparsers.add_parser("remote", aliases=["re"], help="Switch to using a different remote (origin by default)")
    remotename_parser.add_argument("remotename", help="Name of the remote")

    branch_parser = subparsers.add_parser("branch", aliases=["b"], help="Create and switch to a new branch")
    branch_parser.add_argument("name", help="Name of the new branch")

    shortcut_parser = subparsers.add_parser("add-shortcut", aliases=["asc"], help="Add a new shortcut ---- Specify a name as well as a command for the shortcut")
    shortcut_parser.add_argument("shortcut_name", help="Name of the shortcut")
    shortcut_parser.add_argument("shortcut_command", help="Command associated with the shortcut")
    shortcut_parser.add_argument("current", nargs="?", default="", help="Option to specify if the shortcut is profile specific")

    shortcut_parser = subparsers.add_parser("remove-shortcut", aliases=["rsc"], help="Remove a shortcut ---- Specify the name of an existing shortcut to remove it")
    shortcut_parser.add_argument("shortcut_name", help="Name of the shortcut")
    shortcut_parser.add_argument("current", nargs="?", default="", help="Option to specify if the shortcut is profile specific")

    shortcut_parser = subparsers.add_parser("shortcut", aliases=["sc"], help="Execute a shortcut ---- Specify the name of an existing shortcut to run")
    shortcut_parser.add_argument("shortcut_name", help="Name of the shortcut")

    addprofile_parser = subparsers.add_parser("add-profile", aliases=["ap"], help="Add a new profile ---- gith addprofile [copy]  ----  copy current profile")
    addprofile_parser.add_argument("copy", nargs="?", default=False, help="Copy current profile")
    addprofile_parser.add_argument("name", help="Name of the profile")

    switchprofile_parser = subparsers.add_parser("profile", aliases=["pr"], help="Switch to a different profile ---- gith profile [delete]  ----  delete profile")
    switchprofile_parser.add_argument("delete", nargs="?", default=False, help="Delete a profile")
    switchprofile_parser.add_argument("name", help="Name of the profile")

    subparsers.add_parser("explorer", aliases=["e"], help="Open a file explorer in the repo directory")

    return parser

def main():
    parser = init_arg_parser()
    args, unknown_args = parser.parse_known_args()

    if args.command == "repo" or args.command == "r":
        set_repo_path(args.directory)
        print(f"Repository path set to: {args.directory}")
    elif args.command == "status" or args.command == "s":
        print_status_command(args.all == "all")
    elif args.command == "command" or args.command == "c":
        run_command(args.command_args)
    elif args.command == "sub-init" or args.command == "su":
        submodule_command()
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
        push_command(args.force == "force")
    elif args.command == "fetch" or args.command == "f":
        fetch_command(args.rebase == "rebase")
    elif args.command == "fetch-branch" or args.command == "fb":
        fetch_branch_command(args.branch)
    elif args.command == "branch" or args.command == "b":
        branch_command(args.name)
    elif args.command == "add-shortcut" or args.command == "asc":
        current = args.current == "current"
        add_shortcut_command(args.shortcut_name, args.shortcut_command, current)
    elif args.command == "remove-shortcut" or args.command == "rsc":
        current = args.current == "current"
        remove_shortcut_command(args.shortcut_name, current)
    elif args.command == "shortcut" or args.command == "sc":
        execute_shortcut_command(args.shortcut_name)
    elif args.command == "add-profile" or args.command == "ap":
        add_profile_command(args.name, args.copy == "copy")
    elif args.command == "profile" or args.command == "pr":
        delete = args.delete == "delete"
        switch_profile_command(args.name, delete)
    elif args.command == "explorer" or args.command == "e":
        repo_path = get_repo_path()
        os.system(f"explorer {repo_path}")
    elif unknown_args:
        unknown_command = unknown_args[0]
        if not execute_shortcut_command(unknown_command, False):
            print(f"Error: the command '{unknown_command} is not a known command or shortcut, see list below\n")
            parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
# ------- End Main Logic and Argument Parsing -------