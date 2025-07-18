# --- 工具函數 ---
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def modinv(e, phi):
    def extended_gcd(a, b):
        if b == 0:
            return (1, 0)
        else:
            x1, y1 = extended_gcd(b, a % b)
            x, y = y1, x1 - (a // b) * y1
            return x, y
    x, _ = extended_gcd(e, phi)
    return x % phi

def mod_exp(base, exponent, mod):
    result = 1
    base = base % mod
    while exponent > 0:
        if exponent % 2:
            result = (result * base) % mod
        base = (base * base) % mod
        exponent //= 2
    return result

# --- Bob 產生金鑰 ---
# p = 997
# q = 991
p = 2147483647
q = 1610612741
n = p * q          
phi = (p - 1) * (q - 1)  
e = 65537             # 公鑰指數
d = modinv(e, phi) # 私鑰指數

# 公私鑰顯示
print("📬 Bob 公鑰 (n, e)：", (n, e))
print("🔐 Bob 私鑰 (n, d)：", (n, d))
print()

# --- Alice 準備訊息並加密 ---
def rsa_encrypt(text, e, n):
    return [mod_exp(ord(char), e, n) for char in text]

# --- Bob 接收密文並解密 ---
def rsa_decrypt(cipher_list, d, n):
    return ''.join([chr(mod_exp(c, d, n)) for c in cipher_list])

# Alice 傳的訊息
alice_message = "Hello NCHC!"

# Alice 用 Bob 的公鑰加密
encrypted_message = rsa_encrypt(alice_message, e, n)
print("🧑‍💼 Alice 傳送的原文：", alice_message)
print("📦 加密後的密文：", encrypted_message)
print()

# Bob 用私鑰解密
decrypted_message = rsa_decrypt(encrypted_message, d, n)
print("📥 Bob 解密後的內容：", decrypted_message)
