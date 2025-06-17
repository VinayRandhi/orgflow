'use client';

import { FC, useState, useRef, useEffect } from 'react';
import { Send, Upload, FileText, X, Bot, User, Calendar, Clock, Users, Check, X as XIcon, Brain, Search, CheckCircle, ChevronLeft, ChevronRight, MessageSquare, Plus } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  type: 'text' | 'meeting_slots' | 'confirmation' | 'thinking';
  meetingSlots?: {
    id: string;
    date: string;
    time: string;
    duration: string;
    availableAttendees: string[];
  }[];
  selectedSlot?: {
    id: string;
    date: string;
    time: string;
    duration: string;
    attendees: string[];
  };
  thoughtProcess?: {
    steps: string[];
    conclusion: string;
    agents?: {
      name: string;
      type: string;
      role: string;
      status: 'success' | 'error' | 'pending';
    }[];
  };
}

interface ChatHistory {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  unread: boolean;
}

const styles = `
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fade-in {
    animation: fadeIn 0.3s ease-out forwards;
  }
`;

const ChatPage: FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isHistoryCollapsed, setIsHistoryCollapsed] = useState(false);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize with empty chat history
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);

  // Create a new chat when component loads
  useEffect(() => {
    createNewChat();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const styleSheet = document.createElement("style");
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
    return () => {
      document.head.removeChild(styleSheet);
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: 'user',
      timestamp: new Date(),
      type: 'text',
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    // Add thinking message
    const thinkingMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: "Analyzing your request...",
      role: 'assistant',
      timestamp: new Date(),
      type: 'thinking',
      thoughtProcess: {
        steps: [
          "Analyzing the request type and context",
          "Determining the appropriate agent to handle the query",
          "Processing the request",
          "Generating a response"
        ],
        conclusion: "Processing your request...",
        agents: [
          {
            name: "Query Classifier",
            type: "LLM",
            role: "Determines which agents should handle the query",
            status: "pending"
          }
        ]
      }
    };
    setMessages((prev) => [...prev, thinkingMessage]);

    try {
      // Call the orchestrator API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const result = await response.json();

      // Remove thinking message
      setMessages((prev) => prev.filter(msg => msg.id !== thinkingMessage.id));

      // Add AI response
      const aiMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: result.response,
        role: 'assistant',
        timestamp: new Date(),
        type: 'text',
        thoughtProcess: {
          steps: [
            `Query classified as: ${result.agent_types.join(', ')}`,
            `Processed by: ${result.agents_used.join(', ')}`,
            `Response generated successfully`
          ],
          conclusion: `Successfully processed your request using ${result.agents_used.join(', ')}`,
          agents: result.agent_results.map((agent: { agent_name: string; agent_type: string; result: { success: boolean } }) => ({
            name: agent.agent_name,
            type: agent.agent_type,
            role: agent.agent_type === 'rag' ? 'Knowledge Base Search' : 'Web Search',
            status: agent.result.success ? 'success' : 'error'
          }))
        }
      };
      setMessages((prev) => [...prev, aiMessage]);

      // Update chat history with the latest message
      if (selectedChatId) {
        setChatHistory(prev => prev.map(chat => 
          chat.id === selectedChatId 
            ? {
                ...chat,
                lastMessage: input,
                timestamp: new Date()
              }
            : chat
        ));
      }

    } catch (error) {
      console.error('Error:', error);
      // Remove thinking message
      setMessages((prev) => prev.filter(msg => msg.id !== thinkingMessage.id));
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: "I apologize, but I encountered an error while processing your request. Please try again.",
        role: 'assistant',
        timestamp: new Date(),
        type: 'text',
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setUploadedFiles((prev) => [...prev, ...files]);
  };

  const handleRemoveFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleDeleteChat = (chatId: string) => {
    // Prevent event propagation to avoid triggering chat selection
    event?.stopPropagation();
    
    // Remove the chat from history
    setChatHistory((prev) => prev.filter((chat) => chat.id !== chatId));
    
    // If the deleted chat was selected, create a new chat
    if (selectedChatId === chatId) {
      createNewChat();
    }
  };

  const createNewChat = () => {
    const newChatId = Date.now().toString();
    const newChat: ChatHistory = {
      id: newChatId,
      title: 'New Chat',
      lastMessage: '',
      timestamp: new Date(),
      unread: false,
    };
    setChatHistory((prev) => [newChat, ...prev]);
    setSelectedChatId(newChatId);
    setMessages([]);
  };

  const handleChatSelect = (chatId: string) => {
    setSelectedChatId(chatId);
    setMessages([]);
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex">
      {/* Chat History Sidebar */}
      <div
        className={`bg-white border-r border-gray-200 transition-all duration-300 ease-in-out ${
          isHistoryCollapsed ? 'w-16' : 'w-80'
        }`}
      >
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          {!isHistoryCollapsed && (
            <h2 className="text-lg font-semibold text-gray-900">Chat History</h2>
          )}
          <button
            onClick={() => setIsHistoryCollapsed(!isHistoryCollapsed)}
            className="p-1 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
          >
            {isHistoryCollapsed ? (
              <ChevronRight className="h-5 w-5 text-gray-500" />
            ) : (
              <ChevronLeft className="h-5 w-5 text-gray-500" />
            )}
          </button>
        </div>
        <div className="p-4">
          {!isHistoryCollapsed && (
            <button 
              onClick={createNewChat}
              className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <Plus className="h-5 w-5 mr-2" />
              New Chat
            </button>
          )}
          <div className="mt-4 space-y-2">
            {chatHistory.map((chat) => (
              <div
                key={chat.id}
                className={`p-3 rounded-lg cursor-pointer transition-all duration-300 ease-in-out transform ${
                  selectedChatId === chat.id 
                    ? 'bg-blue-100 border border-blue-200 scale-[1.02]' 
                    : chat.unread 
                      ? 'bg-blue-50' 
                      : 'hover:bg-gray-50'
                }`}
                onClick={() => handleChatSelect(chat.id)}
              >
                {isHistoryCollapsed ? (
                  <MessageSquare className={`h-5 w-5 ${selectedChatId === chat.id ? 'text-blue-600' : 'text-gray-500'}`} />
                ) : (
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className={`font-medium ${selectedChatId === chat.id ? 'text-blue-900' : 'text-gray-900'}`}>
                          {chat.title}
                        </h3>
                        {chat.unread && (
                          <span className="h-2 w-2 bg-blue-600 rounded-full" />
                        )}
                      </div>
                      <p className={`text-sm mt-1 truncate ${selectedChatId === chat.id ? 'text-blue-800' : 'text-gray-500'}`}>
                        {chat.lastMessage || 'No messages yet'}
                      </p>
                      <p className={`text-xs mt-1 ${selectedChatId === chat.id ? 'text-blue-600' : 'text-gray-400'}`}>
                        {chat.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteChat(chat.id);
                      }}
                      className="ml-2 p-1 text-gray-400 hover:text-red-500 rounded-full hover:bg-gray-100 transition-colors duration-200"
                      title="Delete chat"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages Area - Scrollable */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                } animate-fade-in`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div
                  className={`max-w-2xl rounded-lg p-4 transition-all duration-300 ease-in-out transform ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    {message.role === 'assistant' ? (
                      <Bot className="h-5 w-5 mr-2" />
                    ) : (
                      <User className="h-5 w-5 mr-2" />
                    )}
                    <span className="font-medium">
                      {message.role === 'assistant' ? 'Assistant' : 'You'}
                    </span>
                  </div>
                  
                  {message.type === 'text' && (
                    <div className="space-y-3">
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      {message.thoughtProcess && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <div className="flex items-center text-sm text-gray-500 mb-2">
                            <Brain className="h-4 w-4 mr-2" />
                            <span>AI Thought Process:</span>
                          </div>
                          <ul className="space-y-2 text-sm">
                            {message.thoughtProcess.steps.map((step, index) => (
                              <li key={index} className="flex items-start">
                                <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                                <span>{step}</span>
                              </li>
                            ))}
                          </ul>
                          {message.thoughtProcess.agents && (
                            <div className="mt-4">
                              <h4 className="text-sm font-medium text-gray-700 mb-2">Agents Used:</h4>
                              <div className="space-y-2">
                                {message.thoughtProcess.agents.map((agent, index) => (
                                  <div key={index} className="flex items-start p-2 bg-gray-50 rounded-lg">
                                    <div className="flex-1">
                                      <div className="flex items-center">
                                        <span className="font-medium text-gray-900">{agent.name}</span>
                                        <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                                          agent.status === 'success' ? 'bg-green-100 text-green-800' :
                                          agent.status === 'error' ? 'bg-red-100 text-red-800' :
                                          'bg-yellow-100 text-yellow-800'
                                        }`}>
                                          {agent.status}
                                        </span>
                                      </div>
                                      <p className="text-sm text-gray-600 mt-1">{agent.role}</p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          <div className="mt-3 text-sm font-medium text-gray-700">
                            {message.thoughtProcess.conclusion}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {message.type === 'thinking' && (
                    <div className="space-y-3">
                      <div className="flex items-center text-blue-600">
                        <Brain className="h-5 w-5 mr-2 animate-pulse" />
                        <span>Thinking...</span>
                      </div>
                      <div className="space-y-2">
                        {message.thoughtProcess?.steps.map((step, index) => (
                          <div key={index} className="flex items-center text-sm text-gray-600">
                            <Search className="h-4 w-4 mr-2" />
                            <span>{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {message.type === 'meeting_slots' && (
                    <div className="space-y-4">
                      <div className="space-y-3">
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        {message.thoughtProcess && (
                          <div className="bg-blue-50 rounded-lg p-3 text-sm">
                            <div className="flex items-center text-blue-700 mb-2">
                              <Brain className="h-4 w-4 mr-2" />
                              <span>Analysis Process:</span>
                            </div>
                            <ul className="space-y-1">
                              {message.thoughtProcess.steps.map((step, index) => (
                                <li key={index} className="flex items-start">
                                  <CheckCircle className="h-4 w-4 text-blue-500 mr-2 mt-0.5" />
                                  <span className="text-blue-800">{step}</span>
                                </li>
                              ))}
                            </ul>
                            <div className="mt-2 text-blue-700 font-medium">
                              {message.thoughtProcess.conclusion}
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="space-y-3">
                        {message.meetingSlots?.map((slot) => (
                          <div
                            key={slot.id}
                            className="bg-white rounded-lg p-4 border border-gray-200"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <Calendar className="h-5 w-5 text-blue-600" />
                                <span className="font-medium">{slot.date}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Clock className="h-4 w-4 text-gray-400" />
                                <span className="text-sm text-gray-500">
                                  {slot.time} ({slot.duration})
                                </span>
                              </div>
                            </div>
                            <div className="mt-3">
                              <div className="flex items-center text-sm text-gray-500">
                                <Users className="h-4 w-4 mr-2" />
                                <span>
                                  {slot.availableAttendees.length} attendees available
                                </span>
                              </div>
                              <div className="mt-2 flex flex-wrap gap-2">
                                {slot.availableAttendees.map((attendee) => (
                                  <span
                                    key={attendee}
                                    className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                                  >
                                    {attendee}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <button 
                              onClick={() => {
                                const confirmationMessage: Message = {
                                  id: Date.now().toString(),
                                  content: `I've scheduled the meeting for ${slot.date} at ${slot.time} (${slot.duration}). I'll send calendar invites to all attendees.`,
                                  role: 'assistant',
                                  timestamp: new Date(),
                                  type: 'confirmation',
                                  selectedSlot: {
                                    ...slot,
                                    attendees: slot.availableAttendees,
                                  },
                                };
                                setMessages((prev) => [...prev, confirmationMessage]);
                              }}
                              className="mt-3 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                            >
                              Select Time Slot
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {message.type === 'confirmation' && message.selectedSlot && (
                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="flex items-center text-green-700 mb-2">
                        <Check className="h-5 w-5 mr-2" />
                        <span className="font-medium">Meeting Scheduled!</span>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm text-green-800">
                          Date: {message.selectedSlot.date}
                        </p>
                        <p className="text-sm text-green-800">
                          Time: {message.selectedSlot.time} ({message.selectedSlot.duration})
                        </p>
                        <div className="mt-2">
                          <p className="text-sm font-medium text-green-800">Attendees:</p>
                          <div className="mt-1 flex flex-wrap gap-2">
                            {message.selectedSlot.attendees.map((attendee) => (
                              <span
                                key={attendee}
                                className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                              >
                                {attendee}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* File Uploads */}
        {uploadedFiles.length > 0 && (
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="flex flex-wrap gap-2">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-1"
                >
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-700">{file.name}</span>
                  <button
                    onClick={() => handleRemoveFile(index)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="flex items-center space-x-4">
            <label className="cursor-pointer">
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                className="hidden"
              />
              <Upload className="h-5 w-5 text-gray-500 hover:text-gray-700" />
            </label>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder={selectedChatId === null ? "Try typing something like 'I need to schedule a meeting with the team to discuss the Q2 roadmap.'" : "Type your message..."}
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-500"
            />
            <button
              onClick={handleSend}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage; 