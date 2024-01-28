package main

import (
    "crypto/sha256"
    "encoding/hex"
    "fmt"
	"Wallet"
)

type TransactionType int

const (
    CoinTransfer TransactionType = iota
    MessageTransfer
)

type Transaction struct {
    SenderAddress    string
    ReceiverAddress  string
    Type             TransactionType
    Amount           float64
    Message          string
    Nonce            int
    TransactionID    string
    Signature        []byte
    TransactionType  string
}

func create_transaction(sender, receiver string, tType TransactionType, amount float64, message string, nonce int) *Transaction {
    transaction := &Transaction{
        SenderAddress:   sender,
        ReceiverAddress: receiver,
        Type:            tType,
        Amount:          amount,
        Message:         message,
        Nonce:           nonce,
    }
    transaction.TransactionID = transaction.GenerateID()
    return transaction
}

func (t *Transaction) GenerateID() string {
    input := fmt.Sprintf("%s:%s:%d:%f:%s:%d",
        t.SenderAddress, t.ReceiverAddress, t.Type, t.Amount, t.Message, t.Nonce)
    hash := sha256.Sum256([]byte(input))
    return hex.EncodeToString(hash[:])
}

func (t *Transaction) String() string {
    return fmt.Sprintf("%s:%s:%d:%f:%s:%d:%s",
        t.SenderAddress, t.ReceiverAddress, t.Type, t.Amount, t.Message, t.Nonce, t.TransactionID)
}

func validate_transaction(transaction *Transaction, blockchain *Blockchain) bool {
    // Verify the transaction's signature
    if !Wallet.verify_signature(transaction, []byte(transaction.SenderAddress), transaction.Signature) {
        return false
    }
    
    // Check if the sender has enough balance for coin transfers
    if transaction.Type == CoinTransfer {
        senderBalance := blockchain.GetBalance(transaction.SenderAddress)
        if senderBalance < transaction.Amount {
            return false
        }
    }
    else if transaction.Type == MessageTransfer {
        senderBalance := blockchain.GetBalance(transaction.SenderAddress)
        messageSize := len(transaction.Message)
        if senderBalance < messageSize {
            return false
        }
    }
        // TODO: Add staking check
    

    // Additional validation logic depending on your blockchain's rules:
    // Check for valid nonce, etc.

    return true
}