import React, { useState, useRef } from 'react';
import axios from 'axios';
import './App.css';
import chatbotLogo from './chatbot.jpg'; // Use the correct path for your image

const App = () => {
  const [messages, setMessages] = useState([
    { text: "Hi Buddy!! How can I help you ?", sender: "bot" },
  ]);
  const [userMessage, setUserMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);

  // Using useRef to store the recognition instance, so it's not re-created
  const recognitionRef = useRef(null);

  // Function to safely display text with line breaks and clickable links
  const formatMessage = (message) => {
    const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g;

    // Replace links with HTML anchor tags
    const formattedMessage = message.replace(linkRegex, (match, text, url) => {
      return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
    });

    // Split the message into an array of strings at line breaks
    return formattedMessage.split("\n").map((item, index) => (
      <span key={index} dangerouslySetInnerHTML={{ __html: item }} />
    ));
  };

  const sendMessage = async () => {
    if (!userMessage.trim()) return;

    // Add the user's message to the chat
    setMessages([...messages, { text: userMessage, sender: "user" }]);

    try {
      // Send the message to the Rasa server
      const response = await axios.post('http://localhost:5005/webhooks/rest/webhook', {
        message: userMessage,
      });

      // Get the bot's response from the Rasa server
      const botResponse = response.data[0]?.text || 'Sorry, I did not understand that.';

      // Add the bot's response to the chat
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: botResponse, sender: "bot" },
      ]);
    } catch (error) {
      console.error("Error sending message to Rasa:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: "Sorry, there was an error. Please try again.", sender: "bot" },
      ]);
    }

    // Clear the input field after sending the message
    setUserMessage("");
  };

  const handleStartRecording = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech Recognition is not supported in this browser.");
      return;
    }

    // Only initialize recognition if it hasn't been initialized yet
    if (!recognitionRef.current) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.lang = 'en-US';  // Set language
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      // Set up result event handler
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript;
        setUserMessage(transcript);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }

    recognitionRef.current.start();  // Start the recording
    setIsRecording(true);
  };

  const handleStopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();  // Stop the recording
      setIsRecording(false);
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        {/* Logo section */}
        <div className="header">
          <img src={chatbotLogo} alt="Chatbot Logo" className="logo" />
          <h1>Chat with Nixie</h1>
        </div>

        {/* Messages section */}
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              <p>{formatMessage(msg.text)}</p> {/* Format message with line breaks and clickable links */}
            </div>
          ))}
        </div>

        {/* Input section */}
        <div className="input-container">
          <input
            type="text"
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            placeholder="Type your message..."
          />
          <button onClick={sendMessage}>Send</button>
        </div>

        {/* Record button */}
        <div className="voice-input">
          <button
            onClick={handleStartRecording}
            disabled={isRecording}
            className="record-btn"
          >
            Start Recording
          </button>
          <button
            onClick={handleStopRecording}
            disabled={!isRecording}
            className="stop-btn"
          >
            Stop Recording
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
