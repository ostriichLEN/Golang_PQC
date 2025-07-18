package main

import (
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/base64"
	"encoding/json"
	"encoding/pem"
	"fmt"
	"io/ioutil"
	"math/big"
	"time"

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
	// === 產生 PQC 金鑰對 ===
	pubKeyPQC, privKeyPQC, err := mode2.GenerateKey(rand.Reader)
	if err != nil {
		panic(err)
	}

	// === 產生 RSA 金鑰對 ===
	privKeyRSA, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		panic(err)
	}

	// === 產生 Hybrid Certificate (RSA 為主，PQC 放入 extension) ===
	pqcExtension := fmt.Sprintf(`{"algo":"Dilithium","pub":"%s"}`,
		base64.StdEncoding.EncodeToString(pubKeyPQC.Bytes()),
	)
	template := &x509.Certificate{
		SerialNumber: big.NewInt(1),
		Subject: pkix.Name{
			CommonName:         "YU-CHIEH,CHANG",
			Organization:       []string{"NCHC"},
			OrganizationalUnit: []string{"Network & Cybersecurity Division"},
			Country:            []string{"TW"},
		},
		NotBefore:             time.Now(),
		NotAfter:              time.Now().Add(365 * 24 * time.Hour),
		KeyUsage:              x509.KeyUsageDigitalSignature,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageClientAuth},
		BasicConstraintsValid: true,
		ExtraExtensions: []pkix.Extension{
			{
				Id:       []int{1, 2, 3, 4, 5, 6, 7, 8, 1},
				Critical: false,
				Value:    []byte(pqcExtension),
			},
		},
	}

	certDER, err := x509.CreateCertificate(rand.Reader, template, template, &privKeyRSA.PublicKey, privKeyRSA)
	if err != nil {
		panic(err)
	}
	certPEM := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: certDER})

	// 可選: 也寫出 RSA 私鑰與憑證（可除錯用）
	_ = ioutil.WriteFile("../signature/x509_cert.crt", certPEM, 0644)
	_ = ioutil.WriteFile("../signature/RSA_priv.key", pem.EncodeToMemory(
		&pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(privKeyRSA)}), 0644)

	// === 讀取 message.txt ===
	message, err := ioutil.ReadFile("../signature/message.txt")
	if err != nil {
		panic("❌  error: ../signature/message.txt NOT FOUND")
	}

	// === 混合簽章 ===
	hash := sha256.Sum256(message)
	sigRSA, err := rsa.SignPKCS1v15(rand.Reader, privKeyRSA, crypto.SHA256, hash[:])
	if err != nil {
		panic(err)
	}

	sigPQC, err := privKeyPQC.Sign(rand.Reader, message, crypto.Hash(0))
	if err != nil {
		panic(err)
	}

	// === 封裝 JSON 輸出 ===
	signed := HybridSignature{
		Message: string(message),
		SigRSA:  base64.StdEncoding.EncodeToString(sigRSA),
		SigPQC:  base64.StdEncoding.EncodeToString(sigPQC),
		PubPQC:  base64.StdEncoding.EncodeToString(pubKeyPQC.Bytes()),
		Cert:    base64.StdEncoding.EncodeToString(certPEM),
	}
	jsonOut, err := json.MarshalIndent(signed, "", "  ")
	if err != nil {
		panic(err)
	}
	err = ioutil.WriteFile("../signature/hybrid_signature.json", jsonOut, 0644)
	if err != nil {
		panic(err)
	}

	fmt.Println("✅ Signing complete : ../signature/hybrid_signature.json generated successfully")
}
