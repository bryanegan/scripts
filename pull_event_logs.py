#!/usr/bin/env python
""" Grab the event logs from a host, assume Win7 default locations"""

import os
import sys
import shutil
from cbapi.response.rest_api import CbEnterpriseResponseAPI
from cbapi.response.models import Sensor
from cbapi.example_helpers import build_cli_parser, disable_insecure_warnings

def main():
    """ Main loop, should probably compose better"""
    parser = build_cli_parser("Download event logs from host")
    parser.add_argument('-i', '--ip', action='store', help="Select the Sensor based on its IP")
    parser.add_argument('-n', '--hostname', action='store',
                        help="Select the Sensor based on its hostname")
    parser.add_argument('-s', '--sensorid', action='store',
                        help="Select the Sensor based on its sensor_id")
    parser.add_argument('-p', '--path', action='store', dest='path',
                        help='Specify a local path to store files')

    args = parser.parse_args()

    if args.path and os.path.isdir(args.path):
        path = args.path
    else:
        path = os.getcwd()
    # Disable requests insecure warnings
    disable_insecure_warnings()

    apiconn = CbEnterpriseResponseAPI()
    # If a sensor id is provided, preclude others, if IP pref over hostname
    if args.sensorid:
        live = apiconn.select(Sensor, unique_id=args.sensorid)
    elif args.ip:
        query = "ip:" + args.ip
        live = apiconn.select(Sensor).where(query).one()
    elif args.hostname:
        query = "hostname:" + args.hostname.upper()
        live = apiconn.select(Sensor).where(query).one()
    else:
        parser.print_usage()
        sys.exit(-1)

    lrsess = live.lr_session()
    # add some error handling

# Look for the files in C:\\windows\system32\winevt\logs\ and make a list of contents
    winlogpath = r"C:\windows\system32\winevt\logs\\"
    # add check to break if path doesn't work
    logcontent = lrsess.list_directory(winlogpath)
    # loop over the new list and go getfile for each one greater than threshold
    # cribbed shutil bits from cblr_cli.py
    for fileob in (fileob for fileob in logcontent if fileob['size'] > 200000):
        fullpath = os.path.join(path, fileob['filename'])
        print "Downloading file %s now" % fileob['filename']
        with open(fullpath, "wb") as fout:
            shutil.copyfileobj(lrsess.get_raw_file(
                os.path.join(winlogpath, fileob['filename'])), fout)

if __name__ == "__main__":
    main()
