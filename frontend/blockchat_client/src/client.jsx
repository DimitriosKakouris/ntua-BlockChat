import React, { useState } from 'react';
import useWebSocket from 'react-use-websocket';

function App() {
  const [message, setMessage] = useState('');
  const [balance, setBalance] = useState(0);
  const [transactionData, setTransactionData] = useState({ from: '', to: '', amount: 0 });
  const [newMessage, setNewMessage] = useState('');

  // Setup WebSocket connection to your server
  const { sendMessage } = useWebSocket('ws://172.18.0.2:8000', {
    onMessage: (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'balance') {
        setBalance(data.balance);
      } else if (data.type === 'message') {
        setMessage(data.message);
      }
      // Handle other types of messages if needed
    },
    shouldReconnect: (closeEvent) => true, // Will attempt to reconnect on all close events
  });

  // Functions to handle user actions
  const sendTransaction = () => {

  
    transaction_data = {'receiver': receiver, 'amount': answers['amount']}
    // response = await send_websocket_request('new_transaction', transaction_data, ip_address, port)
    sendMessage(JSON.stringify({ action: 'new_transaction', data: transactionData}));
  };

  const getBalance = () => {
    sendMessage(JSON.stringify({ action: 'get_balance' }));
  };

  const sendMessageToServer = () => {
    sendMessage(JSON.stringify({ action: 'new_message', message: newMessage }));
  };

  const exit = () => {
    // Handle exit logic if necessary, like closing the WebSocket connection
  };

  return (
    <div className="App">
      <h1>Blockchat Client</h1>
      <div>
        <button onClick={getBalance}>Get Balance</button>
        <p>Balance: {balance}</p>
      </div>
      <div>
        {/* <input type="text" placeholder="From" onChange={(e) => setTransactionData({ ...transactionData, from: e.target.value })} /> */}
        <input type="text" placeholder="Receiver Address" onChange={(e) => setTransactionData({ ...transactionData, to: e.target.value })} />
        <input type="number" placeholder="Amount" onChange={(e) => setTransactionData({ ...transactionData, amount: Number(e.target.value) })} />
        <button onClick={sendTransaction}>New Transaction</button>
      </div>
      <div>
        <input type="text" placeholder="Message" onChange={(e) => setNewMessage(e.target.value)} />
        <button onClick={sendMessageToServer}>New Message</button>
      </div>
      <div>
        <button onClick={exit}>Exit</button>
      </div>
      {message && <p>Last Message: {message}</p>}
    </div>
  );
}

export default App;