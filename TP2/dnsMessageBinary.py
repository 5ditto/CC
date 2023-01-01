
class DNSMessageBinary():
    # Message ID, nrValues, nrAut e nrExtra são inteiros
    def __init__(self, messageID, flags, responseCode, nrValues, nrAut, nrExtra, dom, typeValue, respValues, autValues, extraValues):
        self.messageId = messageID
        self.flags = flags
        self.responseCode = responseCode
        self.nrValues = nrValues
        self.nrAut = nrAut
        self.nrExtra = nrExtra
        self.dom = dom
        self.typeValue = typeValue
        self.respValues = respValues
        self.autValues = autValues
        self.extraValues = extraValues

    def convertFlags(self):

        if self.flags == "Q": 
            flags = 1
        if self.flags == "R":
            flags = 2
        if self.flags == "A":
            flags = 3
        if self.flags == "Q+R":
            flags = 4
        if self.flags == "A+R":
            flags = 5

        # 1 byte chega para representar os inteiros de 1 a 5
        bytes = flags.to_bytes(1,byteorder = "big")

        return bytes
    
    @classmethod
    def deconvertFlags(self, flags):

        if flags == 1:
            return "Q"
        if flags == 2:
            return "R"
        if flags == 3:
            return "A"
        if flags == 4:
            return "Q+R"
        if flags == 5:
            return "A+R"
        
        return ""

    def convertTypeValue(self):
        tv = 0

        if self.typeValue == "DEFAULT":
            tv = 1
        if self.typeValue == "SOASP":
            tv = 2
        if self.typeValue == "SOAADMIN":
            tv = 3
        if self.typeValue == "SOASERIAL":
            tv = 4
        if self.typeValue == "SOAREFRESH":
            tv = 5
        if self.typeValue == "SOARETRY":
            tv = 6
        if self.typeValue == "SOAEXPIRE":
            tv = 7
        if self.typeValue == "NS":
            tv = 8
        if self.typeValue == "A":
            tv = 9
        if self.typeValue == "CNAME":
            tv = 10
        if self.typeValue == "MX":
            tv = 11
        if self.typeValue == "PTR":
            tv = 12

        # 1 byte chega para representar os inteiros de 0 a 12
        bytes = tv.to_bytes(1, byteorder="big")

        return bytes

    @classmethod
    def deconvertTypeValue(self, tv):

        if tv == 1:
            return "DEFAULT"
        if tv == 2:
            return "SOASP"
        if tv == 3:
            return "SOAADMIN"
        if tv == 4:
            return "SOASERIAL"
        if tv == 5:
            return "SOAREFRESH"
        if tv == 6:
            return "SOARETRY"
        if tv == 7:
            return "SOAEXPIRE"
        if tv == 8:
            return "NS"
        if tv == 9:
            return "A"
        if tv == 10:
            return "CNAME"
        if tv == 11:
            return "MX"
        if tv == 12:
            return "PTR"
        if tv == 0:
            print("Campo TypeValue inválido!")

        return ""

    def convertMessage(self):
        resultBytes = b''

        # Message id vai de 0 a 65535, ou seja, 2 bytes chegam para reprensetar o Message id
        msgId = self.messageId
        msgId = msgId.to_bytes(2,byteorder="big")
        resultBytes += msgId

        # 1 byte de flags
        resultBytes += self.convertFlags()

        # 1 byte de response code
        rc = int(self.responseCode)
        resultBytes += rc.to_bytes(1, byteorder="big")

        # 1 byte chega para representar o número de response values
        bytes = (self.nrValues).to_bytes(1,byteorder="big")
        resultBytes += bytes

        # 1 byte chega para representar o número de authorities
        bytes = (self.nrAut).to_bytes(1,byteorder="big")
        resultBytes += bytes

        # 1 byte chega para representar o número de extra values
        bytes = (self.nrExtra).to_bytes(1,byteorder="big")
        resultBytes += bytes

        # 1 byte de comprimento da string dom
        resultBytes += (len(self.dom)).to_bytes(1, byteorder="big")
        # String dom codificada com UTF-8
        resultBytes += self.dom.encode('utf-8')

        # 1 byte de typeValue
        resultBytes += self.convertTypeValue()  

        # 1 byte de comprimento da string respValues
        resultBytes += (len(self.respValues)).to_bytes(1, byteorder="big")
        # String respValues codificada com UTF-8
        resultBytes += self.respValues.encode('utf-8')

        # 1 byte de comprimento da string autValues
        resultBytes += (len(self.autValues)).to_bytes(1, byteorder="big")
        # String autValues codificada com UTF-8
        resultBytes += self.autValues.encode('utf-8')

        # 1 byte de comprimento da string extraValues
        resultBytes += (len(self.extraValues)).to_bytes(1, byteorder="big")
        # String extraValues codificada com UTF-8
        resultBytes += self.extraValues.encode('utf-8')

        return resultBytes

    @classmethod
    def deconvertMessage(self, bytes):
        # 2 bytes de Message Id
        mesageId = bytes[:2]
        mesageId = int.from_bytes(mesageId, byteorder="big")

        # 1 byte de flags
        flags = bytes[2:3]
        flags = int.from_bytes(flags, byteorder="big")
        flags = self.deconvertFlags(flags)

        # 1 byte de response code
        responseCode = bytes[3:4]
        responseCode = int.from_bytes(responseCode, byteorder="big")
        responseCode = str(responseCode)

        # 1 byte de nr Response values
        nrRespValues = bytes[4:5]
        nrRespValues = int.from_bytes(nrRespValues, byteorder="big")

        # 1 byte de nr Authorites
        nrAut = bytes[5:6]
        nrAut = int.from_bytes(nrAut, byteorder="big")

        # 1 byte de nr Extra values
        nrExtraValues = bytes[6:7]
        nrExtraValues = int.from_bytes(nrExtraValues, byteorder="big")

        # 1 byte do comprimento da string dom
        comp = bytes[7:8]
        comp = int.from_bytes(comp, byteorder="big")
        # comp bytes de dom
        dm = bytes[8:8+comp]
        dom = dm.decode('utf-8')
        proxPos = 8 + comp

        # 1 byte de typeValue
        typeValue = bytes[proxPos:proxPos+1]
        typeValue = int.from_bytes(typeValue, byteorder="big")
        typeValue = self.deconvertTypeValue(typeValue)
    
        # 1 byte de comprimento da string respValues
        comp = bytes[proxPos+1:proxPos+2]
        comp = int.from_bytes(comp, byteorder="big")
        # comp bytes de respValues
        rv = bytes[proxPos+2:proxPos+2+comp]
        respValues = rv.decode('utf-8')
        proxPos = proxPos+2+comp

        # 1 byte de comprimento da string autValues
        comp = bytes[proxPos:proxPos+1]
        comp = int.from_bytes(comp, byteorder="big")
        # comp bytes de autValues
        av = bytes[proxPos+1:proxPos+1+comp]
        autValues = av.decode('utf-8')
        proxPos = proxPos+1+comp

        # 1 byte de comprimento da string extraValues
        comp = bytes[proxPos:proxPos+1]
        comp = int.from_bytes(comp, byteorder="big")
        # comp bytes de extraValues
        ev = bytes[proxPos+1:proxPos+1+comp]
        extraValues = ev.decode('utf-8')

        return DNSMessageBinary(mesageId,flags,responseCode,nrRespValues,nrAut,nrExtraValues,dom,typeValue,respValues,autValues,extraValues)

    def __str__(self):
        string = "Message Id: " + str(self.messageId) + ", Flags: " + self.flags + ", Response Code: " + self.responseCode + "\n"
        string += "Nr Values: " + str(self.nrValues) + ", Nr Aut: " + str(self.nrAut) + ", Nr Extra: " + str(self.nrExtra) + "\n"
        string += "Dom: " + self.dom + ", Type Value: " + self.typeValue + "\n"
        string += "Response Values: " + self.respValues + ", AutValues: " + self.autValues + ", Extra Values: " + self.extraValues 
        return string

    def dnsMessageLogs(self, pergunta):
        string = ''

        if(pergunta):
            string += str(self.messageId) + "," + self.flags + "," + self.responseCode + "," + str(self.nrValues) + "," + str(self.nrAut) + "," + str(self.nrExtra) + ";"
            string += self.dom + "," +  self.typeValue + ";"
        else:
            string += str(self.messageId) + "," + self.flags + "," + self.responseCode + "," + str(self.nrValues) + "," + str(self.nrAut) + "," + str(self.nrExtra) + ";"
            string += self.dom + "," +  self.typeValue + ";"
            string += self.respValues + self.autValues + self.extraValues

        return string
    
    def dnsMessageDebug(self, pergunta):
        string = ''

        if(pergunta):
            string += "# Header\nMESSAGE-ID = " + str(self.messageId) + ", FLAGS = " + self.flags + ", RESPONSE-CODE = " + self.responseCode + ",\n"
            string += "N-VALUES = " + str(self.nrValues) + ", N-AUTHORITIES = " + str(self.nrAut) + ", N-EXTRA-VALUES = " + str(self.nrExtra) + ",;\n"
            string += "# Data: Query Info\nQUERY-INFO.NAME = " + self.dom + ", QUERY-INFO.TYPE = " + self.typeValue + ",;\n"
            string += "# Data: List of Response, Authorities and Extra Values\n"
            string += "RESPONSE-VALUES = (Null)\n# AUTHORITIES-VALUES = (Null)\n# EXTRA-VALUES = (Null)"
        else:
            string += "# Header\nMESSAGE-ID = " + str(self.messageId) + ", FLAGS = " + self.flags + ", RESPONSE-CODE = " + self.responseCode + ",\n"
            string += "N-VALUES = " + str(self.nrValues) + ", N-AUTHORITIES = " + str(self.nrAut) + ", N-EXTRA-VALUES = " + str(self.nrExtra) + ",;\n"
            string += "# Data: Query Info\nQUERY-INFO.NAME = " + self.dom + ", QUERY-INFO.TYPE = " + self.typeValue + ",;\n"
            string += "# Data: List of Response, Authorities and Extra Values\n"
            string += "RESPONSE-VALUES = " + self.respValues + "\n"
            string += "AUTHORITIES-VALUES = " + self.autValues + "\n"
            string += "EXTRA-VALUES = " + self.extraValues + "\n"

        return string

