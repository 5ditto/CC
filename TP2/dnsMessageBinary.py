
class DNSMessageBinary():
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

    def serealizeFlags(self):

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

        flags = bin(flags)
        flags = flags[2:]

        return flags

    def serealize(self):
        bits = b''

        msgID = bin(self.messageId)
        msgID = msgID[2:]
        bits += msgID

        bits += self.serealizeFlags()

        return bits

    def deserealize(self):
        
        

