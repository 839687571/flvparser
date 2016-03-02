# following http://download.macromedia.com/f4v/video_file_format_spec_v10_1.pdf
##

import sys
import struct
import StringIO

class Reader:
    def __init__(self, f):
        self.f_ = f

    def tell(self):
        return self.f_.tell()

    def seek(self, pos):
        return self.f_.seek(pos)

    def readAll(self):
        return self.f_.read()

    def read(self, n):
        chunk = self.f_.read(n)
        if len(chunk)!=n:
            raise EOFError()
        return chunk

    def readByte(self):
        n, = struct.unpack("B", self.read(1))
        return n

    def readUInt16(self):
        n, = struct.unpack("!H", self.read(2))
        return n

    def readSInt16(self):
        n, = struct.unpack("!h", self.read(2)) 
        return n 

    def readUInt24(self):
        b1 = self.readByte()
        b2 = self.readByte()
        b3 = self.readByte()
        return ((b1<<16) + (b2<<8) + b3)

    def readUInt32(self):
        n, = struct.unpack("!I", self.read(4))
        return n

    def readSInt32(self):
        n, = struct.unpack("!i", self.read(4))
        return n

    def readUInt64(self):
        n, = struct.unpack("!Q", self.read(8))
        return n

    def readSInt64(self):
        n, = struct.unpack("!q", self.read(8)) 
        return n 
    
    def readDouble64(self):
        n, = struct.unpack("!d", self.read(8))
        return n

    def readString(self):
        n = self.readUInt32()
        return self.read(n)

    def readShortString(self):
        n = self.readUInt16()
        return self.read(n)

#################### SCRIPTDATAVALUE BEGIN ######################
    ##
    # reading for ScriptData
    #Type of the ScriptDataValue.
    #The following types are defined:
    #    0 = Number
    #    1 = Boolean
    #    2 = String
    #    3 = Object
    #    4 = MovieClip (reserved, not supported)
    #    5 = Null
    #    6 = Undefined
    #    7 = Reference
    #    8 = ECMA array
    #    9 = Object end marker
    #    10 = Strict array
    #    11 = Date
    #    12 = Long string
    ##

class ScriptDataProperity:
    def __init__(self):
        self.name_ = ScriptDataValueString(); 
        self.value_ = None; # ScriptDataValue

class ScriptDataValue: 
    def __init__(self, t, simple): 
        self.type_ = t # sr - ScriptReader
        self.simple_ = simple # if simple type 

    def get_type(self):
        return self.type_

    def is_simple(self):
        return self.simple_

    def read(self, sr):
        raise Exception("unimplemented method ScriptDataValue::read")

    def show(self, padding=""):
        raise Exception("unimplemented method ScriptDataValue::show")

    def to_string(self):
        raise Exception("unimplemented method ScriptDataValue::to_string")


class ScriptDataValueNumber(ScriptDataValue):
    def __init__(self):
        ScriptDataValue.__init__(self, 0, True)
        self.value_ = 0.0

    def read(self, sr):
        f = sr.reader_
        self.value_ = f.readDouble64()

    def show(self, padding=""):
        print padding, self.value_

    def to_string(self):
        return str(self.value_)

class ScriptDataValueBoolean(ScriptDataValue):
    def __init__(self):
        ScriptDataValue.__init__(self, 1, True)
        self.value_ = 0

    def read(self, sr):
        f = sr.reader_
        self.value_ = f.readByte()

    def show(self, padding=""):
        print padding, self.value_

    def to_string(self):
        return str(self.value_)

class ScriptDataValueString(ScriptDataValue):
    def __init__(self):
        ScriptDataValue.__init__(self, 2, True)
        self.value_ = ""

    def read(self, sr):
        f = sr.reader_
        self.value_ = f.readShortString()

    def show(self, padding=""):
        print padding, self.value_

    def to_string(self):
        return self.value_

