## Git Helper

This is a tool meant to help speed up the process of using git.
The tool can
* Cache you current repo so that you can enter git commands without navigating to your repo directory
* Fetch latest master, create a new branch and update submodules and clean non-git files, all in one command
* Add shortcuts for any shell command that you can run using a specified keyword
* Add different profiles for different repos

### *Currently only supporting windows*

1. To get started, download and extract both the gith.py and gith.bat files to your install directory of choice.
2. Run `setx path "%PATH%;C:\path\to\directory\"` (ONLY IN COMMAND PROMPT, other shells can break path) to add the path of the program to your main Path environment variable. This allows the `gith` command to work globally across your shell.
3. Run git config --global --add safe.directory '*'


### Usage:
[ ] *indicates optional parameter*
* `gith repo $directory`
  * Sets the git repo directory for the current profile, this will be cached for every time you begin using the tool.
* `gith status [all]`
  * Displays information about your current profile and current repo
  * Run `gith status all` to display extra information, such as a list of your profiles and the shortcuts that exist in your current profile.
* `gith command $git_command`
  * Runs a git command to the repo in your current profile. This works from anywhere so you don't have to cd into your repo directory. Ex: `gith command rebase -i main`
* `gith subinit`
  * This command will update your submodules by running `git submodule update --init --recursive`
* `gith clean`
  * This command will clean all non-git files in your repo using `git clean -ffdx`. This includes navigating to all sub-modules and running `git clean -ffdx` as well.
* `gith fetch [rebase]`
  * This command will do a number of steps to pull latest main into your current checked out branch.
  * This includes: checking out the main branch, fetching changes from remote, resseting local main to remote changes, checking out the previous branch that was checked out, and merging main into that branch.
  * By default, merge is used so as to not be destructive to history, run `git fetch rebase` to rebase instead.
* `gith mainbranch $branch_name`
  * This command allows specifying a different "main" branch name, for projects that don't use "main" as their main branch. This will be used as the base branch for fetching and branching.
* `gith branch $branch_name`
  * This command will do all of the same steps as fetch, but instead of using the previously checked out branch, it will create a new one off of main using the name specified.
* `gith shortcut $shortcut_name [$shortcut_command]`
  * This command has two purposes, to save shortcuts and to execute saved shortcuts. 
  * To add a new shortcut, enter both a shortcut name, ans a command for it. If the command has any spaces in it, make sure to encapsulate it in quots "". Ex: `gith shortcut testName "program Folder/testProgram.py"`
  * To execute this new command, simply enter its name only when running. Ex: `gith shortcut testName`
* `gith addprofile [copy] $name`
  * This command creates a new profile and sets it as our current.
  * Profiles allow differnt repos to be cached so that you can quickly jump between different projects. Shortcuts and mainbranch overrides are also unique to each profile.
  * To create a new profile, type `gith addprofile testProfileName`. This will create a new profile called testProfileName which will be blank.
  * If you would like to copy the current shortcuts, repo path and mainbranch override to the new profile, you can add the `copy` command before the name. Ex: `gith addprofile copy testProfileName`.
* `gith profile [delete] $profile_name`
  * This command allows you to switch between you different profiles. To switch profiles, run `gith profile testProfileName`.
  * Remember that to see all of your profiles, simply enter `gith status all` at any time.
  * If you would like to delete a profile, you can add the `delete` command before the name. Ex: `gith profile delete testProfileName`
* `gith explorer`
  * This command will open a file explorer in the directory of your current profiles repo.
