package main

import (
    "crypto/sha256"
    "math/rand"
    
)

type Blockchain struct {
    // ... existing fields
    Stakes map[string]float64 // Mapping of node addresses to their staked amounts
}

// Function to select the validator for the next block
func (bc *Blockchain) selectValidator() string {
    var totalStake float64
    for _, stake := range bc.Stakes {
        totalStake += stake
    }

    target := rand.Float64() * totalStake
    cumulative := 0.0

    for address, stake := range bc.Stakes {
        cumulative += stake
        if cumulative >= target {
            return address
        }
    }

    return "" // Fallback, should not usually happen
}

func (w *Wallet) GetBalance(address string) int {
    return w.Balance
    
}
// Example of how to seed the random number generator
func seedRandWithPreviousBlockHash(prevBlockHash string) {
    hashBytes := sha256.Sum256([]byte(prevBlockHash))
    rand.Seed(int64(binary.BigEndian.Uint64(hashBytes[:8])))
}
