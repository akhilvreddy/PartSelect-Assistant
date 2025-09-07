'use client';

import { useState } from 'react';
import { ArrowLeft, Check, X, Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function TestAPI() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [result, setResult] = useState<string>('');

  const testHealthEndpoint = async () => {
    setStatus('loading');
    setResult('');

    try {
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.text();
        if (data.toLowerCase().includes('ok') || response.status === 200) {
          setStatus('success');
          setResult('All functionality is working! API is up and running.');
        } else {
          setStatus('error');
          setResult('Error: Unexpected response from API');
        }
      } else {
        setStatus('error');
        setResult(`Error: HTTP ${response.status} - ${response.statusText}`);
      }
    } catch (error) {
      setStatus('error');
      setResult(`Error: ${error instanceof Error ? error.message : 'Failed to connect to API'}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-[#337778] shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <Link 
              href="/"
              className="flex items-center space-x-2 text-white hover:text-teal-100 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              <span className="text-sm font-medium">Back to Home</span>
            </Link>
            <div className="text-white/30 text-lg">|</div>
            <h1 className="text-xl font-bold text-white">API Health Test</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-lg border p-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Test Backend API Connection
            </h2>
            <p className="text-gray-600 mb-8">
              Click the button below to test the connection to the backend API health endpoint.
            </p>

            {/* Test Button */}
            <button
              onClick={testHealthEndpoint}
              disabled={status === 'loading'}
              className="inline-flex items-center px-8 py-3 bg-[#337778] text-white font-medium rounded-lg hover:bg-[#2a6366] disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md mb-8"
            >
              {status === 'loading' ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Testing...
                </>
              ) : (
                'Test Health Endpoint'
              )}
            </button>

            {/* Result Display */}
            {status !== 'idle' && (
              <div className="mt-8">
                <div className={`p-6 rounded-lg border ${
                  status === 'success' 
                    ? 'bg-green-50 border-green-200' 
                    : status === 'error'
                    ? 'bg-red-50 border-red-200'
                    : 'bg-blue-50 border-blue-200'
                }`}>
                  <div className="flex items-center justify-center space-x-3 mb-3">
                    {status === 'success' && (
                      <Check className="h-6 w-6 text-green-600" />
                    )}
                    {status === 'error' && (
                      <X className="h-6 w-6 text-red-600" />
                    )}
                    {status === 'loading' && (
                      <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
                    )}
                    <h3 className={`text-lg font-semibold ${
                      status === 'success' 
                        ? 'text-green-800' 
                        : status === 'error'
                        ? 'text-red-800'
                        : 'text-blue-800'
                    }`}>
                      {status === 'success' && 'Success!'}
                      {status === 'error' && 'Failed'}
                      {status === 'loading' && 'Testing...'}
                    </h3>
                  </div>
                  <p className={`text-sm ${
                    status === 'success' 
                      ? 'text-green-700' 
                      : status === 'error'
                      ? 'text-red-700'
                      : 'text-blue-700'
                  }`}>
                    {result}
                  </p>
                </div>
              </div>
            )}

          </div>
        </div>
      </main>
    </div>
  );
}
