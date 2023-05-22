from itertools import count
import struct

SEGMENT_BITS = 0x7f
CONTINUE_BIT = 0x80

class PayloadParser(object):
    payload: bytearray
    current: int
    def __init__(self, payload):
        self.payload = payload
        self.current = 0

    def readByte(self) -> int:
        end = self.current + 1
        if end >= len(self.payload):
            raise ValueError("Read with no available bytes")
        try:
            return self.payload[self.current]
        finally:
            self.current = end
    
    """def readVarInt(self) -> int:
        value_max = (1 << (32)) - 1
        result = 0
        for i in count():
            byte = self.readByte()
            #print(bin(byte).rjust(10, '0'))
            # Read 7 least significant value bits in this byte, and shift them appropriately to be in the right place
            # then simply add them (OR) as additional 7 most significant bits in our result
            result |= (byte & 0x7F) << (7 * i)
            # Ensure that we stop reading and raise an error if the size gets over the maximum
            # (if the current amount of bits is higher than allowed size in bits)
            if result > value_max:
                raise IOError(f"Received varint was outside the range of {32}-bit int.")

            # If the most significant bit is 0, we should stop reading
            if not byte & 0x80:
                break

        return result"""
    def readVarInt(self) -> int:
        value = 0
        bits = 0
        current_byte = 0
    
        while True:
            current_byte = self.readByte()
            value |= (current_byte & 0x7F) << bits
            bits += 7
    
            #if bits > 35:
                #raise ValueError("VarInt too large")
    
            if not (current_byte & 0x80):
                break
    
        return value

    def readBytes(self, size) -> bytearray:
        end = self.current + size
        if end >= len(self.payload):
            raise ValueError("Read with no available bytes")
        try:
            return self.payload[self.current:end]
        finally:
            self.current = end
    
    def readVarLong(self) -> int:
        value_max = (1 << (64)) - 1
        result = 0
        for i in count():
            byte = self.readByte()
            # Read 7 least significant value bits in this byte, and shift them appropriately to be in the right place
            # then simply add them (OR) as additional 7 most significant bits in our result
            result |= (byte & 0x7F) << (7 * i)

            # Ensure that we stop reading and raise an error if the size gets over the maximum
            # (if the current amount of bits is higher than allowed size in bits)
            if result > value_max:
                raise IOError(f"Received varlong was outside the range of {64}-bit int.")

            # If the most significant bit is 0, we should stop reading
            if not byte & 0x80:
                break

        return result