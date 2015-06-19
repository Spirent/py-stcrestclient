# Python STC ReST API Client: stcrestclient

The stcrestclient package provides the stchttp.py ReST API wrapper module.  This allows simple function calls, nearly identical to those provided by StcPython.py, to be used to access TestCenter server sessions via the STC ReST API.

The stcrestclient package also includes the command-line shell `tccsh` that lets you work interactively with remote STC sessions via the ReST API.

Basic ReST functionality is provided by the resthttp module, and may be used for writing ReST clients independent of STC.  This module is built on top of the [Requests](http://docs.python-requests.org/) package.

All code works with Python2.7 and Python3.x.

## Project Links

- Project page: <https://github.com/Spirent/py-stcrestclient>
- Package download: <http://pypi.python.org/pypi/stcrestclient>
- Documentation: See *Spirent TestCenter Automation Programmer's Reference*
- License: <http://www.opensource.org/licenses/mit-license.php>

## Quick Start
- Install stcrestclient:

   `sudo pip install stcrestclient`

- Write Python code to talk with TestCenter server

   `python`
   ```python
   >>> from stcrestclient import stchttp
   >>> stc = stchttp.StcHttp('stcserver.somewhere.com')
   >>> sid = stc.new_session('JoeUser', 'ExampleTest')
   >>> stc.system_info()
   ```

- Interact with TestCenter server

   `python -m stcrestclient.tccsh`

## Installation

### Install Using pip

Make sure python-pip is installed on you system.  If you are using virtualenv, then pip is already installed into environments created by virtualenv, and using sudo is not needed.  To install the latest, use pip to install from pypi:

    sudo pip install stcrestclient

Or, install from the repository archive URL:

    sudo pip install https://github.com/Spirent/py-stcrestclient/archive/master.zip

### Upgrade with pip

If a newer version of the stcrestclient package is available, you can upgrade your existing version using the same command as you used to install, and adding the --upgrade flag:

    sudo pip install --upgrade stcrestclient

### From Source

The stcrestclient package is installed from source using distutils in the usual way.  Download the [source distribution](https://github.com/Spirent/py-stcrestclient/archive/master.zip) first.  Unzip the zip archive and run the setup.py script to install the package site-wide.  Here are to commands to do that:

    wget https://github.com/Spirent/py-stcrestclient/archive/master.zip py-stcrestclient.zip
    unzip py-stcrestclient.zip
    cd py-stcrestclient-*
    sudo python setup.py install

## Using the stchttp module

To use the STC ReST client library, import the `stchttp.py` module, create a new session or join an existing session, and then call the STC API automation functions provided by the module.

```python
from stcrestclient import stchttp
stc = stchttp.StcHttp('stcserver.somewhere.com')

# Create new session
sid = stc.new_session('JoeUser', 'ExampleTest')

# Get system information
stc.system_info()

# Create a Project
project = stc.create('project')

# Create Port under project
port_handle = stc.create('port', project)

# Connect to a chassis
stc.connect('172.16.23.54')

# Configure port location
stc.config(port_handle, {'location': "//172.16.23.54/1/1"})

# Create StreamBlock under Port
sb_handle = stc.create('streamBlock', port_handle)

# Apply config
stc.apply()

# Run STAK command to archive log files
stc.perform('spirent.core.ArchiveDiagnosticLogsCommand')

# Get a list of available files
files_list = stc.files()

# Download and save the diagnostic.tgz file
file_name = 'diagnostic.tgz'
file_data = stc.download(file_name)
with open(file_name, 'w') as save_file:
    save_file.write(file_data)

# Detach from and delete the session
stc.end_session(end_tcsession=True)
```

For example usage, look in the [examples] directory(https://github.com/ajgillis/py-stcrestclient/examples) for Python code examples.  The examples, like the client lib, will run with either Python2.7 or Python3.x.

## Using the ReST API Command line Shell: tccsh

This is an interactive command shell that provides Session Manager and Automation API functionality using a command line interface.  This command accesses a TestCenter Server over its HTTP interface, so no local BLL installation is needed.  This utility is primarily useful for testing and debugging the ReST API.  It should run on any platform with Python 2.7 or 3.x.

To start the shell, use the following command:

    python -m stcrestclient.tccsh

You will be prompted for the server address to connect to.  You can also supply the server address on the command line: `python -m stcrestclient.tccsh 10.8.232.105`  To see command line options: `python python -m stcrestclient.tccsh --help`

    Usage: python -m stcrestclient.tccsh server [options]

	Options:
	  -c command_string
	        Command string.  Commands are separated by ";" (semicolon).

	  -d, --debug
	        Enable debug output.

	  -f, --file file_path
	        Read commands from the specified file.

	  -h, --help
	        Prints this help information.

	  -p, --port port_num
	        Server port to connect to (default 80).


Notice that commands can be entered from a file (--file) or from a command string (-c), as an alternative to the normal interactive mode.

### Interactive tccsh

Once started and connected to a server, you will see a prompt that contains the address of the server you are connected to.

Type help to see help info on the available commands.  This displays the help menu:

	Documented commands (type help <topic>):
	========================================
	chassis       download      join           stc_config         stc_get
	chassis_info  end           ls             stc_connect        stc_help
	connections   exit          new            stc_connectall     stc_perform
	debug_off     files         recording_off  stc_create         system_info
	debug_on      help          recording_on   stc_delete         upload
	delete        info          server         stc_disconnect
	delete_all    is_connected  stc_apply      stc_disconnectall


To see help for a command, type "help" followed by the command name.  For example, type `help ls` to see help on the `ls` command.

Use `Tab` for command auto-completion. Command auto-completion may not work on Windows.

The interactive shell has a recording feature that is enabled by the "recording_on" command.  This records commands, entered interactively, to a file that can be played back later through tccsh.  Executing the recorded commands is done by running tccsh and specifying the file containing the recorded commands, using the --file command line option.

### Command line tccsh

The tccsh shell can also be use on the command line, by specifying a file containing tccsh commands, or by providing a command string.

A file is provided using the "--file" command line option.  A command file contains commands that are executed in order, and each command is on a separate line.  Comment lines, which are lines starting with "#", and blank lines are ignored.

A command string is provided using the "-c" command line option.  A number of command can be specified, each separated by a ";" semicolon.  For example:

   `python -m stcrestclient.tccsh server -c 'new jdoe test1; stc_create project; stc_create port project1'`

The above will create a new test session, create a project, and create a port object under the project.  The output looks like this:

```
Created and joined session: test1 - jdoe
created: project1
created: port1
```


## TestCenter system information.

The stcrestclient package includes a module, systeminfo, to retrieve STC and API information from a system running a TestCenter server. This module is provided as a convenient command line tool to get information about a TestCenter server.

To get information about a TestCenter server use the following command:

   `python -m stcrestclient.systeminfo server_addr`


## Requirements

- Python2.7 or Python3.x
