package main

import (
    "github.com/gorilla/websocket"
    "log"
)

func main() {
    // Connect to the server
    c, _, err := websocket.DefaultDialer.Dial("ws://localhost:8765/ws", nil)
    if err != nil {
        log.Fatal("dial:", err)
    }
    defer c.Close()

    // Example: Send node registration
    msg := Message{
        Action: "register_node",
        NodeInfo: &NodeInfo{
            PublicKey: "node_public_key",
            IP:        "node_ip",
            Port:      "node_port",
        },
    }
    err = c.WriteJSON(msg)
    if err != nil {
        log.Fatal("write:", err)
    }

    // Read response
    // ... Handle response
}
