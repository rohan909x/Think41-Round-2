import React from 'react';
import { formatTimestamp } from '../services/api';

const Message = ({ message, isTyping = false }) => {
  if (isTyping) {
    return (
      <div className="chat-message assistant">
        <div className="typing-indicator">
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
        </div>
      </div>
    );
  }

  const isUser = message.role === 'user';
  const messageClass = `chat-message ${isUser ? 'user' : 'assistant'}`;

  return (
    <div className={messageClass}>
      <div className="flex flex-col">
        <div className="message-content">
          {message.content}
        </div>
        <div className={`text-xs mt-1 ${isUser ? 'text-primary-100' : 'text-gray-500'}`}>
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default Message; 