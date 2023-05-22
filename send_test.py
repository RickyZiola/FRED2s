from mcproto.buffer import Buffer
from mcproto.protocol.base_io import StructFormat
from mcproto.connection import TCPAsyncConnection
import asyncio
import time
import json
async def chat (message, conn):
    chat_packet = Buffer()
    chat_packet.write_utf(message)
    chat_packet.write_value(StructFormat.LONG, int(time.time()))
    chat_packet.write_value(StructFormat.LONG, 696969)
    chat_packet.write_value(StructFormat.BOOL, False)
    chat_packet.write_varint(1)
    chat_packet.write_varint(0)
    for i in range(20):
        chat_packet.write_value(StructFormat.LONG, 0)
    
    
    packet = Buffer()
    packet.write_varint(0x05)
    packet.write(chat_packet)
    
    
    await conn.write_varint(len(packet))
    await conn.write(packet)
    
async def status(conn: TCPAsyncConnection, ip: str, port: int = 25565) -> dict:
    # This function will be called right after a handshake
    # Sending this packet told the server recognize our connection, and since we've specified
    # the intention to query status, it then moved us to STATUS game state.

    # Different game states have different packets that we can send out, for example there is a
    # game state for login, that we're put into while joining the server, and from it, we tell
    # the server our username player UUID, etc.

    # The packet IDs are unique to each game state, so since we're now in status state, a packet
    # with ID of 0 is no longer the handshake packet, but rather the status request packet
    # (precisely what we need).
    # https://wiki.vg/Protocol#Status_Request

    # The status request packet is empty, and doesn't contain any data, it just instructs the
    # server to send us back a status response packet. Let's send it!
    packet = Buffer()
    packet.write_varint(0)  # Status request packet ID

    await conn.write_varint(len(packet))
    await conn.write(packet)

    # Now, let's receive the response packet from the server
    # Remember, the packet format states that we first receive a length, then packet id, then data
    _response_len = await conn.read_varint()
    _response = await conn.read(_response_len)  # will give us a bytearray

    # Amazing, we've just received data from the server! But it's just bytes, let's turn it into
    # a Buffer object, which includes helpful methods that allow us to read from it
    response = Buffer(_response)
    packet_id = response.read_varint()  # Remember, 2nd field is the packet ID

    # Let's see it then, what packet did we get?
    print(packet_id)  # 0

    # Interesting, this packet has an ID of 0, but wasn't that the status request packet? We wanted
    # a response tho. Well, actually, if we take a look at the status response packet at the wiki,
    # it really has an ID of 0:
    # https://wiki.vg/Protocol#Status_Response
    # Aha, so not only are packet ids unique between game states, they're also unique between the
    # direction a server bound packet (sent by client, with server as the destination) can have an
    # id of 0, while a client bound packet (sent by server, with client as the destination) can
    # have the same id, and mean something else.

    # Alright then, so we know what we got is a status response packet, let's read the wiki a bit
    # further and see what data it actually contains, and see how we can get it out. Hmmm, it
    # contains a UTF-8 encoded string that represents JSON data, ok, so let's get that string, it's
    # still in our buffer.
    received_string = response.read_utf()

    # Now, let's just use the json module, convert the string into some json object (in this case,
    # a dict)
    data = json.loads(received_string)
    return data
async def handshake(conn: TCPAsyncConnection, ip: str, port: int = 25565) -> None:
    # As a simple example, let's request status info from a server.
    # (this is what you see in the multiplayer server list, i.e. the server's motd, icon, info
    # about how many players are connected, etc.)

    # To do this, we first need to understand how are minecraft packets composed, and take a look
    # at the specific packets that we're interested in. Thankfully, there's an amazing community
    # made wiki that documents all of this! You can find it at https://wiki.vg/

    # Alright then, let's take a look at the (uncompressed) packet format specification:
    # https://wiki.vg/Protocol#Packet_format
    # From the wiki, we can see that a packet is composed of 3 fields:
    # - Packet length (in bytes), sent as a variable length integer
    #       combined length of the 2 fields below
    # - Packet ID, also sent as varint
    #       each packet has a unique number, that we use to find out which packet it is
    # - Data, specific to the individual packet
    #       every packet can hold different kind of data, this will be shown in the packet's
    #       specification (you can find these in wiki.vg)

    # Ok then, with this knowledge, let's establish a connection with our server, and request
    # status. To do this, we fist need to send a handshake packet. Let's do it:

    # Let's take a look at what data the Handshake packet should contain:
    # https://wiki.vg/Protocol#Handshake
    handshake = Buffer()
    # We use 47 for the protocol version, as it's quite old, and will work with almost any server
    handshake.write_varint(47)
    handshake.write_utf(ip)
    handshake.write_value(StructFormat.USHORT, port)
    handshake.write_varint(1)  # Intention to query status

    # Nice! Now that we have the packet data, let's follow the packet format and send it.
    # Let's prepare another buffer that will contain the last 2 fields (packet id and data)
    # combined. We do this since the first field will require us to know the size of these
    # two combined, so let's just put them into 1 buffer.
    packet = Buffer()
    packet.write_varint(0)  # Handshake packet has packet ID of 0
    packet.write(handshake)  # Full data from our handshake packet

    # And now, it's time to send it!
    await conn.write_varint(len(packet))  # First field (size of packet id + data)
    await conn.write(packet)  # Second + Third fields (packet id + data)
async def main():
    async with (await TCPAsyncConnection.make_client(("cubeville.org", 25565), 2)) as conn:
        await handshake(conn, "cubeville.org")
        print(await status(conn, "cubeville.org"))
        await chat("Test", conn)
    
    
asyncio.run(main())