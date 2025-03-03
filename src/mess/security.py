import hashlib
import logging
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 32-byte key using PBKDF2."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000,
        dklen=32
    )


def encrypt_file(file_path: str, password: str):
    """Encrypt a file using AES-256 and delete the original file."""
    if not os.path.exists(file_path):
        logging.error("❌ File not found: %s", file_path)
        return

    salt = os.urandom(16)  # Generate a random salt
    key = derive_key(password, salt)
    iv = os.urandom(16)  # Random IV for CBC mode

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    with open(file_path, "rb") as f:
        plaintext = f.read()

    padded_data = padder.update(plaintext) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_path = file_path + ".mess"
    with open(encrypted_path, "wb") as f:
        f.write(salt + iv + ciphertext)  # Store salt + IV + encrypted data

    os.remove(file_path)  # Delete the original file
    logging.info("✅ File encrypted")


def decrypt_file(file_path: str, password: str):
    """Decrypt a file using AES-256 and delete the encrypted file."""
    if not os.path.exists(file_path):
        logging.error("❌ File not found: %s", file_path)
        return

    if not file_path.endswith(".mess"):
        logging.error("❌ Not an encrypted file!")
        return

    with open(file_path, "rb") as f:
        data = f.read()

    salt, iv, ciphertext = data[:16], data[16:32], data[32:]
    key = derive_key(password, salt)

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    plaintext = unpadder.update(decrypted_padded) + unpadder.finalize()

    decrypted_path = file_path[:-5]  # Remove `.mess` extension
    with open(decrypted_path, "wb") as f:
        f.write(plaintext)

    os.remove(file_path)  # Delete the encrypted file
    logging.info("✅ File decrypted")
