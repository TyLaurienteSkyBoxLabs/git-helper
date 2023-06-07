## Git Helper

This is a tool meant to help speed up the process of using git.
The tool can
* Cache you current repo so that you can enter git commands without navigating to your repo directory
* Fetch latest master, create a new branch and update submodules and clean non-git files, all in one command
* Add shortcuts for any shell command that you can run using a specified keyword
* Add different profiles for different repos

## *Currently only supporting windows*

1. To get started, download and extract both the gith.py and gith.bat files to your install directory of choice.
2. Run `setx path "%PATH%;C:\path\to\directory\"` to add the path of the program to your main Path environment variable. This allows the `gith` command to work globally across your shell.