# Eve 假設只知道 n 和 e（公鑰）
n = 988027
e = 65537

# 嘗試分解 n（暴力法，適用小數）
for i in range(2, int(n**0.5)+1):
    if n % i == 0:
        p = i
        q = n // i
        break

print("Eve 分解出 p =", p, ", q =", q)

# 計算 φ(n)
phi = (p - 1) * (q - 1)

# 求出 d
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

# 解密密文
ciphertext = [779438, 291699, 577623, 577623, 777124, 169492, 475830, 494822, 779438, 494822, 293306]

# RSA 指數運算
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