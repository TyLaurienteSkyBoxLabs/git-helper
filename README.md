## Git Helper

This is a tool meant to help speed up the process of using git.
The tool can
* Cache you current repo so that you can enter git commands without navigating to your repo directory
* Fetch latest master, create a new branch and update submodules and clean non-git files, all in one command
* Add shortcuts for any shell command that you can run using a specified keyword
* Add different profiles for different repos

### *Currently only supporting windows*

1. Search for and select **Edit the System Environment variables** in the windows search bar
2. On the System Properties window that pops up, select **Environment Variables...**
3. Under **User Variables**, select the `Path` variable
4. Click on new and paste in the path to your program


#### Steps for setup
1. To get started, download and extract both the gith.py and gith.bat files to your install directory of choice
2. Ensure install directory path does not have any spaces in it, or Git Bash usage may not work correctly
3. Add your install directory to your `Path` environment variable. This allows the `gith` command to work globally across your shell.command to work globally across your shell.
4. Run git config --global --add safe.directory '*'

### Allow gith to run globally in Git Bash
1. Navigate to your user folder (`%USERPROFILE%`)
2. Create or open `.bash_profile`
3. Add the below command into the file, subsituting `path/to/git-helper/` for the actual path to git-helper. (Make sure to use forrward slashes`/` instead of back slashes `\` for the path)
4. Save and re-launch git bash, you should now be able to run gith globablly, without the need for specifying.bat

```
gith() {
    path/to/git-helper/gith.bat "${@:1}"
}
```


### Usage:
[ ] *indicates optional parameter*
* `gith repo [directory]`
  * Sets the git repo directory for the current profile, this will be cached for every time you begin using the tool.
  * If no $directory path is passed in, the repo directory will default to your current shells current working directory
* `gith status [all]`
  * Displays information about your current profile and current repo
  * Run `gith status all` to display extra information, such as a list of your profiles and the shortcuts that exist in your current profile.
* `gith command $command`
  * Runs a shell command to the repo directory that's in your current profile. This works from anywhere so you don't have to cd into your repo directory. Ex: `gith command git rebase -i main`
* `gith sub-init`
  * This command will update your submodules by running `git submodule update --init --recursive`
* `gith clean`
  * This command will clean all non-git files in your repo using `git clean -ffdx`. This includes navigating to all sub-modules and running `git clean -ffdx` as well.
* `git commit $commit_message`
  * This command will add all untracked changes using `git add .` and then proceed to commit the changes by running `git commit -m"$commit_message"`
* `git push [force]`
  * This command will push changes to the remote that is has been specified by the `gith remote` command (origin by default).
  * You can run `git push force` to perform a force push.
* `gith fetch [rebase]`
  * This command will do a number of steps to pull latest main into your current checked out branch.
  * This includes: checking out the main branch, fetching changes from remote, resseting local main to remote changes, checking out the previous branch that was checked out, and merging main into that branch.
  * By default, merge is used so as to not be destructive to history, run `git fetch rebase` to rebase instead.
  * **Be careful**, this command will erase your build files and any other git ignored files
* `gith fetch-branch $branch_name`
  * This command will fetch a remote branch, checkout to the fetch branch and reset the local branch to the remote branch
  * **Be careful**, this command will erase your build files and any other git ignored files
* `gith main-branch $branch_name`
  * This command allows specifying a different "main" branch name, for projects that don't use "main" as their main branch. This will be used as the base branch for fetching and branching.
* `gith remote $remote_name`
  * This command allows specifying a different "origin" remote name, for projects that use multiple remotes. This will be used as the base branch for fetching and branching.
* `gith branch $branch_name`
  * This command will do all of the same steps as fetch, but instead of using the previously checked out branch, it will create a new one off of main using the name specified.
  * **Be careful**, this command will erase your build files and any other git ignored files
* `gith shortcut $shortcut_name [$shortcut_command]`
  * This command has two purposes, to save shortcuts and to execute saved shortcuts. 
  * To add a new shortcut, enter both a shortcut name, ans a command for it. If the command has any spaces in it, make sure to encapsulate it in quots "". Ex: `gith shortcut testName "program Folder/testProgram.py"`
  * To execute this new command, simply enter its name only when running. Ex: `gith shortcut testName`
* `gith add-profile [copy] $name`
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

### Shortcut macros
* Shortcut macros allow for certain characters to be interpreted by `gith` to insert certain values.
* `^#repo_path`
  * If this text is specified in a shortcut, the text `^#repo_path` will be substituted for the repo directory that is in the current profile
  * An example of a shortcut that makes use of this is: `gith shortcut start-build "python ^#repo_path/project_gen/start_build.py`

### Chaining shortcuts
* You can chain shortcuts together by calling `gith` multiple times within a shortcut. 
* To do this in command prompt, use the `&&` operator
* To do this in powershell, use the `;` operator
* For chaining commands within a shortcut, you have to use the `&&` operator since `gith` uses cmd as its underlying shell
* An example of this would be to create a shortcut for building a project solution, lets call this shortcut `build-solution`.
* Now what if you would like to fetch latest main and build the solution in one command.
* You can accomplish this by creating another shortcut called `fetch-build-solution`. This can be accomplished using the following command `gith shortcut fetch-build-solution "gith fetch && gith shortcut build-solution`.
* Now that this shortcut is saved, to run both a fetch and a build-solution, simply run `gith shortcut fetch-build-solution` and it will run both commands.

### Non-shortcut chaining
* You can also simply chain commands without creating shortcuts
* For example, you can run `gith branch testBranchName && gith shortcut win32 && gith shortcut build` (Substitute `&&` for `;` if using Powershell)