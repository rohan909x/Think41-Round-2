import React from 'react';
import { formatTimestamp } from '../services/api';

const ChatMessage = ({ message, isTyping = false }) => {
  if (isTyping) {
    return (
      <div className="flex items-start space-x-2 mb-3 animate-fade-in">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-semibold">AI</span>
          </div>
        </div>
        <div className="flex-1">
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        </div>
      </div>
    );
  }

  const isUser = message.message_type === 'user';

  return (
    <div className={`flex items-start space-x-2 mb-3 animate-slide-up ${
      isUser ? 'flex-row-reverse space-x-reverse' : ''
    }`}>
      <div className="flex-shrink-0">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-primary-500' 
            : 'bg-gray-200'
        }`}>
          <span className={`text-sm font-semibold ${
            isUser ? 'text-white' : 'text-gray-600'
          }`}>
            {isUser ? 'You' : 'AI'}
          </span>
        </div>
      </div>
      
      <div className={`flex-1 max-w-xs lg:max-w-md ${
        isUser ? 'text-right' : ''
      }`}>
        <div className={`chat-message ${
          isUser ? 'user' : 'assistant'
        }`}>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
        <div className={`text-xs text-gray-500 mt-1 ${
          isUser ? 'text-right' : 'text-left'
        }`}>
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage; 