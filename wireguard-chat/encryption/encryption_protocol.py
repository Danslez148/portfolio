import os
import struct
from nacl.public import PrivateKey
from encryption.crypto_math import (
    DH, DH_Generate, Hash, Kdf1, Kdf2, Kdf3, 
    AEAD_encrypt, AEAD_decrypt, Timestamp, Mac,XAEAD_decrypt
)

class WireGuardProtocol:
    """
    Class for wireguard protocol implementation 
    Handles Handshake (Identity/Key Exchange) and Transport (Data/Chat).
    """

    def __init__(self, static_priv, peer_static_pub):
        # Identity Keys
        self.static_priv = static_priv
        self.peer_static_pub = peer_static_pub
        self.preshared_key =b'\x00' * 32 #currently filled with zeros , as assignment doesn't require section 5.2 of wireguard 
       
        # Session Identifiers
        self.local_index = struct.unpack("<I", os.urandom(4))[0]
        self.remote_index = None

        # Noise State (Handshake only)
        self.chaining_key = None
        self.hash = None
        self.ephemeral_priv = None

        # Transport State (Post-Handshake)
        self.is_transport_ready = False
        self.send_key = None
        self.recv_key = None
        self.send_counter = 0
        self.recv_counter = 0
        # Constants
        self.CONSTRUCTION = b"Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s"
        self.IDENTIFIER = b"WireGuard v1 zx2c4 Jason@zx2c4.com"
        self.LABEL_MAC1 = b"mac1----"
        self.LABEL_COOKIE = b"cookie--" # Used for cookie decryption
        #Extended encryption 
        self.cookie = None 
        self.saved_mac1 = None 

    #  HANDSHAKE PHASE

    def create_initiation_packet(self) -> bytes:
        """
        Builds the 148-byte Initiation Packet.
        """
        # Initialise Noise State
        self.chaining_key = Hash(self.CONSTRUCTION)
        self.hash = Hash(self.chaining_key + self.IDENTIFIER)
        self.hash = Hash(self.hash + self.peer_static_pub)

        # Generate ephemeral keypair and mix into state
        self.ephemeral_priv, e_pub = DH_Generate()
        self.chaining_key = Kdf1(self.chaining_key, e_pub)
        self.hash = Hash(self.hash + e_pub)

        # Encrypt our static public key
        ss1 = DH(self.ephemeral_priv, self.peer_static_pub)
        self.chaining_key, key1 = Kdf2(self.chaining_key, ss1)

        # Derive static public key  from private key
        my_static_pub = bytes(PrivateKey(self.static_priv).public_key)

        msg_static = AEAD_encrypt(key1, 0, my_static_pub, self.hash)
        self.hash = Hash(self.hash + msg_static)

        # Encrypt timestamp
        ss2 = DH(self.static_priv, self.peer_static_pub)
        self.chaining_key, key2 = Kdf2(self.chaining_key, ss2)

        msg_timestamp = AEAD_encrypt(key2, 0, Timestamp(), self.hash)
        self.hash = Hash(self.hash + msg_timestamp)

        # Assemble packet body (before MACs)
        # type (1 byte) + reserved (3 bytes) + sender index (4 bytes)
        # + ephemeral (32 bytes) + encrypted static (48 bytes) + encrypted timestamp (28 bytes)
        # = 116 bytes before MACs
        packet_body = (
            b'\x01'                             # type = 1
            + b'\x00' * 3                       # reserved
            + struct.pack("<I", self.local_index)  # sender index
            + e_pub                             # ephemeral public key (32 bytes)
            + msg_static                        # encrypted static key (32 + 16 tag = 48 bytes)
            + msg_timestamp                     # encrypted timestamp (12 + 16 tag = 28 bytes)
        )

        # Calculate mac1 
        # mac1 = Mac(Hash(Label-Mac1 || S_R_pub), packet_body)
        mac_key = Hash(self.LABEL_MAC1 + self.peer_static_pub)
        mac1 = Mac(mac_key, packet_body)
        self.saved_mac1 = mac1 # Save  mac 1 
        
        if self.cookie is None: 
            # If no cookie, mac2 is all zeros , assuming the none extened port is being used 
            mac2 = b'\x00' * 16 
        else: 
            mac2 = Mac(self.cookie, packet_body + mac1)

        return packet_body + mac1 + mac2

    def handle_response_packet(self, packet: bytes) -> str:
        """
        Processes the 92-byte response from the server.
        Handles both Handshake Response (Type 2) and Cookie Reply (Type 3).
        Returns "SUCCESS" if the tunnel is ready, or "COOKIE_RETRY" if a cookie was received..
        """
        if len(packet) < 62:
            raise ValueError("Packet too short for Response")

        # Unpack Response
        msg_type = struct.unpack("<I", packet[0:4])[0]
        if msg_type == 2: 
            self.remote_index = struct.unpack("<I", packet[4:8])[0]
            e_r_pub = packet[12:44]
            msg_empty = packet[44:60] # Authentication Tag

            # Update Noise State
            self.chaining_key = Kdf1(self.chaining_key, e_r_pub)
            self.hash = Hash(self.hash + e_r_pub)

            # Double DH (Ephemeral-Ephemeral and Static-Ephemeral)
            self.chaining_key = Kdf1(self.chaining_key, DH(self.ephemeral_priv, e_r_pub))
            self.chaining_key = Kdf1(self.chaining_key, DH(self.static_priv, e_r_pub))

            # Mix in Pre-shared Key (00000000)
            self.chaining_key, tmp, key3 = Kdf3(self.chaining_key, self.preshared_key)
            self.hash = Hash(self.hash + tmp)

            # Verify the "Empty" message 
            # If this fails, AEAD_decrypt will raise an exception.
            AEAD_decrypt(key3, 0, msg_empty, self.hash)
            self.hash = Hash(self.hash + msg_empty)

            # HANDSHAKE SUCCESS!!!!!!!!!!!! :) 
            self._split_keys()
            return "SUCCESS"
        elif msg_type == 3:
            if len(packet) < 64:
             raise ValueError("Packet too short for Cookie Reply (Type 3)")

            nonce = packet[8:32]              # 24 random bytes
            encrypted_cookie = packet[32:64]  # 32 bytes (16 cookie + 16 poly1305 tag)
            cookie_key = Hash(self.LABEL_COOKIE + self.peer_static_pub)
            self.cookie = XAEAD_decrypt(cookie_key, nonce, encrypted_cookie, self.saved_mac1)
            return "COOKIE_RETRY"
        else:
            raise ValueError(f"Invalid Message Type - Expected 2 or 3, got {msg_type}")
    def _split_keys(self):
        """Generates independent session keys for send/recv."""
        self.send_key, self.recv_key = Kdf2(self.chaining_key, b"")
        self.send_counter = 0
        self.recv_counter = 0
        self.is_transport_ready = True
        
        # Wipe the handshake state from memory
        self.chaining_key = None
        self.hash = None
        self.ephemeral_priv = None

    # DATA transmission 

    def encrypt_message(self, plaintext_bytes: bytes) -> bytes:
        """Wraps msgpack bytes into a WireGuard Type 4 packet."""
        # Header: Type(4), RemoteIndex(4), Counter(8)
        header = struct.pack("<I", 4) + struct.pack("<I", self.remote_index) + \
                struct.pack("<Q", self.send_counter)
        
        ciphertext = AEAD_encrypt(self.send_key, self.send_counter, plaintext_bytes, b"")
        
        packet = header + ciphertext
        self.send_counter += 1
        return packet

    def decrypt_message(self, packet: bytes) -> str:
        """
        Decrypts an incoming Type 4 Data Packet.
        """
        if len(packet) < 28: # Min =  4 type + 4 index + 8 counter + 12 tag + 0 data
            raise ValueError("Data packet too short")

        # Unpack header
        remote_idx = struct.unpack("<I", packet[4:8])[0]
        counter = struct.unpack("<Q", packet[8:16])[0]
        ciphertext = packet[16:]

        # Decrypt
        plaintext = AEAD_decrypt(self.recv_key, counter, ciphertext, b"")
        self.recv_counter = counter + 1
        return plaintext