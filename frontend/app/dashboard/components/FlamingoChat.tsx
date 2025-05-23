// frontend/app/dashboard/components/FlamingoChat.tsx
import { FiSend, FiMessageSquare, FiUser, FiHelpCircle } from 'react-icons/fi';
import { useState, useRef, useEffect } from 'react';

type Message = {
  id: string;
  text: string;
  sender: 'user' | 'flamingo';
  timestamp: Date;
};

export default function FlamingoChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi there! I'm Flamingo, your AI code review assistant. 🦩 How can I help you with your Python code today?",
      sender: 'flamingo',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = () => {
    if (inputValue.trim() === '') return;

    const newUserMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputValue('');

    // Simulate AI response
    setTimeout(() => {
      const aiResponses = [
        "I'd recommend using list comprehensions here for better readability and performance.",
        "This pattern looks good, but have you considered adding error handling?",
        "That's an interesting approach! Here's a similar example from our docs...",
        "I've detected a potential security concern in this code. Let me explain...",
        "Great question! This is a common Python pattern. The key thing to remember is..."
      ];
      
      const randomResponse = aiResponses[Math.floor(Math.random() * aiResponses.length)];
      
      const newAiMessage: Message = {
        id: Date.now().toString(),
        text: randomResponse,
        sender: 'flamingo',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, newAiMessage]);
    }, 1000 + Math.random() * 2000);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <span className="text-pink-400">🦩</span> Flamingo Chat
          </h2>
          <p className="text-gray-400">Ask me anything about your code or best practices</p>
        </div>
        <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg flex items-center gap-2">
          <FiHelpCircle /> Help
        </button>
      </div>

      <div className="flex-1 bg-gray-800 rounded-xl border border-gray-700 p-4 flex flex-col">
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[80%] rounded-lg p-3 ${message.sender === 'user' 
                  ? 'bg-pink-600/20 border border-pink-600/30' 
                  : 'bg-gray-700/50 border border-gray-600'}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {message.sender === 'user' ? (
                    <FiUser className="text-pink-400" />
                  ) : (
                    <span className="text-pink-400">🦩</span>
                  )}
                  <span className="text-xs text-gray-400">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p>{message.text}</p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask Flamingo about your code..."
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim()}
            className={`p-2 rounded-lg ${inputValue.trim() 
              ? 'bg-pink-600 hover:bg-pink-700 text-white' 
              : 'bg-gray-700 text-gray-500'}`}
          >
            <FiSend />
          </button>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <button 
          onClick={() => setInputValue("Can you explain this error in my code?")}
          className="bg-gray-800 hover:bg-gray-700 p-3 rounded-lg border border-gray-700 text-sm text-left"
        >
          <span className="text-pink-400">Explain error</span> in my code
        </button>
        <button 
          onClick={() => setInputValue("How can I improve this function's performance?")}
          className="bg-gray-800 hover:bg-gray-700 p-3 rounded-lg border border-gray-700 text-sm text-left"
        >
          Improve <span className="text-pink-400">performance</span>
        </button>
        <button 
          onClick={() => setInputValue("Show me a more Pythonic way to write this")}
          className="bg-gray-800 hover:bg-gray-700 p-3 rounded-lg border border-gray-700 text-sm text-left"
        >
          More <span className="text-pink-400">Pythonic</span> solution
        </button>
        <button 
          onClick={() => setInputValue("What's the security risk in this code?")}
          className="bg-gray-800 hover:bg-gray-700 p-3 rounded-lg border border-gray-700 text-sm text-left"
        >
          Identify <span className="text-pink-400">security</span> risks
        </button>
      </div>
    </div>
  );
}