from cryptography.fernet import Fernet

# === Alice ===
# 1. 產生對稱金鑰（或是事先由Alice與Bob共用）
key = Fernet.generate_key()
cipher = Fernet(key)

# 2. Alice 要傳送的訊息
plaintext = "Hello NCHC!"
plaintext_bytes = plaintext.encode()

# 3. Alice 將訊息加密
ciphertext = cipher.encrypt(plaintext_bytes)

# === 傳輸中（例如透過網路） ===

# === Bob ===
# 4. Bob 收到密文和共享金鑰，進行解密
cipher_bob = Fernet(key)
decrypted_bytes = cipher_bob.decrypt(ciphertext)
decrypted_message = decrypted_bytes.decode()

# === 顯示所有資訊 ===
print("對稱金鑰（Base64編碼）:")
print(key.decode())
print("\n密文（Base64編碼）:")
print(ciphertext.decode())
print("\n解密後明文:")
print(decrypted_message)
