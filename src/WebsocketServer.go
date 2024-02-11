package main

import (
    "encoding/json"
    "net/http"
    "github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        return true // Adjust the origin policy as needed
    },
}

// Define your Node structure
type Node struct {
    // Add node properties here
}

// Node registration info
type NodeInfo struct {
    PublicKey string `json:"public_key"`
    IP        string `json:"ip"`
    Port      string `json:"port"`
}

// Message structure for WebSocket communication
type Message struct {
    Action      string `json:"action"`
    NodeInfo    *NodeInfo `json:"node_info,omitempty"`
    Transaction string `json:"transaction,omitempty"` // Assuming transaction is a serialized string
    Block       string `json:"block,omitempty"` // Assuming block is a serialized string
}

func handleConnections(w http.ResponseWriter, r *http.Request) {
    ws, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        // Handle error
        return
    }
    defer ws.Close()

    for {
        var msg Message
        err := ws.ReadJSON(&msg)
        if err != nil {
            // Handle error
            break
        }

        switch msg.Action {
        case "register_node":
            // Register the node
            // Respond back with confirmation or node ID
        case "broadcast_transaction":
            // Handle transaction
        case "receive_block":
            // Validate and add block
        }
    }
}

func main() {
    http.HandleFunc("/ws", handleConnections)

    // Start the server
    err := http.ListenAndServe("localhost:8765", nil)
    if err != nil {
        // Handle error
    }
}
