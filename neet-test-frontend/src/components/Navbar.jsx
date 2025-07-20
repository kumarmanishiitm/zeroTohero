import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BookOpen, Home, Clock, Award, LogOut, User, History } from 'lucide-react';
import { useTest } from '../context/TestContext';

const Navbar = () => {
  const location = useLocation();
  const { user, logout } = useTest();

  const isActive = (path) => {
    return location.pathname === path;
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">NEET Prep</h1>
              <p className="text-xs text-gray-500">Test Platform</p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center space-x-6">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors duration-200 ${
                isActive('/') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Home className="w-4 h-4" />
              <span className="font-medium">Home</span>
            </Link>

            <Link
              to="/test-selection"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors duration-200 ${
                isActive('/test-selection') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Clock className="w-4 h-4" />
              <span className="font-medium">Take Test</span>
            </Link>

            <Link
              to="/test-history"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors duration-200 ${
                isActive('/test-history') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <History className="w-4 h-4" />
              <span className="font-medium">Test History</span>
            </Link>

            <div className="flex items-center space-x-2 px-3 py-2 text-gray-500">
              <Award className="w-4 h-4" />
              <span className="font-medium">Practice Mode</span>
            </div>

            {/* User Section */}
            {user && (
              <div className="flex items-center space-x-4 border-l border-gray-200 pl-6">
                <div className="flex items-center space-x-2">
                  <User className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">
                    Welcome, {user.username}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="font-medium">Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