class ScriptDataValueObject(ScriptDataValue):
    def __init__(self):
        ScriptDataValue.__init__(self, 3, False)
        self.properities_ = [] # ScriptDataProperity array

    def read(self, sr):
        f = sr.reader_
        while True:
            old_pos = f.tell()
            tmp = f.read(3)
            if (0, 0, 9)==struct.unpack("BBB", tmp):
                break;
            f.seek( old_pos );
            
            prop = ScriptDataProperity()
            prop.name_.read(sr)
            prop.value_ = sr.readNext()
            self.properities_.append( prop )

    def show(self, padding=""):
        for prop in self.properities_:
            if prop.value_.is_simple():
                print padding, prop.name_.to_string(), ":", prop.value_.to_string()
            else:
                print padding, prop.name_.to_string(), "(", prop.value_.to_string() , ") :"
                prop.value_.show( padding+"\t" )

    def to_string(self):
        return "ScriptDataValueObject"

class ScriptDataValueReference(ScriptDataValue):
    def __init__(self):
        ScriptDataValue.__init__(self, 7, True)
        self.value_

    def read(self, sr):
        f = sr.reader_
        self.value_ = f.readUInt16()

    def show(self, padding=""):
        print padding, self.value_

    def to_string(self):
        return str(self.value_)

class ScriptDataValueEcmaArray(ScriptDataValue):
    def __init__(self):
        ScriptDataValue.__init__(self, 8, False)
        self.properities_ = [] # ScriptDataProperity array

    def read(self, sr):
        f = sr.reader_
        n = f.readUInt32()
        obj = ScriptDataValueObject()
        obj.read( sr )
        self.properities_ = obj.properities_

    def show(self, padding=""):
        for prop in self.properities_:
            if prop.value_.is_simple():
                print padding, prop.name_.to_string(), ":", prop.value_.to_string()
            else:
                print padding, prop.name_.to_string(), "(", prop.value_.to_string() , "): "
                prop.value_.show( padding+"\t" )

    def to_string(self):
        return "ScriptDataValueEcmaArray"

class ScriptDataValueStrictArray(ScriptDataValue):
    def __init__(self):
        ScriptDataValue.__init__(self, 10, False)
        self.arr_ = [] # ScriptDataValue array

    def read(self, sr):
        f = sr.reader_
        n = f.readUInt32()
        for i in range(n):
            v = sr.readNext()
            if v:
                self.arr_.append( v )

    def show(self, padding=""):
        first=True
        print padding, "[",
        for o in self.arr_:
            if first:
                first=False
                print o.to_string() ,
            else:
                print ",", o.to_string() ,
        print "]"

    def to_string(self):
        return "ScriptDataValueStrictArray"

class ScriptDataValueDate(ScriptDataValue):
    def __init__(self):
        ScriptDataValue.__init__(self, 11, True)
        self.date_time_ = 0.0
        self.offset_ = 0

    def read(self, sr):
        f = sr.reader_
        self.date_time_ = f.readDouble64()
        self.offset_ = f.readSInt16()

    def show(self, padding=""):
        print padding, "Date { date: ", self.date_time_, ", offset: ", self.offset_ , "}"

    def to_string(self):
        return padding, "Date { date: ", self.date_time_, ", offset: ", self.offset_ , "}"

class ScriptDataValueLongString(ScriptDataValue):
    def __init__(self):
        ScriptDataValue.__init__(self, 12, True)
        self.value_ = ""

    def read(self, sr):
        f = sr.reader_
        self.value_ = f.readString()

    def show(self, padding=""):
        print padding, self.value_

    def to_string(self):
        return self.value_

#################### SCRIPTDATAVALUE END ######################

