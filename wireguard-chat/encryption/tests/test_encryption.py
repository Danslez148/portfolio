import os
from dotenv import load_dotenv
import struct
import base64
from encryption.SecureSocket import SecureSocket

#configs
load_dotenv()
B64_MY_PRIVATE = os.getenv("USER_KEY")
B64_SERVER_PUBLIC = os.getenv("SERVER_KEY")

def do_request(secure_sock, request_dict, step_description):
    """A helper just to log steps and inject the random handle."""
    print(f"\n[*] {step_description}")
    
    # Inject a random request_handle , honestly not sure why this is even a thing
    # But hey https://csc4026z.link/chat_messages/session/ is what's being followed here
    request_dict['request_handle'] = struct.unpack("<I", os.urandom(4))[0]
    
    # Send and Receive using wrapper, yall should yoink this for the protocol when doing encryped
    secure_sock.send_dict(request_dict)
    response_dict = secure_sock.recv_dict()
    
    print(f"[+] Server Response: {response_dict}")
    return response_dict

def run_test():
    my_priv = base64.b64decode(B64_MY_PRIVATE)
    server_pub = base64.b64decode(B64_SERVER_PUBLIC)

    #  SOCK INIT 
    secure_sock = SecureSocket(my_priv, server_pub)
    try:
        # HANDSHAKE
        print("[*] Establishing Secure Tunnel...")
        secure_sock.establish_tunnel()
        print("[!] Handshake Complete. Transport phase ready.\n")

        # CONNECT
        connect_res = do_request(secure_sock, {
            'request_type': 1
        }, "STEP 1: Connecting to Chat Server")
        
        session_id = connect_res['session']
        username = connect_res.get('username', 'Unknown')
        print(f"[]-> Logged in as {username} (Session: {session_id})")

        #CREATE A CHANNEL 
        do_request(secure_sock, {
            'request_type': 4,
            'session': session_id,
            'channel': 'tadiwa-test-room',
            'description': 'Literally none ya business bud'
        }, "STEP 2: Creating a Channel")

        #SEND A MESSAGE
        do_request(secure_sock, {
            'request_type': 9,
            'session': session_id,
            'channel': 'tadiwa-test-room',
            'message': 'Big dawg checking in' 
        }, "STEP 3: Sending Message to Channel")

        # LIST CHANNELS
        do_request(secure_sock, {
            'request_type': 5,
            'session': session_id
        }, "Fetching Channel List")

        print("\n" + "="*100)
        print("[:O]Welp , it works on my machine :) ")
        print("="*100)

    except TimeoutError:
        print("[-] TIMEOUT :( ")
    except Exception as e:
        print(f"[-] ERROR: {e}")
    finally:
        secure_sock.close()

if __name__ == "__main__":
    run_test()