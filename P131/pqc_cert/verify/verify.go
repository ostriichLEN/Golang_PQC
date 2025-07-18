package main

import (
	"crypto"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/base64"
	"encoding/json"
	"encoding/pem"
	"errors"
	"fmt"
	"os"

	"github.com/cloudflare/circl/sign/dilithium/mode2"
)

type HybridSignature struct {
	Message string `json:"message"`
	SigRSA  string `json:"sig_rsa"`
	SigPQC  string `json:"sig_pqc"`
	PubPQC  string `json:"pub_pqc"`
	Cert    string `json:"cert"`
}

func main() {
	// ✅ 改成 signature 資料夾下的檔案
	err := VerifyHybridSignature("../signature/hybrid_signature.json")
	if err != nil {
		fmt.Println("❌ 驗證失敗:", err)
		os.Exit(1)
	}

	fmt.Println("✅ 雙重簽章驗證成功")
}

func VerifyHybridSignature(filename string) error {
	data, err := os.ReadFile(filename)
	if err != nil {
		return fmt.Errorf("讀取 JSON 失敗: %w", err)
	}

	var sig HybridSignature
	if err := json.Unmarshal(data, &sig); err != nil {
		return fmt.Errorf("解析 JSON 失敗: %w", err)
	}

	message := []byte(sig.Message)

	// === RSA 驗證 ===
	certBlock, _ := pem.Decode(decodeB64(sig.Cert))
	if certBlock == nil {
		return errors.New("解析 PEM 憑證失敗")
	}
	cert, err := x509.ParseCertificate(certBlock.Bytes)
	if err != nil {
		return fmt.Errorf("解析 X.509 憑證失敗: %w", err)
	}

	rsaPubKey, ok := cert.PublicKey.(*rsa.PublicKey)
	if !ok {
		return errors.New("憑證中不是 RSA 公鑰")
	}

	hash := sha256.Sum256(message)
	sigBytesRSA := decodeB64(sig.SigRSA)
	if err := rsa.VerifyPKCS1v15(rsaPubKey, crypto.SHA256, hash[:], sigBytesRSA); err != nil {
		return fmt.Errorf("RSA 驗證失敗: %w", err)
	}
	fmt.Println("✅ RSA 簽章驗證成功")

	// === PQC 驗證 ===
	pubKeyBytes := decodeB64(sig.PubPQC)
	sigBytesPQC := decodeB64(sig.SigPQC)

	var pubKeyPQC mode2.PublicKey
	if err := pubKeyPQC.UnmarshalBinary(pubKeyBytes); err != nil {
		return fmt.Errorf("還原 PQC 公鑰失敗: %w", err)
	}

	if !mode2.Verify(&pubKeyPQC, message, sigBytesPQC) {
		return errors.New("PQC 簽章驗證失敗")
	}
	fmt.Println("✅ PQC 簽章驗證成功")

	fmt.Printf("📜 Certificate info:\n- 簽署者: %s\n- 簽署單位: %s\n -簽署部門: %s\n- 有效期自: %s 到 %s\n",
		cert.Subject.CommonName,
		cert.Subject.Organization,
		cert.Subject.OrganizationalUnit,
		cert.NotBefore.Format("2006-01-02 15:04:05"),
		cert.NotAfter.Format("2006-01-02 15:04:05"))

	return nil
}

func decodeB64(s string) []byte {
	b, err := base64.StdEncoding.DecodeString(s)
	if err != nil {
		panic("Base64 解碼失敗: " + err.Error())
	}
	return b
}
