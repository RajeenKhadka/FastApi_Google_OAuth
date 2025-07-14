import React, { useState, useRef, useEffect } from "react";
import "./Chat.css";
import api from "../../api";

const Chat = ({ className = "" }) => {
  // State for messages, input, and loading
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Send message to chatbot
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    // Add user message to chat
    const userMessage = {
      type: "user",
      content: inputMessage,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await api.post("/chat", { message: inputMessage });

      // Add bot response after short delay
      setTimeout(() => {
        const botResponse = response.data.response;
        
        // Limit response length
        const limitedResponse =
          botResponse.length > 300
            ? botResponse.substring(0, 300) + "..."
            : botResponse;

        const botMessage = {
          type: "bot",
          content: limitedResponse,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, botMessage]);
        setIsTyping(false);
      }, 500);
    } catch (error) {
      console.error("Chat error:", error);
      
      // Determine error message
      let errorMsg = "Sorry, I encountered an error. Please try again.";
      if (!error.response) {
        errorMsg = "Connection error. Please check if the backend is running.";
      } else if (error.response?.status === 500) {
        errorMsg = "Server error. Please try a different message.";
      }

      const errorMessage = {
        type: "bot",
        content: errorMsg,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setIsTyping(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Reset chat conversation
  const resetChat = async () => {
    try {
      await api.post("/chat/reset");
      setMessages([]);
    } catch (error) {
      console.error("Reset error:", error);
    }
  };

  // Format timestamp for display
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className={`chat-container ${className}`}>
      <div className="chat-header">
        <h3>AI Assistant</h3>
        <button
          onClick={resetChat}
          className="reset-btn"
          title="Reset conversation"
        >
          🗑️
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>👋 Hello! I'm your AI assistant. How can I help you today?</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <div className="message-content">
              <p>{message.content}</p>
              <span className="message-time">
                {formatTime(message.timestamp)}
              </span>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="message bot typing">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={sendMessage} className="chat-input-form">
        <div className="input-group">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            className="chat-input"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-btn"
            disabled={isLoading || !inputMessage.trim()}
          >
            {isLoading ? "⏳" : "📤"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chat;