class ScriptReader:
    def __init__(self, f):
        self.reader_ = f
    
    def readNext(self):
        value = None
        t = self.reader_.readByte()
        if t==0:
            value = ScriptDataValueNumber()
        elif t==1:
            value = ScriptDataValueBoolean()
        elif t==2:
            value = ScriptDataValueString()
        elif t==3:
            value = ScriptDataValueObject()
        elif t==7:
            value = ScriptDataValueReference()
        elif t==8:
            value = ScriptDataValueEcmaArray()
        elif t==10:
            value = ScriptDataValueStrictArray()
        elif t==11:
            value = ScriptDataValueDate()
        elif t==12:
            value = ScriptDataValueLongString()

        if value:
            value.read( self )
        else:
            raise Exception("[ERROR] unsupported ScriptDataType", t)

        return value

class FlvHeader:
    def __init__(self):
        self.type_ = 0;
        self.version_ = 0;
        self.stream_info_ = 0;
        self.header_len_ = 0;

    def read(self, f):
        self.type_ = f.read(3)
        self.version_ = f.readByte()
        self.stream_info_ = f.readByte()
        self.header_len_ = f.readUInt32()

    def has_video(self):
        if self.stream_info_&0x01!=0:
            return True
        return False

    def has_audio(self):
        if self.stream_info_&0x04!=0:
            return True
        return False

    def show(self):
        print "==========HEADER============"
        print "TYPE: %10s"%(self.type_)
        print "VERSION: %10d"%(self.version_)
        print "STREAM INFO:"
        print " has video: %10d"%(self.has_video())
        print " has audio: %10d"%(self.has_audio())
        print "HEADER LEN: %10d"%(self.header_len_)
        print "==========HEADER============"

class FlvTagHeader:

    TagTypeMap = {8: "AUDIO", 9: "VIDEO", 18: "SCRIPT"};

    def __init__(self):
        self.type_ = 0
        self.data_len_ = 0
        self.ts_ = 0
        self.ts_ext_ = 0
        self.stream_id_ = 0

        self.off_ = 0

    def read(self, f):
        self.off_ = f.tell()

        self.type_ = f.readByte()
        self.data_len_ = f.readUInt24()
        self.ts_ = f.readUInt24()
        self.ts_ext_ = f.readByte()
        self.stream_id_ = f.readUInt24()

    def type_name(self):
        if self.type_==FlvTag.TAG_AUDIO:
            return "AUDIO"
        if self.type_==FlvTag.TAG_VIDEO:
            return "VIDEO"
        if self.type_==FlvTag.TAG_SCRIPT:
            return "SCRIPT"
        return "OTHER(%d)"%(self.type_)

    def show(self):
        print "TAG(off %d) { type: %s, data len: %d, ts: %d, ts ext: %d, stream id: %d }"\
                %( self.off_, self.type_name(), self.data_len_, self.ts_, self.ts_ext_, self.stream_id_ )

class AudioTag:

    FORMAT_NAME = ["Linear PCM, platform endian",
                    "ADPCM",
                    "MP3",
                    "Linear PCM, little endian",
                    "Nellymoser 16-kHz mono",
                    "Nellymoser 8-kHz mono",
                    "Nellymoser",
                    "G.711 A-law logarithmic PCM",
                    "G.711 mu-law logarithmic PCM",
                    "reserved",
                    "AAC",
                    "Speex",
                    "UNDEFINED",
                    "UNDEFINED",
                    "MP3 8-Khz",
                    "Device-specific sound"];

    SOUND_RATE_NAME = ["5.5-kHz", "11-kHz", "22-kHz", "44-kHz"];

    SOUND_SIZE_NAME = ["8Bit-sample", "16Bit-sample"];

    TYPE_NAME = ["Mono sound", "Stereo sound"];

    AAC_TYPE_NAME = ["AAC sequence header", "AAC raw"]

    def __init__(self):
        self.format_ = 0
        self.sample_ = 0
        self.sample_len_ = 0
        self.type_ = 0
        self.aac_pack_type_ = 0
        self.data_ = None

    def read(self, data):
        reader = Reader( StringIO.StringIO(data) )
        info = reader.readByte()
        self.format_ = info>>4
        self.sound_rate_ = ((info>>2)&0x03)
        self.sound_size_ = ((info>>1)&0x01)
        self.type_ = (info&0x01)

        if self.format_ == 10:#AAC
            self.aac_pack_type_ = reader.readByte()

        self.data_ = reader.readAll()

    def show(self):
        print "\t{format: %s, sound rate: %s, sound size: %s, type: %s, data size: %d}"\
                %( self.FORMAT_NAME[self.format_], self.SOUND_RATE_NAME[self.sound_rate_], self.SOUND_SIZE_NAME[self.sound_size_],\
                        self.TYPE_NAME[self.type_], len(self.data_))
        if self.format_ == 10:
            print "\t{aac_pack_type: %s}"%( self.AAC_TYPE_NAME[self.aac_pack_type_])

