from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService
from fractions import Fraction
from math import gcd
import numpy as np

service = QiskitRuntimeService(channel="ibm_cloud", token="sg1H8-cT6M-fBStJDxwvoTniFLsnhCk4auLMlQilQElK")
backend_name = "ibm_torino"  # 你可改成 ibm_brisbane 或 ibm_sherbrooke

def c_amod15(a, power):
    if a not in [2,4,7,8,11,13]:
        raise ValueError("'a' must be 2,4,7,8,11 or 13")
    U = QuantumCircuit(4)
    for _ in range(power):
        if a in [2,13]:
            U.swap(2,3)
            U.swap(1,2)
            U.swap(0,1)
        if a in [7,8]:
            U.swap(0,1)
            U.swap(1,2)
            U.swap(2,3)
        if a in [4,11]:
            U.swap(1,3)
            U.swap(0,2)
        if a in [7,11,13]:
            for q in range(4):
                U.x(q)
    return U.to_gate().control()

def qft_dagger(n):
    qc = QuantumCircuit(n)
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit -1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / (2 ** (j - m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc

def qpe_amod15(a):
    N_COUNT = 8
    qc = QuantumCircuit(N_COUNT + 4, N_COUNT)
    for q in range(N_COUNT):
        qc.h(q)
    qc.x(N_COUNT)
    for q in range(N_COUNT):
        qc.append(c_amod15(a, 2**q), [q] + [i + N_COUNT for i in range(4)])
    qc.append(qft_dagger(N_COUNT), range(N_COUNT))
    qc.measure(range(N_COUNT), range(N_COUNT))

    # 使用 service.run 執行
    job = service.run(program="sampler", backend=backend_name, inputs={"circuits": [qc], "shots": 1, "memory": True})
    result = job.result()
    readings = result.get_memory()
    print("Register Reading:", readings[0])
    phase = int(readings[0], 2) / (2 ** N_COUNT)
    print("Corresponding Phase:", phase)
    return phase

# 主程式
N = 15
a = 7
print(f"選擇的 a = {a}")
print(f"gcd({a}, {N}) = {gcd(a, N)}")

FACTOR_FOUND = False
ATTEMPT = 0

while not FACTOR_FOUND:
    ATTEMPT += 1
    print(f"\nATTEMPT {ATTEMPT}:")
    phase = qpe_amod15(a)
    frac = Fraction(phase).limit_denominator(N)
    r = frac.denominator
    print(f"Result: r = {r}")
    if phase != 0:
        guesses = [gcd(a ** (r // 2) - 1, N), gcd(a ** (r // 2) + 1, N)]
        print(f"Guessed Factors: {guesses[0]} and {guesses[1]}")
        for guess in guesses:
            if guess not in [1, N] and (N % guess) == 0:
                print(f"*** 找到非平凡因數: {guess} ***")
                FACTOR_FOUND = True
