package main


import (
	"crypto/sha256"
	
)


type Node struct {
	address 			string
	wallet  			Wallet
	ip 					string
	port 				int
	id 					int
	blockchain 			Blockchain
	pendingTransactions []Transaction
	// ... other fields
}


func create_new_block(transactions *Transaction, bc *Blockchain) *Block {
	// Create a new block
	block := NewBlock(bc.length, transactions, bc.last_block.current_hash)
	// Add the block to the blockchain
	bc.add_block(block)
	// Reset the pending transactions
	bc.pendingTransactions = []Transaction{}
	return block
}