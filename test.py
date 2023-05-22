from mcproto.buffer import PacketBuffer
from mcproto.protocol import PacketContext, ProtocolState

buffer = PacketBuffer()
context = PacketContext(ProtocolState.HANDSHAKING)
