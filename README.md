# Python STC ReST API Client: stcrestclient

The stcrestclient package provides the stchttp.py ReST API wrapper module.  This allows simple function calls, nearly identical to those provided by StcPython.py, to be used to access TestCenter server sessions via the STC ReST API.

The stcrestclient package also includes the commandline shell `tccsh` that lets you work interactively with remote STC sessions via the ReST API.

All code works with Python2.7 and Python3.x.

## Project Links

- Downloads: <https://github.com/ajgillis/py-stcrestclient>
- Documentation: See *Spirent TestCenter Automation Programmer's Reference*

## Quick Start
- Install stcrestclient:

   `sudo pip install https://github.com/ajgillis/py-stcrestclient/archive/master.zip`

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

Make sure python-pip is installed on you system.  If you are using virtualenv, then pip is alredy installed into environments created by vertualenv, and using sudo is not needed.  To install the latest, use pip with the repository archive URL:

    sudo pip install https://github.com/ajgillis/py-stcrestclient/archive/master.zip


### Upgrade with pip

If a newer version of the stcrestclient package is available, you can upgrade your existing version like this:

    sudo pip install --upgrade https://github.com/ajgillis/py-stcrestclient/archive/master.zip

### From Source

The stcrestclient package is installed from source using distutils in the usual way.  Download the source distribution (https://github.com/ajgillis/py-stcrestclient/archive/master.zip) first.  Unzip the zip archive and run the setup.py script to install the package site-wide.  Here are to commands to do that:

    wget https://github.com/ajgillis/py-stcrestclient/archive/master.zip py-stcrestclient.zip
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

Once started and connected to a server, you will see a prompt that contains the address of the server you are connected to.

Type help to see help info on the available commands.  This displays the help menu: 

	Documented commands (type help <topic>):
	========================================
	chassis       exit          new             stc_create         system_info
	chassis_info  files         results         stc_delete         upgrade
	connections   help          server          stc_disconnect     upload
	delete        info          stc_apply       stc_disconnectall
	delete_all    is_connected  stc_config      stc_get
	download      join          stc_connect     stc_help
	end           ls            stc_connectall  stc_perform


To see help for a command, type "help" followed by the command name.  For example, type `help ls` to see help on the `ls` command.

Use <TAB> for command auto-completion. Command auto-completion may not work on Windows.

## Requirements

- Python2.7 or Python3.x
