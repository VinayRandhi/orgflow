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

  // Sample chat history data
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([
    {
      id: '2',
      title: 'Document Review',
      lastMessage: 'Q&A about Q2 Strategy Document',
      timestamp: new Date('2024-03-19T15:45:00'),
      unread: false,
    },
    {
      id: '3',
      title: 'Team Meeting Notes',
      lastMessage: 'Q2 Planning Meeting Summary',
      timestamp: new Date('2024-03-18T09:15:00'),
      unread: false,
    },
  ]);

  // Select the most recent chat by default when component loads
  useEffect(() => {
    if (chatHistory.length > 0 && !selectedChatId) {
      handleChatSelect(chatHistory[0].id);
    }
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
          "Checking team members' availability",
          "Identifying potential time slots",
          "Verifying meeting requirements",
          "Preparing response options"
        ],
        conclusion: "Based on the analysis, I'll present available meeting slots that accommodate all team members."
      }
    };
    setMessages((prev) => [...prev, thinkingMessage]);

    // Simulate AI processing
    setTimeout(() => {
      if (input.toLowerCase().includes('schedule') && input.toLowerCase().includes('meeting')) {
        // Remove thinking message
        setMessages((prev) => prev.filter(msg => msg.id !== thinkingMessage.id));
        
        // Add meeting slots response
        const aiMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: "I've analyzed the team's calendars and found the following available time slots for all team members:",
          role: 'assistant',
          timestamp: new Date(),
          type: 'meeting_slots',
          thoughtProcess: {
            steps: [
              "Identified key team members from the request",
              "Checked calendar availability for the next 5 business days",
              "Filtered out times with conflicts",
              "Ensured minimum 1-hour duration for meaningful discussion",
              "Verified all required attendees are available"
            ],
            conclusion: "Found 3 optimal time slots that work for all team members."
          },
          meetingSlots: [
            {
              id: '1',
              date: '2024-03-25',
              time: '10:00 AM',
              duration: '1 hour',
              availableAttendees: ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Emma Davis'],
            },
            {
              id: '2',
              date: '2024-03-25',
              time: '2:00 PM',
              duration: '1 hour',
              availableAttendees: ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Emma Davis'],
            },
            {
              id: '3',
              date: '2024-03-26',
              time: '11:00 AM',
              duration: '1 hour',
              availableAttendees: ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Emma Davis'],
            },
          ],
        };
        setMessages((prev) => [...prev, aiMessage]);
      } else {
        // Remove thinking message
        setMessages((prev) => prev.filter(msg => msg.id !== thinkingMessage.id));
        
        // Default response for other queries
        const aiMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: "I understand you're asking about something. Let me help you with that. Could you please provide more details about what you'd like to know?",
          role: 'assistant',
          timestamp: new Date(),
          type: 'text',
          thoughtProcess: {
            steps: [
              "Analyzed the query for specific requirements",
              "Checked knowledge base for relevant information",
              "Identified need for more context",
              "Prepared follow-up questions"
            ],
            conclusion: "Need more specific information to provide a detailed response."
          }
        };
        setMessages((prev) => [...prev, aiMessage]);
      }
    }, 2000);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setUploadedFiles((prev) => [...prev, ...files]);
  };

  const handleRemoveFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // Function to handle chat deletion
  const handleDeleteChat = (chatId: string) => {
    if (window.confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
      setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
      if (selectedChatId === chatId) {
        setSelectedChatId(null);
        setMessages([]);
      }
    }
  };

  // Function to create a new chat
  const createNewChat = () => {
    const newChatId = Date.now().toString();
    const newChat: ChatHistory = {
      id: newChatId,
      title: 'New Chat',
      lastMessage: 'Started a new conversation',
      timestamp: new Date(),
      unread: false,
    };
    
    setChatHistory(prev => [newChat, ...prev]);
    setSelectedChatId(newChatId);
    setMessages([{
      id: '1',
      content: 'Hello! I can help you schedule meetings, manage tasks, or answer questions about documents. Try typing something like "I need to schedule a meeting with the team to discuss the Q2 roadmap."',
      role: 'assistant',
      timestamp: new Date(),
      type: 'text',
    }]);
  };

  // Function to handle chat selection
  const handleChatSelect = (chatId: string) => {
    setSelectedChatId(chatId);
    // Clear existing messages
    setMessages([]);

    // Load chat history based on selection
    switch (chatId) {
      case '2': // Document Review
        setMessages([
          {
            id: '1',
            content: 'I\'ve reviewed the Q2 Strategy Document. What would you like to know about it?',
            role: 'assistant',
            timestamp: new Date(),
            type: 'text',
          },
          {
            id: '2',
            content: 'What are the key initiatives planned for Q2?',
            role: 'user',
            timestamp: new Date(),
            type: 'text',
          },
          {
            id: '3',
            content: "Let me analyze the document and provide you with the key initiatives.",
            role: 'assistant',
            timestamp: new Date(),
            type: 'thinking',
            thoughtProcess: {
              steps: [
                "Scanning document for key initiatives section",
                "Identifying main project categories",
                "Extracting timeline information",
                "Verifying resource allocation",
                "Preparing structured response"
              ],
              conclusion: "Found three major initiatives with detailed planning information."
            }
          },
          {
            id: '4',
            content: 'Based on the document, there are three key initiatives planned for Q2:\n\n1. Product Launch: New AI-powered analytics dashboard\n2. Market Expansion: Entry into European markets\n3. Infrastructure Upgrade: Migration to cloud-native architecture\n\nWould you like more details about any of these initiatives?',
            role: 'assistant',
            timestamp: new Date(),
            type: 'text',
          },
          {
            id: '5',
            content: 'What\'s the timeline for the product launch?',
            role: 'user',
            timestamp: new Date(),
            type: 'text',
          },
          {
            id: '6',
            content: "I'll check the specific timeline details for the product launch.",
            role: 'assistant',
            timestamp: new Date(),
            type: 'thinking',
            thoughtProcess: {
              steps: [
                "Locating product launch section in document",
                "Extracting timeline milestones",
                "Verifying dependencies",
                "Checking resource allocation",
                "Preparing detailed timeline response"
              ],
              conclusion: "Found comprehensive timeline with specific dates and milestones."
            }
          },
          {
            id: '7',
            content: 'According to the document, the product launch is scheduled for May 15th, 2024. The timeline includes:\n\n- April 1-15: Beta testing\n- April 16-30: Feedback incorporation\n- May 1-14: Final testing and preparation\n- May 15: Official launch\n\nThe document also mentions that we\'re targeting 10,000 active users within the first month of launch.',
            role: 'assistant',
            timestamp: new Date(),
            type: 'text',
          }
        ]);
        break;

      case '3': // Team Meeting Notes
        setMessages([
          {
            id: '1',
            content: 'Here\'s the summary of our Q2 Planning Meeting:\n\n1. Project Timeline Review\n2. Resource Allocation\n3. Risk Assessment\n4. Action Items\n\nWould you like me to elaborate on any of these sections?',
            role: 'assistant',
            timestamp: new Date(),
            type: 'text',
          },
          {
            id: '2',
            content: 'Can you show me the action items?',
            role: 'user',
            timestamp: new Date(),
            type: 'text',
          },
          {
            id: '3',
            content: "I'll analyze the meeting notes to extract the action items.",
            role: 'assistant',
            timestamp: new Date(),
            type: 'thinking',
            thoughtProcess: {
              steps: [
                "Reviewing meeting transcript",
                "Identifying action items and owners",
                "Extracting deadlines and priorities",
                "Verifying task dependencies",
                "Preparing structured task list"
              ],
              conclusion: "Found four key action items with clear priorities and deadlines."
            }
          },
          {
            id: '4',
            content: 'Here are the key action items from the meeting:\n\n1. Finalize Q2 roadmap by March 25th (High Priority)\n2. Complete resource allocation matrix by March 22nd (Medium Priority)\n3. Schedule stakeholder review meeting by March 28th (High Priority)\n4. Update risk assessment document by March 30th (Medium Priority)\n\nWould you like me to add these to your tasks?',
            role: 'assistant',
            timestamp: new Date(),
            type: 'text',
          },
          {
            id: '5',
            content: 'Yes, please add them to my tasks.',
            role: 'user',
            timestamp: new Date(),
            type: 'text',
          },
          {
            id: '6',
            content: "I'll process these tasks and add them to your dashboard.",
            role: 'assistant',
            timestamp: new Date(),
            type: 'thinking',
            thoughtProcess: {
              steps: [
                "Verifying task details",
                "Setting up task priorities",
                "Configuring deadlines",
                "Assigning tasks to you",
                "Preparing dashboard update"
              ],
              conclusion: "Successfully processed all tasks for dashboard integration."
            }
          },
          {
            id: '7',
            content: 'I\'ve added the following tasks to your dashboard:\n\n1. Finalize Q2 roadmap\n   - Priority: High\n   - Deadline: March 25th, 2024\n   - Assigned: You\n\n2. Complete resource allocation matrix\n   - Priority: Medium\n   - Deadline: March 22nd, 2024\n   - Assigned: You\n\n3. Schedule stakeholder review meeting\n   - Priority: High\n   - Deadline: March 28th, 2024\n   - Assigned: You\n\n4. Update risk assessment document\n   - Priority: Medium\n   - Deadline: March 30th, 2024\n   - Assigned: You\n\nYou can view and manage these tasks in your dashboard. Would you like me to show you the detailed notes for any other sections?',
            role: 'assistant',
            timestamp: new Date(),
            type: 'text',
          }
        ]);
        break;

      default:
        setMessages([
          {
            id: '1',
            content: 'Hello! I can help you with various tasks like scheduling meetings, organizing documents, and answering questions about your organization. How can I assist you today?',
            role: 'assistant',
            timestamp: new Date(),
            type: 'text',
          }
        ]);
    }
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
              >
                {isHistoryCollapsed ? (
                  <MessageSquare className={`h-5 w-5 ${selectedChatId === chat.id ? 'text-blue-600' : 'text-gray-500'}`} />
                ) : (
                  <div className="flex items-center justify-between">
                    <div 
                      className="flex-1"
                      onClick={() => handleChatSelect(chat.id)}
                    >
                      <div className="flex items-center justify-between">
                        <h3 className={`font-medium ${selectedChatId === chat.id ? 'text-blue-900' : 'text-gray-900'}`}>
                          {chat.title}
                        </h3>
                        {chat.unread && (
                          <span className="h-2 w-2 bg-blue-600 rounded-full" />
                        )}
                      </div>
                      <p className={`text-sm mt-1 truncate ${selectedChatId === chat.id ? 'text-blue-800' : 'text-gray-500'}`}>
                        {chat.lastMessage}
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
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
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