import React, { createContext, useContext, useReducer, useEffect, useState } from 'react';
import { testAPI } from '../services/api';

const TestContext = createContext();

const testReducer = (state, action) => {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_SUBJECTS':
      return { ...state, subjects: action.payload };
    case 'SET_TOPICS':
      return { ...state, topics: action.payload };
    case 'SET_SELECTED_SUBJECT':
      return { ...state, selectedSubject: action.payload, selectedTopic: null };
    case 'SET_SELECTED_TOPIC':
      return { ...state, selectedTopic: action.payload };
    case 'SET_QUESTION_COUNT':
      return { ...state, questionCount: action.payload };
    case 'SET_TEST_TYPE':
      return { ...state, testType: action.payload };
    case 'SET_CURRENT_TEST':
      return { ...state, currentTest: action.payload };
    case 'SET_TEST_RESULTS':
      return { ...state, testResults: action.payload };
    case 'RESET_TEST':
      return {
        ...state,
        selectedSubject: null,
        selectedTopic: null,
        questionCount: 10,
        testType: 'topic',
        currentTest: null,
        testResults: null
      };
    default:
      return state;
  }
};

const initialState = {
  user: null,
  subjects: [],
  topics: [],
  selectedSubject: null,
  selectedTopic: null,
  questionCount: 10,
  testType: 'topic', // 'topic', 'subject', 'full'
  currentTest: null,
  testResults: null
};

export const TestProvider = ({ children }) => {
  const [state, dispatch] = useReducer(testReducer, initialState);
  const [loading, setLoading] = useState(true);

  // Check authentication on app start
  useEffect(() => {
    const validateToken = async () => {
      console.log('🔍 Checking authentication on app start...');
      const token = localStorage.getItem('token');
      
      if (token) {
        console.log('📝 Token found, validating with backend...');
        try {
          const response = await testAPI.getCurrentUser();
          if (response.data.success) {
            console.log('✅ Token valid, user authenticated:', response.data.user.username);
            dispatch({ type: 'SET_USER', payload: response.data.user });
          } else {
            console.warn('❌ Token invalid, removing and redirecting to login');
            localStorage.removeItem('token');
            dispatch({ type: 'SET_USER', payload: null });
          }
        } catch (error) {
          console.error('❌ Token validation failed:', error.message);
          localStorage.removeItem('token');
          dispatch({ type: 'SET_USER', payload: null });
        }
      } else {
        console.log('📭 No token found, user needs to login');
        dispatch({ type: 'SET_USER', payload: null });
      }
      
      setLoading(false);
      console.log('✅ Authentication check complete');
    };

    validateToken();
  }, []);

  const login = (userData, token) => {
    localStorage.setItem('token', token);
    dispatch({ type: 'SET_USER', payload: userData });
  };

  const logout = () => {
    localStorage.removeItem('token');
    dispatch({ type: 'SET_USER', payload: null });
    dispatch({ type: 'SET_CURRENT_TEST', payload: null });
  };

  const value = {
    ...state,
    loading,
    login,
    logout,
    dispatch,
  };

  return (
    <TestContext.Provider value={value}>
      {children}
    </TestContext.Provider>
  );
};

export const useTest = () => {
  const context = useContext(TestContext);
  if (!context) {
    throw new Error('useTest must be used within a TestProvider');
  }
  return context;
};
