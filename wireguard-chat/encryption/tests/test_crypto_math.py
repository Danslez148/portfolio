# This file contains unit tests for the cryptographic math functions defined in crypto_math.py.
# Tests are derived from csc4026z.link/encryption
import pytest
from encryption.crypto_math import (
    DH, DH_Generate, Hash, MixHash, Mac, Hmac, 
    Kdf1, Kdf2, Kdf3, Timestamp, AEAD_encrypt, AEAD_decrypt
)

def test_dh_generate():
    """Test that DH_Generate returns a valid private/public key tuple."""
    private_key, public_key = DH_Generate()
    assert private_key is not None
    assert public_key is not None
    assert len(private_key) == 32
    assert len(public_key) == 32

def test_dh_shared_secret():
    """Test DH scalar multiplication against the provided assignment inputs."""
    private_key = b'\xb0)e\xdbZ\x01\x8f\x0f\xf5\x91\x88<\xab\x15\x14\x95\xb3\x92\xbd&3\xfe\x18<\x8f\xd6P\xeb\xd0k\xdb\x7f'
    public_key = b'\x14\xde\xd1\x90m?\x0eaBa\xbb\xf8\\\x08\xdd\xfd\x08\xa7?^\x9f\xcb\x16Y\xdf\xa1\\B\x9d\t7k'
    expected_secret = b'p\x06\xe4\x7f\xce\x87\x88\xe2\xb9\xd1\xb0\xb7\xf3\x0e}\xb1\xc6{g\xae\x17\x8b\x17{\x91}\x05&\x0cl\xbd:'
    
    assert DH(private_key, public_key) == expected_secret

def test_aead():
    """Test ChaCha20Poly1305 encryption and decryption."""
    key = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'
    counter = 0 
    plaintext = b"attack at dawn"
    authtext = b'\x8e2\x89\xe2\x14\xfd\x16\x19o\x06\xc9\xb2\xd9\xe8F\xfd\xdaf\xdc\xa4\xf9\xe9\x98\xbc\xd8x\xb9\x90\x1e\n\xac\x98'
    expected_encrypted = b'\xfbv\x84\xea\xd0S\n\xc1\x16\x9et\xd5\xa4/\xeee\x9a\xa9MR\xe3\xd5p3\x85\r\xce\x15r\xcd'
    
    # Test Encryption
    ciphertext = AEAD_encrypt(key, counter, plaintext, authtext)
    assert ciphertext == expected_encrypted
    
    # Test Decryption
    decrypted = AEAD_decrypt(key, counter, ciphertext, authtext)
    assert decrypted == plaintext

def test_hash():
    """Test BLAKE2s hashing."""
    input_data = b'Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s'
    expected_hash = b"`\xe2m\xae\xf3'\xef\xc0.\xc35\xe2\xa0%\xd2\xd0\x16\xebB\x06\xf8rw\xf5-8\xd1\x98\x8bx\xcd6"
    assert Hash(input_data) == expected_hash

def test_mix_hash():
    """Test MixHash convenience function."""
    input1 = b'a' * 50
    input2 = b'b' * 50
    expected_hash = b'#B\x17\x17\xbe=\xfcc\xd6\xb5@81\t\x8dh\x88\x9b\xb3\xa8\xb9\xb2n\n\x02\r:\xcb\xbe\xb0\xa7\xee'
    assert MixHash(input1, input2) == expected_hash

def test_mac():
    """Test keyed BLAKE2s MAC calculation (16-byte output)."""
    key = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'
    input_data = b'I am a message without a MAC, but only for now.'
    expected_mac = b'*\xbd\x8ak4%\xe4\xb0\xe7\x96\xe5z\x14q\xdd!'
    assert Mac(key, input_data) == expected_mac

def test_hmac():
    """Test standard HMAC calculation (32-byte output)."""
    key = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'
    input_data = b'I am a message without an HMAC, but only for now.'
    expected_hmac = b'\x1ew,:\x03\xdd\x0b\x1e\x96\n\x00J\x8c\xe1QzQ\xff\xb8\x02\xcb\xa29\xa8{\x00\x07(\xa6\xc0\x07\xde'
    assert Hmac(key, input_data) == expected_hmac

def test_kdf_functions():
    """Test the HKDF extract-and-expand functions."""
    key = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'
    input_data = b'Choose your LLM adventure folks.'
    
    expected_t1 = b'0fO\x0e\x0f\xb2\xf4\xaa\xcc\x14\x9c\x84\x8a\xb0D\xd3i\xa6\xac\xbf\xae\xdc^\xd0-D"64X\x93W'
    expected_t2 = b'\xaa\x9b\x0fh\xf9\x99z\\%\\\x0f\x8c9L\x7f~<\x1f\xa9G\x9d \x1dw\xba\xc3\x96\x9e\xbb\x8f\x12&'
    expected_t3 = b'\\\xfb\xc9\xf8!\x88\x03\xa1u\xa8!gUk\xfd\x8b4E|\n5\x89\xb1\xb6\xc1\x1a\x8f\xae?\\\xac)'

    assert Kdf1(key, input_data) == expected_t1
    assert Kdf2(key, input_data) == (expected_t1, expected_t2)
    assert Kdf3(key, input_data) == (expected_t1, expected_t2, expected_t3)

def test_timestamp():
    """Test the TAI64N formatted timestamp."""
    t = 1744366282.5143921
    expected_timestamp = b'@\x00\x00\x00g\xf8\xea\xd4\x00\x07\xd9X'
    assert Timestamp(t) == expected_timestamp