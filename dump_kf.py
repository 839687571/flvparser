#!/bin/env python 
## dump key frame 
#   Usage: ./dump_kr [input] [output dir]
#        input:         input flv file.
#        output dir:    output directory.
#
##

import sys
import utils
from utils.parser import *

if __name__=="__main__":
    
    ifile=""
    odir=""
    if len(sys.argv)<2:
        print "Usage: %s [input] [output]"%( sys.argv[0] )
        sys.exit(0)

    ifile = sys.argv[1]
    odir = sys.argv[2]
    tag = None
    found = False

    try:
        f = open(ifile, "r");

        flvheader = FlvHeader()
        reader = Reader(f)

        # read flv header
        flvheader.read(reader)

        # first previous tag size
        reader.readUInt32()
        while True:
            tag = FlvTag()
            tag.read( reader )

            if tag.get_type()==FlvTag.TAG_SCRIPT: # 
                found = True
                break

            reader.readUInt32() #previous tag size

        if not found:
            print "No Script Tag found"
            sys.exit(0)
        
        ## get filepositions
        offs = None
        for prop in tag.context_.ecma_.properities_:
            if prop.name_.value_=="keyframes":
                for prop2 in prop.value_.properities_:
                    if prop2.name_.value_=="filepositions":
                        offs = prop2.value_ # ScriptDataValueStrictArray
                        break
                break

        if not offs:
            print "Not keyframes in Script Tag"
            sys.exit(0)

        ## flush tags
        count=0
        offs.show()
        for o in offs.arr_:
            reader.f_.seek( o.value_ )
            tag = FlvTag()
            tag.read( reader )
            if tag.get_type()!=FlvTag.TAG_VIDEO:
                print "[ERROR] not VIDEO tag at [", count, "]", o.value_
                sys.exit(0)
            
            print "KeyFrame ", count, " at ", o.value_
            of = open( "%s/%d.avc"%(odir, count), "w" )
            of.write( tag.context_.data_ )
            of.close()

            count=count+1

    except EOFError as e:
        None

    f.close()
