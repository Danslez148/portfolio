# Message formatter
# Because we have a standard message format we will be required to run through these methods many times. We 
# have placed the formatting and deformatting of the header together in this class. 
# FORMAT: header(10bytes)--> msgID(4bytes), msgType(2bytes), bodyLength(4bytes) body(bodyLength bytes) 

class MessageFormatter:

    @staticmethod
    # takes the msgID, msgType, and the message and puts it into the standard message format. Returns the whole encoded message
    def putTogether(msgID, message):
        encodedMsgID = msgID.to_bytes(1, byteorder="big")
        encodedMessage = message.encode()
        bodyLength = len(encodedMessage)
        encodedBodyLength = bodyLength.to_bytes(4, byteorder='big')
        result = encodedMsgID + encodedBodyLength + encodedMessage
        return result

    @staticmethod
    # pulls apart and decodes the header given. returns the msgID, msgType and the bodyLength. 
    def pullApart(header):
        msgID = int.from_bytes(header[:1], byteorder='big')
        bodyLength = int.from_bytes(header[1:], byteorder='big')
        return msgID, bodyLength
