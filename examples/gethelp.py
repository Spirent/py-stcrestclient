from __future__ import print_function
import sys
from stcrestclient import stchttp

if len(sys.argv) < 2:
    print('usage: python', sys.argv[0], 'server_addr', file=sys.stderr)
    sys.exit(1)

try:
    stc = stchttp.StcHttp(sys.argv[1])

    print('---- USAGE HELP ----')
    print(stc.help())
    print()
    print('---- COMMANDS HELP ----')
    print(stc.help('commands'))
    print()
    print('---- COMMAND "perform" HELP ----')
    print(stc.help('perform'))

except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
