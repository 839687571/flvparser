#!/bin/env python 
## flv parser
#   Usage: ./flv_parser [path] [-r]
#        path:          flv file path
#        -r:            Row mode. Print all tags.
#
##

import sys
import utils
from utils.parser import *

if __name__=="__main__":
    
    raw=False
    if len(sys.argv)<2:
        print "Usage: %s [flv file] [-r]"%( sys.argv[0] )
        sys.exit(0)

    for i in range( 2, len(sys.argv) ):
        if sys.argv[i]=="-r":
            raw=True

    fpath = sys.argv[1]

    try:
        f = open(fpath, "r");

        flvheader = FlvHeader()
        reader = Reader(f)

        # flv header
        flvheader.read(reader)
        flvheader.show()

        # first previous tag size
        reader.readUInt32()
        while True:
            tag = FlvTag()
            tag.read( reader )

            if raw:
                tag.show()
            elif tag.get_type()==FlvTag.TAG_SCRIPT: # only print script tag
                tag.show()
                break

            reader.readUInt32() #previous tag size

    except EOFError as e:
        None

    f.close()
