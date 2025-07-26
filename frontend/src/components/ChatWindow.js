import React, { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import MessageList from './MessageList';
import UserInput from './UserInput';
import ConversationHistory from './ConversationHistory';
import { chatAPI } from '../services/api';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [error, setError] = useState(null);

  // Load conversations on component mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const response = await chatAPI.getSessions();
      setConversations(response.sessions || []);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError('Failed to load conversation history');
    }
  };

  const handleSendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatAPI.sendMessage(messageText, activeConversationId);
      
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update active conversation ID if this is a new conversation
      if (response.session_id && !activeConversationId) {
        setActiveConversationId(response.session_id);
        // Reload conversations to include the new one
        setTimeout(loadConversations, 500);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message. Please try again.');
      
      // Remove the user message if the API call failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectConversation = async (conversationId) => {
    if (conversationId === activeConversationId) return;

    try {
      const response = await chatAPI.getSession(conversationId);
      setMessages(response.messages || []);
      setActiveConversationId(conversationId);
      setError(null);
    } catch (err) {
      console.error('Failed to load conversation:', err);
      setError('Failed to load conversation');
    }
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await chatAPI.deleteSession(conversationId);
      
      // If we're deleting the active conversation, clear the chat
      if (conversationId === activeConversationId) {
        setMessages([]);
        setActiveConversationId(null);
      }
      
      // Reload conversations
      loadConversations();
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError('Failed to delete conversation');
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setActiveConversationId(null);
    setError(null);
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar Toggle for Mobile */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setShowSidebar(!showSidebar)}
          className="p-2 bg-white rounded-lg shadow-lg border border-gray-200"
        >
          {showSidebar ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Conversation History Sidebar */}
      <div className={`${showSidebar ? 'block' : 'hidden'} lg:block`}>
        <ConversationHistory
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-800">
              E-commerce Customer Support
            </h1>
            <p className="text-sm text-gray-500">
              {activeConversationId ? `Session ${activeConversationId}` : 'New Conversation'}
            </p>
          </div>
          <button
            onClick={startNewConversation}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            New Chat
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="text-red-700">{error}</div>
            </div>
          </div>
        )}

        {/* Messages */}
        <MessageList messages={messages} isLoading={isLoading} />

        {/* Input */}
        <UserInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          disabled={!!error}
        />
      </div>
    </div>
  );
};

export default ChatWindow; 