import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Bot, User, Loader2, Sparkles, AlertCircle } from 'lucide-react';

interface ChatInterfaceProps {
  location: string;
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  error?: boolean;
}

const API_BASE_URL = 'http://localhost:5000'; // Change in production

const ChatInterface: React.FC<ChatInterfaceProps> = ({ location }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: `Hi! I'm your AI food assistant. I can help you find great food recommendations based on your location in ${location}. What are you in the mood for today?`,
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [demoMode, setDemoMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickSuggestions = [
    "I'm hungry, suggest something",
    "What's good for this weather?",
    "Show me healthy options",
    "Something spicy please",
    "Quick snack ideas"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/food/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text.trim(),
          location: location
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response');
      }

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        sender: 'bot',
        timestamp: new Date(),
        error: false
      };

      setDemoMode(data.demo_mode || false);
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm having trouble connecting to the food assistant. Please try again later.",
        sender: 'bot',
        timestamp: new Date(),
        error: true
      };
      setMessages(prev => [...prev, botMessage]);
      setDemoMode(true);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputText);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Demo Mode Notice */}
      {demoMode && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded-lg mb-4">
          <p className="font-medium">Demo Mode Active</p>
          <p className="text-sm">
            Using sample responses. For full features, please configure API keys in the backend.
          </p>
        </div>
      )}

      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-red-100 overflow-hidden">
        {/* Chat Header */}
        <div className="bg-gradient-to-r from-red-500 to-red-600 p-6 text-white">
          <div className="flex items-center space-x-3">
            <div className="bg-white/20 p-2 rounded-xl">
              <MessageCircle className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Food Chat Assistant</h2>
              <p className="text-red-100 text-sm">Ask me anything about food in {location}</p>
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <div className="h-96 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
                message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.sender === 'user'
                    ? 'bg-red-500 text-white'
                    : message.error
                    ? 'bg-red-100 text-red-600'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {message.sender === 'user' ? (
                  <User className="h-4 w-4" />
                ) : (
                  <Bot className="h-4 w-4" />
                )}
              </div>
              
              <div
                className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                  message.sender === 'user'
                    ? 'bg-red-500 text-white'
                    : message.error
                    ? 'bg-red-100 text-red-700 border border-red-200'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p className="text-sm leading-relaxed">{message.text}</p>
                <p
                  className={`text-xs mt-2 ${
                    message.sender === 'user' 
                      ? 'text-red-100' 
                      : message.error
                      ? 'text-red-500'
                      : 'text-gray-500'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  {message.error && (
                    <span className="ml-2">
                      <AlertCircle className="h-3 w-3 inline" />
                    </span>
                  )}
                </p>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                <Bot className="h-4 w-4" />
              </div>
              <div className="bg-gray-100 px-4 py-3 rounded-2xl">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestions */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-3">Quick suggestions:</p>
          <div className="flex flex-wrap gap-2">
            {quickSuggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSendMessage(suggestion)}
                disabled={isTyping}
                className="px-3 py-2 bg-white text-gray-700 rounded-xl text-sm hover:bg-red-50 hover:text-red-600 transition-colors duration-200 border border-gray-200 hover:border-red-200 disabled:opacity-50"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="p-6 bg-white border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="flex-1 relative">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about food recommendations, cuisines, or anything food-related..."
                className="w-full p-4 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none h-12 text-sm"
                rows={1}
                disabled={isTyping}
              />
            </div>
            <button
              onClick={() => handleSendMessage(inputText)}
              disabled={!inputText.trim() || isTyping}
              className="bg-gradient-to-r from-red-500 to-red-600 text-white p-3 rounded-2xl hover:shadow-lg transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isTyping ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Chat Features */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <FeatureCard 
          icon={<Sparkles className="h-5 w-5 text-red-500" />}
          iconBg="bg-red-100"
          title="Smart Recommendations"
          description="AI-powered food suggestions"
        />
        
        <FeatureCard 
          icon={<MessageCircle className="h-5 w-5 text-blue-500" />}
          iconBg="bg-blue-100"
          title="Natural Conversation"
          description="Chat naturally about food"
        />
        
        <FeatureCard 
          icon={<Bot className="h-5 w-5 text-green-500" />}
          iconBg="bg-green-100"
          title="24/7 Available"
          description="Always here to help"
        />
      </div>
    </div>
  );
};

interface FeatureCardProps {
  icon: React.ReactNode;
  iconBg: string;
  title: string;
  description: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ icon, iconBg, title, description }) => (
  <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 shadow-lg border border-red-100">
    <div className="flex items-center space-x-3">
      <div className={`${iconBg} p-2 rounded-xl`}>
        {icon}
      </div>
      <div>
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </div>
  </div>
);

export default ChatInterface;