# 超過512 bit 會明顯變慢
# RSA標準2048 bit 無法破譯


from sympy import factorint

n = 3458764522947346427
e = 65537


factors = factorint(n)
p, q = list(factors.keys())
print("Eve 分解出 p =", p, ", q =", q)

# 計算 φ(n)
phi = (p - 1) * (q - 1)

# 求出 d（私鑰）
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

d = modinv(e, phi)
print("Eve 算出 d =", d)

# 密文
ciphertext = [3030529166250592041, 843938771573534626, 2148773775910448317,
              2148773775910448317, 329012413651598212, 1829740544955738454,
              430828965784047002, 666892817268534998, 3030529166250592041,
              666892817268534998, 3069524265684469999]

# RSA 解密函數
def mod_exp(base, exponent, mod):
    result = 1
    base = base % mod
    while exponent > 0:
        if exponent % 2:
            result = (result * base) % mod
        base = (base * base) % mod
        exponent //= 2
    return result

# 解密
plaintext = ''.join([chr(mod_exp(c, d, n)) for c in ciphertext])
print("Eve 解密結果：", plaintext)
