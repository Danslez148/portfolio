import nacl.bindings
import nacl.public
import hashlib
import hmac
import time
import struct
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from nacl.bindings import crypto_aead_xchacha20poly1305_ietf_decrypt


def DH_Generate():
    """Generates a new Diffie-Hellman private/public keypair."""
    #Ripped straight from https://csc4026z.link/encryption/
    private_key = nacl.public.PrivateKey.generate()
    return (bytes(private_key), bytes(private_key.public_key))

def DH(private_key, public_key):
    """Calculates the shared secret given a private and public key."""
    #Ripped straight from https://csc4026z.link/encryption/
    return nacl.bindings.crypto_scalarmult(n=private_key, p=public_key)

def Hash(data: bytes) -> bytes:
    """#BLAKE2s with a 32-byte output hashing function."""
    hasher = hashlib.blake2s(digest_size=32)
    hasher.update(data)
    return hasher.digest()

def MixHash(hash_val: bytes, data: bytes) -> bytes:
    """Convenience function: Hash(hash_val || data)"""
    return Hash(hash_val + data)

def Mac(key: bytes, data: bytes) -> bytes:
    """Message Authentication Code calculation."""
    # keyed BLAKE2s hash with a 16-byte output.
    hasher = hashlib.blake2s(data, key=key, digest_size=16)
    return hasher.digest()

def Hmac(key: bytes, data: bytes) -> bytes:
    """Hash-based Message Authentication Code calculation."""
    return hmac.new(key, data, hashlib.blake2s).digest()

def Kdf1(key: bytes, input_data: bytes) -> bytes:
    """Key Derivation Function 1."""
    t0 = Hmac(key, input_data)
    t1 = Hmac(t0, b'\x01')
    return t1

def Kdf2(key: bytes, input_data: bytes) -> tuple:
    """Key Derivation Function 2. Returns (key1, key2)."""
    t0 = Hmac(key, input_data)
    t1 = Hmac(t0, b'\x01')
    t2 = Hmac(t0, t1 + b'\x02')
    return (t1, t2)

def Kdf3(key: bytes, input_data: bytes) -> tuple:
    """Key Derivation Function 3. Returns (key1, key2, key3)."""
    t0 = Hmac(key, input_data)
    t1 = Hmac(t0, b'\x01')
    t2 = Hmac(t0, t1 + b'\x02')
    t3 = Hmac(t0, t2 + b'\x03')
    return (t1, t2, t3)

def AEAD_encrypt(key: bytes, counter: int, plaintext: bytes, authtext: bytes) -> bytes:
    """Encrypts plaintext using Authenticated Encryption with Associated Data."""
    # ChaCha20-Poly1305 requires a 12-byte 'nonce'\number used once. Wireguard's protocol uses a 4-byte counter, so we pad it to 12 bytes.
    # '<Q' packs the counter as an 8-byte Little-Endian unsigned long long.
    num_used_once = b'\x00\x00\x00\x00' + struct.pack("<Q", counter)
    
    chacha = ChaCha20Poly1305(key)
    return chacha.encrypt(num_used_once, plaintext, authtext)

def AEAD_decrypt(key: bytes, counter: int, ciphertext: bytes, authtext: bytes) -> bytes:
    """Decrypts ciphertext using Authenticated Encryption with Associated Data."""
    num_used_once = b'\x00\x00\x00\x00' + struct.pack("<Q", counter)
    chacha = ChaCha20Poly1305(key)
    return chacha.decrypt(num_used_once, ciphertext, authtext)

def Timestamp(t: float = None) -> bytes:
    """Generates a formatted 12-byte timestamp.
       t for testing purposes, if not provided, it defaults to the current time as specified in assignment docs
    """
    if t is None:
        t = time.time()
    # Wireguard expects 12-byte timestamp .
    # TAI64N adds exactly 0x4000000000000000a to the UNIX seconds
    # https://blog.dave.tf/post/tai64-is-not-tai/
    # 8 bytes for seconds, 4 bytes for microseconds.(Wireguard has nano, but assignement is micro)
    seconds = int(t) + 0x400000000000000a
    microseconds = int((t - int(t)) * 1e6)

    # Pack it as Big-Endian ('>'): 'q' is an 8-byte int for seconds, 'I' is a 4-byte int for microseconds.
    return struct.pack(">qI", seconds, microseconds)


def XAEAD_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, additional_data: bytes) -> bytes:
    """
    XChaCha20-Poly1305 authenticated decryption (XAEAD).
    Unlike AEAD, uses a 24-byte random nonce instead of a 12-byte counter nonce.
    Used for cookie reply for the extended wireguard  
    """
    return crypto_aead_xchacha20poly1305_ietf_decrypt(
        ciphertext=ciphertext,
        aad=additional_data,
        nonce=nonce,
        key=key
    )  