# # Header
# MESSAGE-ID = 3874, FLAGS = Q+R, RESPONSE-CODE = 0,
# N-VALUES = 0, N-AUTHORITIES = 0, N-EXTRA-VALUES = 0,;
# # Data: Query Info
# QUERY-INFO.NAME = example.com., QUERY-INFO.TYPE = MX,;
# # Data: List of Response, Authorities and Extra Values
# RESPONSE-VALUES = (Null)
# AUTHORITIES-VALUES = (Null)
# EXTRA-VALUES = (Null)

# # Header
# MESSAGE-ID = 3874, FLAGS = R+A, RESPONSE-CODE = 0,
# N-VALUES = 2, N-AUTHORITIES = 3, N-EXTRA-VALUES = 5;
# # Data: Query Info
# QUERY-INFO.NAME = example.com., QUERY-INFO.TYPE = MX;
# # Data: List of Response, Authorities and Extra Values
# RESPONSE-VALUES = example.com. MX mx1.example.com 86400 10,
# RESPONSE-VALUES = example.com. MX mx2.example.com 86400 20;
# AUTHORITIES-VALUES = example.com. NS ns1.example.com. 86400,
# AUTHORITIES-VALUES = example.com. NS ns2.example.com. 86400,
# AUTHORITIES-VALUES = example.com. NS ns3.example.com. 86400;
# EXTRA-VALUES = mx1.example.com. A 193.136.130.200 86400,
# EXTRA-VALUES = mx2.example.com. A 193.136.130.201 86400,
# EXTRA-VALUES = ns1.example.com. A 193.136.130.250 86400,
# EXTRA-VALUES = ns2.example.com. A 193.137.100.250 86400,
# EXTRA-VALUES = ns3.example.com. A 193.136.130.251 86400;

# 31388,Q+R,0,0,0,0;lon3r.,MX;

# 31388,0,2,3,5;lon3r.,MX;lon3r. MX mx1.lon3r. 86400 10;lon3r. MX mx2.lon3r. 86400 20;lon3r. NS ns1.lon3r. 86400;lon3r. NS ns2.lon3r. 86400;lon3r. NS ns3.lon3r. 86400;mx1 A 193.136.130.200 86400;mx2 A 193.136.130.201 86400;ns1 A 193.136.130.250 86400;ns2 A 193.137.100.250 86400;ns3 A 193.136.130.251 86400;