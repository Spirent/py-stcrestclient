from __future__ import print_function
import sys
import os
from stcrestclient import stchttp

if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

config_file = 'config.xml'
if not os.path.isfile(config_file):
    print('missing file:', config_file)
    sys.exit(1)

# Connect to server.
stc = stchttp.StcHttp(sys.argv[1])

# Start new session.
stc.new_session('someuser', 'xmltest')

# Upload the config file.
stc.upload(config_file)

# Load the config.
data = stc.perform('LoadFromXml', filename=config_file)
print(data)


