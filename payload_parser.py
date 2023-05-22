SEGMENT_BITS = 0x7f
CONTINUE_BIT = 0x80

class PayloadParser:
    payload: bytearray
    current: int
    def __init__(self, payload):
        self.payload = payload
        self.current = 0

    def readByte(self) -> int:
        self.current += 1
        return self.payload[self.current - 1]
    
    def readVarInt(self) -> int:
        value: int = 0
        position: int = 0
        current_byte: int = 0
        while (True):
            current_byte = self.readByte()
            print(bin(current_byte)[2:].rjust(8, "0"))
            value |= (current_byte & SEGMENT_BITS) << position
            if ((current_byte & CONTINUE_BIT) == 0): break

            position += 7
            if (position >= 32): raise ValueError("VarInt too large")
        return value