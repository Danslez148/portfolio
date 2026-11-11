#Wrapper class for encryption_protocol.py to easier usage in main application
import msgpack
from encryption.encryption_protocol import WireGuardProtocol
import socket 
class SecureSocket:
    """
    Handles the WireGuard handshake and encrypts/decrypts msgpack payloads automatically.
    """
    def __init__(self, my_priv_key: bytes, server_pub_key: bytes, host="csc4026z.link", port=51821):
        self.host = host
        self.port = port
        self.proto = WireGuardProtocol(my_priv_key, server_pub_key)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5.0)

    def establish_tunnel(self):
        """
        Executes the initial WireGuard Handshake (Noise IK).
        Must be called before sending any chat data.
        """
        # Send 148-byte initiation
        init_pkt = self.proto.create_initiation_packet()
        self.sock.sendto(init_pkt, (self.host, self.port))
        
        # Wait for 92-byte response
        wg_response, _ = self.sock.recvfrom(2048)        
        # Ask the protocol class what the server said
        status = self.proto.handle_response_packet(wg_response)
        if status == "COOKIE_RETRY":
            print("[!] Server requested MAC2 proof (Extended Port). Resending...")
            retry_pkt = self.proto.create_initiation_packet()
            self.sock.sendto(retry_pkt, (self.host, self.port))
            final_response, _ = self.sock.recvfrom(2048)
            status = self.proto.handle_response_packet(final_response)
        if status != "SUCCESS":
            raise ConnectionError("[!] Handshake failed after cookie retry.")
        print("[+] Secure WireGuard tunnel established successfully!")
        if not self.proto.is_transport_ready:
            raise ConnectionError("[!] WireGuard Handshake failed.")

    def send_dict(self, payload_dict: dict):
        """
        Takes a python dictionary, packs it, encrypts it, and sends it via wireguard defined in encruption_protocol.py
        """
        if not self.proto.is_transport_ready:
            raise RuntimeError("Call establish_tunnel() before sending data.")
            
        packed_payload = msgpack.packb(payload_dict)
        encrypted_pkt = self.proto.encrypt_message(packed_payload)
        self.sock.sendto(encrypted_pkt, (self.host, self.port))

    def recv_dict(self) -> dict:
        """
        Waits for a packet, decrypts it, and returns a python dictionary.
        """
        data, _ = self.sock.recvfrom(4096)
        decrypted_payload = self.proto.decrypt_message(data)
        
        return msgpack.unpackb(decrypted_payload, raw=False)

    def close(self):
        """Closes the  socket."""
        self.sock.close()