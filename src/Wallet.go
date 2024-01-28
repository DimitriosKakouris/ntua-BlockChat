package main

import (
    "crypto/rand"
    "crypto/rsa"
    "crypto/sha256"
    "crypto/x509"
    "encoding/pem"
    "os"
)

type Wallet struct {
    PrivateKey *rsa.PrivateKey
    PublicKey  []byte
}

func NewWallet() *Wallet {
    privateKey, _ := rsa.GenerateKey(rand.Reader, 2048)
    publicKey := &privateKey.PublicKey
    return &Wallet{PrivateKey: privateKey, PublicKey: publicKeyBytes(publicKey)}
}

func publicKeyBytes(pub *rsa.PublicKey) []byte {
    publicKeyBytes, _ := x509.MarshalPKIXPublicKey(pub)
    return pem.EncodeToMemory(&pem.Block{
        Type:  "RSA PUBLIC KEY",
        Bytes: publicKeyBytes,
    })
}

func (w *Wallet) SignTransaction(transaction *Transaction) ([]byte, error) {
    hasher := sha256.New()
    hasher.Write([]byte(transaction.String()))
    signature, err := rsa.SignPSS(rand.Reader, w.PrivateKey, crypto.SHA256, hasher.Sum(nil), nil)
    return signature, err
}

func VerifyTransaction(transaction *Transaction, publicKey []byte, signature []byte) bool {
    pubKey, _ := x509.ParsePKIXPublicKey(publicKey)
    hasher := sha256.New()
    hasher.Write([]byte(transaction.String()))
    err := rsa.VerifyPSS(pubKey.(*rsa.PublicKey), crypto.SHA256, hasher.Sum(nil), signature, nil)
    return err == nil
}
