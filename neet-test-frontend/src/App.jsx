import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import TestSelection from './pages/TestSelection';
import TestInterface from './pages/TestInterface';
import TestResults from './pages/TestResults';
import TestHistory from './pages/TestHistory';
import { TestProvider, useTest } from './context/TestContext';

// Protected App Component
const AppContent = () => {
  const { user, loading } = useTest();

  // Show loading spinner while checking authentication
  if (loading) {
    console.log('⏳ Showing loading screen...');
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // If no user, force redirect to login
  if (!user) {
    console.log('🚫 No user found - forcing redirect to login');
    return (
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    );
  }

  // User is authenticated - show normal app
  console.log('✅ User authenticated - showing normal app');
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/login" element={<Navigate to="/" replace />} />
          <Route path="/" element={<Home />} />
          <Route path="/test-selection" element={<TestSelection />} />
          <Route path="/test-history" element={<TestHistory />} />
          <Route path="/test/:testId" element={<TestInterface />} />
          <Route path="/results/:testId" element={<TestResults />} />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return (
    <TestProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <AppContent />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </TestProvider>
  );
}

export default App;
