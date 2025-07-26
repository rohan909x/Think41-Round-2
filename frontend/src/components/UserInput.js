import React, { useState } from 'react';
import { Send } from 'lucide-react';

const UserInput = ({ onSendMessage, isLoading, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
      <div className="flex space-x-3">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
          className="message-input flex-1"
          disabled={isLoading || disabled}
        />
        <button
          type="submit"
          disabled={!message.trim() || isLoading || disabled}
          className="send-button flex items-center space-x-2"
        >
          <Send size={18} />
          <span>Send</span>
        </button>
      </div>
    </form>
  );
};

export default UserInput; 