# P4 to Gource
This Python CLI tool will generate a basic report of the changes in a Helix Core repository (number of changes, number of users, number of operations) and generate a Gource-style log. The log can be used with [Gource](https://gource.io/) to generate a pretty visualization of all the activity in the depot.

## Prerequisites
If you are using the pre-compiled windows binary, the only prerequisite is the [P4 CLI](https://www.perforce.com/downloads/helix-command-line-client-p4).

If you are running from the python script you need the P4 CLI, Python 3 (tested on 3.9) and the p4python module with `pip install p4python`


## Usage
On Windows, you can use the pre-compiled binary in this repository: `bin/p2g.exe`

By default, the tool will use whatever server and user is set in your P4 environment and will report changes on all depots.

You can change the port (server address), user, and password just like you would in the P4 CLI with the -p, -u, and -P flags.  
For example: 
    
    `p2g -p ssl:my-server-ip:1666 -u my_username -P my_password`

You can also specify specific Perforce-style depot paths to limit the report and log to changes that affect those paths.  
For example: 

    `p2g //depot_1/... //depot_2/stream_1/... //depot_3/*/src/...`

By default it will create a Gource-style log in the current directory as `gource.log` but you can change the log path and filename with the `-l` or `--logname` flag. 
Or you can opt out of creating a gource log with the `--no-gource` flag.

    usage: p2g.exe [-h] [-p PORT] [-P PASSWORD] [-u USER] [--no-gource] [-l LOGNAME] [depotPath ...]

## Use with Gource
You can install Gource on Windows with the installer available at [Gource.io](https://gource.io/downloads).

Gource has many [command-line options](https://github.com/acaudwell/Gource/wiki/Controls) that you can use to customize the visualization.

Here is an example of some of my preferred settings: 

    gource -f --seconds-per-day .1 --auto-skip-seconds 1 --file-idle-time 0 --hide filenames --log-format custom gource.log

An example of what Gource looks like (click to view on Youtube): 
[![Video of Gource visualization of repo activity](https://img.youtube.com/vi/NjUuAuBcoqs/0.jpg)](https://www.youtube.com/watch?v=NjUuAuBcoqs)

## Building From Source
You can also build the tool from source:

1. Create a python 3 virtual environment. eg. `py -3.9 -m venv .env`
2. Activate the environment: `.env/Scripts/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Build with pyinstaller: `pyinstaller --distpath ./bin --workpath ./build --noconfirm --onefile src/p2g.py`

