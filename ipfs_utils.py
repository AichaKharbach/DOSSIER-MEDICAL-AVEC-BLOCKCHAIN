import os
import base64
import requests
from dotenv import load_dotenv
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

load_dotenv()

PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')

# ------------------------------
# 1. Générer une paire de clés RSA (publique et privée)
# ------------------------------
def generate_key_pair():
    """
    Génère une paire de clés RSA (privée et publique).
    :return: Tuple contenant la clé privée et la clé publique.
    """
    key = RSA.generate(2048)  
    private_key = key.export_key().decode()
    public_key = key.publickey().export_key().decode()
    return private_key, public_key

# ------------------------------
# 2. Chiffrement des données avec AES et RSA
# ------------------------------
def encrypt_file(file_path, public_key):
    """
    Crypte un fichier avec AES et chiffre la clé AES avec RSA.
    :param file_path: Chemin du fichier à chiffrer.
    :param public_key: La clé publique RSA pour chiffrer la clé AES.
    :return: Tuple contenant le nonce, le tag, le fichier chiffré et la clé AES chiffrée.
    """
    aes_key = get_random_bytes(16)

    cipher_aes = AES.new(aes_key, AES.MODE_EAX)

    with open(file_path, "rb") as file:
        plaintext = file.read()
    ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext)

    recipient_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)

    return cipher_aes.nonce, tag, ciphertext, base64.b64encode(encrypted_aes_key).decode()

# ------------------------------
# 3. Téléversement sur IPFS (Pinata)
# ------------------------------
def upload_encrypted_file_to_pinata(nonce, tag, ciphertext, encrypted_aes_key, jwt_token):
    """
    Téléverse les données chiffrées et la clé AES chiffrée sur Pinata (IPFS).
    :param nonce: Nonce AES.
    :param tag: Tag AES.
    :param ciphertext: Fichier chiffré.
    :param encrypted_aes_key: Clé AES chiffrée (RSA).
    :param jwt_token: Jeton d'authentification Pinata.
    :return: Réponse de Pinata contenant le hash IPFS.
    """
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}

    data = {
        "nonce": base64.b64encode(nonce).decode(),
        "tag": base64.b64encode(tag).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "encrypted_aes_key": encrypted_aes_key,
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()  
        else:
            raise Exception(f"Échec du téléversement sur Pinata : {response.text}")
    except Exception as e:
        raise Exception(f"Erreur lors du téléversement sur Pinata : {str(e)}")

# ------------------------------
# 4. Téléchargement depuis IPFS (Pinata)
# ------------------------------
def download_from_pinata(ipfs_hash, jwt_token):
    """
    Télécharge les données chiffrées depuis Pinata (IPFS).
    :param ipfs_hash: Le hash IPFS du fichier à télécharger.
    :param jwt_token: Jeton d'authentification Pinata.
    :return: Données chiffrées sous forme de dictionnaire.
    """
    url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    headers = {"Authorization": f"Bearer {jwt_token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()  
        else:
            raise Exception(f"Échec du téléchargement depuis Pinata : {response.text}")
    except Exception as e:
        raise Exception(f"Erreur lors du téléchargement depuis Pinata : {str(e)}")

# ------------------------------
# 5. Déchiffrement des données avec AES et RSA
# ------------------------------
def decrypt_file(encrypted_data, private_key):
    """
    Déchiffre un fichier chiffré avec AES à l'aide d'une clé privée RSA.
    :param encrypted_data: Données chiffrées récupérées depuis IPFS.
    :param private_key: Clé privée RSA pour déchiffrer la clé AES.
    :return: Contenu déchiffré du fichier.
    """
    encrypted_aes_key = base64.b64decode(encrypted_data["encrypted_aes_key"])
    nonce = base64.b64decode(encrypted_data["nonce"])
    tag = base64.b64decode(encrypted_data["tag"])
    ciphertext = base64.b64decode(encrypted_data["ciphertext"])

    private_rsa_key = RSA.import_key(private_key)
    cipher_rsa = PKCS1_OAEP.new(private_rsa_key)
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)

    cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return plaintext.decode()


