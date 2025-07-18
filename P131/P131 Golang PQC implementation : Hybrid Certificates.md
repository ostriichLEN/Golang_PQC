# P131 Golang PQC implementation : Hybrid Certificates
## Background
## X.509 Certificate with PQC extension ( Hybrid Certificates )
- Def:憑證（Certificate）是一種經過簽章的身份證明文件，用來表明「某個公開金鑰」屬於「某個實體（人、網站、公司）

- main.go 這個程式的主要目的是生成一個包含後量子密碼學 (PQC) 
  簽章資訊的 X.509 憑證，並同時生成一個傳統的 RSA 私鑰。
- X.509 憑證，這是目前用在 TLS（HTTPS）、S/MIME（加密郵件）等的標準格式。

| 欄位                | 說明                         |
| ----------------- | -------------------------- |
| **Subject**       | 憑證擁有者的名稱，如 Alice           |
| **Public Key**    | 與憑證綁定的公開金鑰                 |
| **Issuer**        | 誰簽發這張憑證（可能是自己，也可能是憑證機構 CA） |
| **Validity**      | 有效時間（開始與結束）                |
| **Serial Number** | 憑證編號                       |
| **Signature**     | 發行者對上述內容的**簽章**，證明這些資料未被竄改 |
| **Extensions**    | 額外資訊，如用途、PQC 的自定義欄位等       |



 ### 結合兩種密碼學技術：
 1. **後量子密碼學 (PQC)**：使用 Dilithium 演算法來生成金鑰對並對訊息進行簽章。
 2. **傳統密碼學(使用 RSA)**：生成一個 RSA 金鑰對，並用其來簽署 X.509 憑證。

| 模式                | 功能                                                         |
| ----------------- | ---------------------------------------------------------- |
| **RSA 簽章（憑證主體）**  | 與傳統系統相容                                                    |
| **PQC extension** | 提前支援後量子加密驗證                                                |
| **未來用處**          | Client 或 Server 可雙重驗證：<br>RSA + PQC 同時驗證身分、防止 RSA 被量子破解後攻擊 |


  ### 以下是程式碼的詳細解釋：


本專案旨在實作一個混合簽章系統，結合了傳統的 RSA 簽章與後量子密碼學 (Post-Quantum Cryptography, PQC) 中的 Dilithium 簽章演算法。此系統的目標是在現有基礎設施（如 X.509 憑證）的基礎上，提供對抗未來量子電腦攻擊的安全性，同時保持與現有系統的相容性。

#### 專案主要包含兩個部分：
- **簽章模組 (`sign/main.go`)**：負責生成混合金鑰對（RSA 和 Dilithium），建立包含 Dilithium 公鑰的 X.509 憑證，並對訊息進行 RSA 和 Dilithium 雙重簽章。
- **驗證模組 (`verify/verify.go`)**：負責解析混合簽章資料，並分別驗證 RSA 簽章和 Dilithium 簽章。

### 核心技術

- **RSA 簽章**：使用 Go 語言標準庫 `crypto/rsa` 進行 RSA 金鑰生成、簽章和驗證。
- **Dilithium 簽章**：採用 Cloudflare 的 `circl` 密碼學庫中的 `dilithium/mode2` 實作 Dilithium 金鑰生成、簽章和驗證。Dilithium 是一種基於格的後量子簽章演算法，被美國國家標準與技術研究院 (NIST) 選為標準。
- **X.509 憑證**：利用 Go 語言標準庫 `crypto/x509` 建立 X.509 憑證。Dilithium 公鑰以自定義擴展 (Extension) 的形式嵌入到 X.509 憑證中，以實現混合憑證的概念。

### 簽章流程 (`sign/main.go`)
1. **生成金鑰對**：
   - 生成 Dilithium 金鑰對 (`pubKeyPQC`, `privKeyPQC`)。
   - 生成 RSA 金鑰對 (`privKeyRSA`, `pubKeyRSA`)。

2. **建立混合憑證**：
   - 構造一個 X.509 憑證模板。
   - 將 Dilithium 公鑰 (`pubKeyPQC`) 進行 Base64 編碼後，以 JSON 格式嵌入到 X.509 憑證的自定義擴展中。該擴展的 OID 為 `1.2.3.4.5.6.7.8.1`。
   - 使用 RSA 私鑰 (`privKeyRSA`) 對憑證進行簽章，生成 `certDER`。
   - 將憑證編碼為 PEM 格式 (`certPEM`)，並可選地寫入 `x509_cert.crt` 文件。
   - 可選地將 RSA 私鑰寫入 `RSA_priv.key` 文件。

3. **讀取訊息**：
   - 從 `../signature/message.txt` 讀取待簽章的訊息。

4. **執行雙重簽章**：
   - 對訊息計算 SHA256 雜湊值。
   - 使用 RSA 私鑰 (`privKeyRSA`) 對雜湊值進行 RSA 簽章 (`sigRSA`)。
   - 使用 Dilithium 私鑰 (`privKeyPQC`) 對原始訊息進行 Dilithium 簽章 (`sigPQC`)。

5. **封裝與輸出**：
   - 將原始訊息、RSA 簽章、Dilithium 簽章、Dilithium 公鑰和混合憑證封裝成 `HybridSignature` 結構體。
   - 將 `HybridSignature` 結構體序列化為 JSON 格式，並寫入 `../signature/hybrid_signature.json` 文件。

### 驗證流程 (`verify/verify.go`)
1. **讀取與解析簽章資料**：
   - 從 `../signature/hybrid_signature.json` 讀取混合簽章 JSON 文件。
   - 將 JSON 資料解析為 `HybridSignature` 結構體。

2. **RSA 簽章驗證**：
   - 從 `HybridSignature` 中提取 Base64 編碼的憑證 (`sig.Cert`)，並解碼為 PEM 格式。
   - 解析 PEM 憑證，獲取 X.509 憑證對象。
   - 從 X.509 憑證中提取 RSA 公鑰 (`rsaPubKey`)。
   - 對原始訊息計算 SHA256 雜湊值。
   - 使用 RSA 公鑰和雜湊值驗證 RSA 簽章 (`sig.SigRSA`)。

3. **PQC (Dilithium) 簽章驗證**：
   - 從 `HybridSignature` 中提取 Base64 編碼的 Dilithium 公鑰 (`sig.PubPQC`) 和 Dilithium 簽章 (`sig.SigPQC`)。
   - 將 Dilithium 公鑰還原為 `mode2.PublicKey` 對象。
   - 使用還原的 Dilithium 公鑰和原始訊息驗證 Dilithium 簽章。

### 測試 (`main_test.go`)

專案包含一個單元測試 `TestDilithiumSignAndVerify`，用於驗證 Dilithium 簽章和驗證功能的正確性。該測試生成 Dilithium 金鑰對，對一個測試訊息進行簽章，然後驗證簽章的有效性。


##  結論

本專案成功實作了一個混合簽章系統，將傳統的 RSA 簽章與後量子密碼學的 Dilithium 簽章結合，並將 Dilithium 公鑰嵌入到 X.509 憑證中。這為在現有 PKI 基礎設施上逐步引入後量子安全性提供了一種可行的方案。該系統能夠對訊息進行雙重簽章和驗證，為未來的量子威脅提供了額外的安全層。

