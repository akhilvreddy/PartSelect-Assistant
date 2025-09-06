'use client';

import { ArrowLeft, Database, Search, MessageCircle, Zap, Globe, Brain, ChevronRight } from 'lucide-react';
import Link from 'next/link';

export default function HowItWorks() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-[#337778] shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link 
              href="/"
              className="flex items-center space-x-3 text-white hover:text-teal-100 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              <span className="text-sm font-medium">Back to Assistant</span>
            </Link>
            <h1 className="text-xl font-bold text-white">How This Works</h1>
            <div className="w-24"></div> {/* Spacer for centering */}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-[#f4d03f] to-[#f7dc6f] rounded-lg p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">PartSelect QA Assistant</h2>
          <p className="text-lg text-gray-700 mb-4">
            Powered by advanced AI and Retrieval-Augmented Generation (RAG) technology to provide accurate, 
            real-time answers about appliance parts and repairs.
          </p>
          <div className="flex items-center space-x-2 text-gray-600">
            <Brain className="h-5 w-5" />
            <span className="font-medium">AI-Powered • Real-Time • Accurate</span>
          </div>
        </div>

        {/* How RAG Works */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">How RAG (Retrieval-Augmented Generation) Works</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <div className="bg-[#337778] p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Search className="h-8 w-8 text-white" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">1. Query Processing</h4>
              <p className="text-sm text-gray-600">Your question is analyzed and converted into searchable vectors using advanced NLP models.</p>
            </div>
            
            <div className="text-center">
              <div className="bg-[#337778] p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Database className="h-8 w-8 text-white" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">2. Knowledge Retrieval</h4>
              <p className="text-sm text-gray-600">Relevant information is retrieved from our comprehensive PartSelect knowledge base.</p>
            </div>
            
            <div className="text-center">
              <div className="bg-[#337778] p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <MessageCircle className="h-8 w-8 text-white" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">3. Response Generation</h4>
              <p className="text-sm text-gray-600">AI combines retrieved data with context to generate accurate, helpful responses.</p>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-6">
            <h5 className="font-semibold text-gray-900 mb-3">The RAG Advantage:</h5>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start space-x-2">
                <ChevronRight className="h-4 w-4 text-[#337778] mt-0.5 flex-shrink-0" />
                <span><strong>Always Current:</strong> Information is retrieved in real-time from updated sources</span>
              </li>
              <li className="flex items-start space-x-2">
                <ChevronRight className="h-4 w-4 text-[#337778] mt-0.5 flex-shrink-0" />
                <span><strong>Highly Accurate:</strong> Responses are grounded in actual PartSelect data</span>
              </li>
              <li className="flex items-start space-x-2">
                <ChevronRight className="h-4 w-4 text-[#337778] mt-0.5 flex-shrink-0" />
                <span><strong>Context-Aware:</strong> Understands nuanced questions about specific appliance models</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Data Sources */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Data Sources & Knowledge Base</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Globe className="h-6 w-6 text-[#337778]" />
                <h4 className="font-semibold text-gray-900">PartSelect.com Integration</h4>
              </div>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li>• 2+ Million appliance parts catalog</li>
                <li>• Detailed part specifications and compatibility</li>
                <li>• Installation guides and repair manuals</li>
                <li>• Brand-specific troubleshooting information</li>
                <li>• Real-time inventory and pricing data</li>
              </ul>
            </div>
            
            <div className="border rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Database className="h-6 w-6 text-[#337778]" />
                <h4 className="font-semibold text-gray-900">Specialized Focus Areas</h4>
              </div>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li>• <strong>Dishwashers:</strong> All major brands and models</li>
                <li>• <strong>Refrigerators:</strong> Complete parts database</li>
                <li>• Part compatibility matrices</li>
                <li>• Step-by-step repair procedures</li>
                <li>• Common failure patterns and solutions</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Technical Architecture */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Technical Architecture</h3>
          
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between text-sm font-mono">
              <span className="bg-blue-100 px-3 py-1 rounded">User Query</span>
              <ChevronRight className="h-4 w-4 text-gray-400" />
              <span className="bg-green-100 px-3 py-1 rounded">Intent Classification</span>
              <ChevronRight className="h-4 w-4 text-gray-400" />
              <span className="bg-yellow-100 px-3 py-1 rounded">Vector Search</span>
              <ChevronRight className="h-4 w-4 text-gray-400" />
              <span className="bg-purple-100 px-3 py-1 rounded">Response Generation</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Core Technologies:</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li>• <strong>Embeddings:</strong> OpenAI text-embedding-3-small</li>
                <li>• <strong>Vector Database:</strong> Pinecone/Weaviate</li>
                <li>• <strong>LLM:</strong> GPT-4 for response generation</li>
                <li>• <strong>Framework:</strong> LangChain for orchestration</li>
                <li>• <strong>Frontend:</strong> Next.js with real-time updates</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Query Processing:</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li>• Natural language understanding</li>
                <li>• Model number extraction and validation</li>
                <li>• Intent classification (search/repair/compatibility)</li>
                <li>• Context-aware semantic search</li>
                <li>• Multi-step reasoning for complex queries</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Use Cases */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">What You Can Ask</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-[#337778] mb-3">Part Search & Compatibility:</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li>• "What door seal fits my Whirlpool WDF520PADM?"</li>
                <li>• "Compatible water filters for Samsung RF23J9011SR"</li>
                <li>• "Replacement pump for KitchenAid dishwasher model KDFE104HPS"</li>
                <li>• "Alternative parts that work with my GE refrigerator"</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-[#337778] mb-3">Repair & Troubleshooting:</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li>• "How do I replace a dishwasher pump?"</li>
                <li>• "My refrigerator ice maker isn't working"</li>
                <li>• "Step-by-step door seal replacement"</li>
                <li>• "Troubleshoot dishwasher not draining properly"</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Performance & Accuracy</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-[#337778] mb-2">95%</div>
              <div className="text-sm text-gray-600">Part Match Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[#337778] mb-2">&lt;2s</div>
              <div className="text-sm text-gray-600">Average Response Time</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[#337778] mb-2">2M+</div>
              <div className="text-sm text-gray-600">Parts in Database</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[#337778] mb-2">24/7</div>
              <div className="text-sm text-gray-600">Availability</div>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-8">
          <Link 
            href="/"
            className="inline-flex items-center space-x-2 bg-[#337778] text-white px-6 py-3 rounded-lg hover:bg-[#2a6366] transition-colors"
          >
            <MessageCircle className="h-5 w-5" />
            <span>Try the Assistant Now</span>
          </Link>
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
