'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, MessageCircle, Wrench, ExternalLink, Info, ChevronDown, Bot } from 'lucide-react';
import Link from 'next/link';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your PartSelect QA Assistant. I can help you find dishwasher and refrigerator parts, provide repair guidance, and answer technical questions. What can I help you with today?',
      isUser: false,
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('DeepSeek Chat');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const models = [
    { name: 'DeepSeek Chat', description: 'Fast & Efficient' }
  ];

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      // removed chat.ts just for simplicity -> make the API call right here async
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: currentInput,
          model: selectedModel === 'DeepSeek Chat' ? 'deepseek-chat' : 'deepseek-reasoning'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: data.response || data.message || 'I received your message but got an unexpected response format.',
          isUser: false,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, aiResponse]);
      } else {
        const errorResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: `Sorry, I encountered an error (HTTP ${response.status}). Please try again or check if the backend is running.`,
          isUser: false,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorResponse]);
      }
    } catch (error) {
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: `Sorry, I couldn't connect to the backend. Please make sure the API server is running on localhost:8000. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-[#337778] shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="grid grid-cols-3 items-center">
            {/* Left: Model Selector */}
            <div className="flex justify-start">
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center space-x-2 bg-white/10 hover:bg-white/20 px-3 py-2 rounded-lg transition-colors"
                  title="Select AI Model"
                >
                  <Bot className="h-4 w-4 text-white" />
                  <span className="text-sm font-medium text-white">{selectedModel}</span>
                  <ChevronDown className={`h-4 w-4 text-white transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
                </button>
                
                {isDropdownOpen && (
                  <div className="absolute top-full left-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-50">
                    {models.map((model) => (
                      <button
                        key={model.name}
                        onClick={() => {
                          setSelectedModel(model.name);
                          setIsDropdownOpen(false);
                        }}
                        className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors ${
                          selectedModel === model.name ? 'bg-gray-50' : ''
                        } ${model.name === models[0].name ? 'rounded-t-lg' : ''} ${
                          model.name === models[models.length - 1].name ? 'rounded-b-lg' : ''
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <Bot className={`h-4 w-4 ${selectedModel === model.name ? 'text-[#337778]' : 'text-gray-400'}`} />
                          <div>
                            <div className={`text-sm font-medium ${selectedModel === model.name ? 'text-[#337778]' : 'text-gray-900'}`}>
                              {model.name}
                            </div>
                            <div className="text-xs text-gray-500">{model.description}</div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Center: Logo and Title (Fixed) */}
            <div className="flex items-center justify-center space-x-3">
              <div className="bg-white p-2 rounded-lg">
                <Wrench className="h-6 w-6 text-[#337778]" />
              </div>
              <div className="text-center">
                <h1 className="text-2xl font-bold text-white">PartSelect.com Q&A Assistant</h1>
                <p className="text-sm text-teal-100">Dishwasher & Refrigerator Parts Expert</p>
              </div>
            </div>

            {/* Right: Navigation Links */}
            <div className="flex items-center justify-end space-x-4">
              <Link 
                href="/test-api"
                className="flex items-center space-x-2 text-white hover:text-teal-100 transition-colors"
                title="Test the API connection"
              >
                <span className="text-sm font-medium">Test API</span>
                <Info className="h-4 w-4" />
              </Link>
              <div className="text-white/30 text-lg">|</div>
              <a 
                href="https://www.partselect.com/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-white hover:text-teal-100 transition-colors"
                title="Visit PartSelect.com"
              >
                <span className="text-sm font-medium">Visit PartSelect.com</span>
                <ExternalLink className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Features Section */}
        <div className="bg-gradient-to-r from-[#f4d03f] to-[#f7dc6f] rounded-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">How I Can Help You</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center space-x-3 mb-3">
                <Search className="h-5 w-5 text-[#337778]" />
                <h3 className="font-semibold text-gray-900">Smart Part Search</h3>
              </div>
              <p className="text-gray-600 text-sm">Find exact replacement parts using natural language queries</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center space-x-3 mb-3">
                <MessageCircle className="h-5 w-5 text-[#337778]" />
                <h3 className="font-semibold text-gray-900">Repair Guidance</h3>
              </div>
              <p className="text-gray-600 text-sm">Get step-by-step installation and repair instructions</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center space-x-3 mb-3">
                <Wrench className="h-5 w-5 text-[#337778]" />
                <h3 className="font-semibold text-gray-900">Compatibility Check</h3>
              </div>
              <p className="text-gray-600 text-sm">Verify part compatibility with your appliance model</p>
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="bg-white rounded-lg shadow-lg border overflow-hidden">
          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.isUser
                      ? 'bg-[#337778] text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <p className={`text-xs mt-1 ${
                    message.isUser ? 'text-teal-200' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 px-4 py-2 rounded-lg">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex space-x-3">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about dishwasher or refrigerator parts, repairs, or compatibility..."
                className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#337778] focus:border-transparent text-gray-900 placeholder-gray-500"
                rows={2}
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="bg-[#337778] text-white px-6 py-2 rounded-lg hover:bg-[#2a6366] focus:outline-none focus:ring-2 focus:ring-[#337778] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Example Queries */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Try asking about:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              "How much is a dishwasher drain pump (120v 60hz)?",
              "How can I install part number PS11752778?",
              "Is this part (PS10065979) compatible with my WDT780SAEM1 model?",
              "The ice maker on my Whirlpool fridge is not working. How can I fix it?",
            ].map((query, index) => (
              <button
                key={index}
                onClick={() => setInput(query)}
                className="text-left p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-sm text-gray-700"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      </main>


      {/* Footer */}
      <footer className="mt-16 bg-[#337778] border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-white mb-2">
              PartSelect QA Assistant - RAG powered appliance parts support
            </p>
            <p className="text-sm text-teal-100">
              By Akhil Reddy | Frontend built with Next.js & Tailwind CSS
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}