class VideoTag:
    FRAME_TYPE_NAME = ["", 
            "keyframe (for AVC, a seekable frame)", 
            "inter frame (for AVC, a non-seekable frame)", 
            "disposable inter frame (H.263 only)", 
            "generated keyframe (reserved for server use only)", 
            "video info/command frame"]

    CODEC_NAME = ["", 
            "", 
            "Sorenson H.263", 
            "Screen video", 
            "On2 VP6", 
            "On2 VP6 with alpha channel", 
            "Screen video version 2", 
            "AVC"]

    AVC_TYPE_NAME = ["AVC sequence header", "AVC NALU", "AVC end of sequence"]

    def __init__(self):
        self.frame_type_ = 0;
        self.codec_ = 0;
        self.avc_pack_type_ = 0
        self.composition_time_ = 0
        self.data_ = None

    def read(self, data):
        reader = Reader( StringIO.StringIO(data) )
        info = reader.readByte()
        self.frame_type_ = info>>4;
        self.codec_ = (info&0x0F)
        
        if self.codec_==7: # AVC
            self.avc_pack_type_ = reader.readByte()
            self.composition_time_ = reader.readUInt24()

        self.data_ = reader.readAll()
        
    def show(self):
        print "\t{frame: %s, codec: %s, data size: %d}"%(self.FRAME_TYPE_NAME[self.frame_type_], self.CODEC_NAME[self.codec_], len(self.data_))
        if self.codec_==7:
            print "\t{avc_pack_type: %s, composition_time: %d}"%(self.AVC_TYPE_NAME[self.avc_pack_type_], self.composition_time_)

class ScriptTag:
    def __init__(self):
        self.name_ = ScriptDataValueString()
        self.ecma_ = ScriptDataValueEcmaArray()

    def read(self, data):
        reader = ScriptReader( Reader( StringIO.StringIO(data) ) )
        self.name_ = reader.readNext()
        if self.name_.get_type()!=2:
            raise Exception("ScriptTagBody error, first field ScriptDataValueString")

        self.ecma_ = reader.readNext()
        if self.ecma_.get_type()!=8:
            raise Exception("ScriptTagBody error, second field ScriptDataValueEcmaArray")

    def show(self):
        print self.name_.to_string(), ":"
        self.ecma_.show("\t")

class FlvTag:
    TAG_AUDIO = 8;
    TAG_VIDEO = 9;
    TAG_SCRIPT = 18;

    def __init__(self):
        self.header_ = FlvTagHeader()
        self.context_ = None

    def read(self, f):
        self.header_.read(f)
        data = f.read( self.header_.data_len_ )
        if self.header_.type_==FlvTag.TAG_AUDIO:
            self.context_ = AudioTag()
        elif self.header_.type_==FlvTag.TAG_VIDEO:
            self.context_ = VideoTag()
        elif self.header_.type_==FlvTag.TAG_SCRIPT:
            self.context_ = ScriptTag()
        else:
            raise Exception("unknown tag", self.header_.type_)

        try:
            if self.context_:
                self.context_.read( data )
        except EOFError:
            None
 
    def get_type(self):
        return self.header_.type_;

    def show(self):
        if self.header_.type_!=FlvTag.TAG_SCRIPT:# MetaData don't print header
            self.header_.show()
        if self.context_:
            self.context_.show()
