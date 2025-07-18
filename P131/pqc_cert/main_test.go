package main

import (
	"crypto"
	"crypto/rand"
	"testing"

	"github.com/cloudflare/circl/sign/dilithium/mode2"
)

func TestDilithiumSignAndVerify(t *testing.T) {
	pk, sk, err := mode2.GenerateKey(rand.Reader)
	if err != nil {
		t.Fatalf("failed to generate keys: %v", err)
	}
	if pk == nil || sk == nil {
		t.Fatalf("generated keys are nil: pk=%v, sk=%v", pk, sk)
	}

	message := []byte("message to be signed")
	signature, err := sk.Sign(rand.Reader, message, crypto.Hash(0))
	if err != nil {
		t.Fatalf("failed to sign: %v", err)
	}

	if !mode2.Verify(pk, message, signature) {
		t.Fatal("signature verification failed")
	}
}
