from Crypto.PublicKey import RSA

def carregar_chave_privada(caminho="private_key.pem"):
    with open(caminho, "rb") as f:
        return RSA.import_key(f.read())

def carregar_chave_publica(caminho="public_key.der"):
    with open(caminho, "rb") as f:
        return RSA.import_key(f.read())
