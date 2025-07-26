import React, { useEffect, useRef } from 'react';
import Message from './Message';

const MessageList = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && !isLoading && (
        <div className="text-center text-gray-500 mt-8">
          <div className="text-2xl mb-2">👋</div>
          <p>Welcome to the E-commerce Customer Support Chatbot!</p>
          <p className="text-sm mt-1">Ask me anything about products, orders, or get help with your shopping experience.</p>
        </div>
      )}
      
      {messages.map((message, index) => (
        <Message key={index} message={message} />
      ))}
      
      {isLoading && (
        <Message message={{ role: 'assistant', content: '' }} isTyping={true} />
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList; 