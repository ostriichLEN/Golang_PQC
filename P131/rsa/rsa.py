from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# 1. 產生 RSA 公私鑰對
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=1024
)
public_key = private_key.public_key()

# 2. 要加密的訊息
message = b"Hello NCHC!"

# 3. 使用公鑰加密訊息
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# 4. 使用私鑰解密訊息
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# 印出結果
print("原始訊息：", message.decode())
print("加密後：", ciphertext.hex())
print("解密後：", plaintext.decode())
