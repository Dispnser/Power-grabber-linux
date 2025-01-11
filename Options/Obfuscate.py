import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def xor_encrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def encrypt_with_aes(data, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

def obfuscate_file(file_path, iterations=3):
    with open(file_path, 'r') as file:
        code = file.read().encode('utf-8')
    
    for _ in range(iterations):
        key = os.urandom(16)
        code = xor_encrypt(code, key)
        code = encrypt_with_aes(code, key)
        code = f"""
import base64, os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def xor_decrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def decrypt_with_aes(data, key):
    decoded = base64.b64decode(data.encode('utf-8'))
    iv = decoded[:16]
    encrypted_data = decoded[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_data) + decryptor.finalize()

key = {list(key)}
encrypted_code = '{code}'
decrypted_code = xor_decrypt(decrypt_with_aes(encrypted_code, bytes(key)), bytes(key)).decode('utf-8')
exec(decrypted_code)
"""
    
    obfuscated_code = f"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
{code}
"""
    with open(file_path, 'w') as file:
        file.write(obfuscated_code)
    
    print("Obfuscation complete.")

if __name__ == "__main__":
    obfuscate_file(__file__)
