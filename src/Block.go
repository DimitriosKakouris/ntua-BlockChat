package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"time"
	
)

// Block represents a block in the blockchain
const capacity = 100

type Block struct {
	index        int
	timestamp    time.Time
	transactions []Transaction
	validator     string
	previous_hash string
	current_hash  string
	blockcapacity int
}

// CalculateHash calculates the hash for a block
func (b *Block) CalculateHash() {
	// Convert block data to a string for hashing
	blockData := fmt.Sprintf("%d%s%s%s", b.index, b.timestamp.String(), b.transactions, b.previous_hash)

	// Calculate hash using SHA-256
	hashInBytes := sha256.Sum256([]byte(blockData))
	b.current_hash = hex.EncodeToString(hashInBytes[:])
}

// NewBlock creates a new block with the given data
func NewBlock(index int, transactions []string, previous_hash string) *Block {
	block := &Block{
		index:        		index,
		timestamp:    		time.Now(),
		transactions: 	    transactions,
		previous_hash:     	previous_hash,
		current_hash:       "",
		blockcapacity:		0,
	}
	block.CalculateHash()
	return block
}

func main() {
	// Creating a genesis block 
	genesisBlock := NewBlock(0, []string{"Genesis Transaction"}, "")
	fmt.Printf("Genesis Block:\nindex: %d\ntimestamp: %s\ntransactions: %v\nprevious_hash: %s\ncurrent_hash: %s\n",
		genesisBlock.index, genesisBlock.timestamp.String(), genesisBlock.transactions, genesisBlock.previous_hash, genesisBlock.current_hash)

	// Creating a new block
	newtransactions := Transaction{}
	newBlock := NewBlock(1, newtransactions, genesisBlock.current_hash)
	fmt.Printf("\nNew Block:\nindex: %d\ntimestamp: %s\ntransactions: %v\nprevious_hash: %s\ncurrent_hash: %s\n",
		newBlock.index, newBlock.timestamp.String(), newBlock.transactions, newBlock.previous_hash, newBlock.current_hash)
}
