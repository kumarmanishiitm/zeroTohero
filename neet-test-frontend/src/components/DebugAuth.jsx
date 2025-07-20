import React, { useEffect } from 'react';
import { useTest } from '../context/TestContext';

const DebugAuth = () => {
  const { user, loading } = useTest();

  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('=== AUTHENTICATION DEBUG ===');
    console.log('User from context:', user);
    console.log('Loading state:', loading);
    console.log('Token in localStorage:', token ? `${token.substring(0, 20)}...` : 'NO TOKEN');
    console.log('Current URL:', window.location.href);
    console.log('================================');
  }, [user, loading]);

  return (
    <div className="p-4 bg-yellow-100 border border-yellow-400 rounded-lg">
      <h3 className="font-bold text-yellow-800">Authentication Debug</h3>
      <p><strong>User:</strong> {user ? JSON.stringify(user) : 'null'}</p>
      <p><strong>Loading:</strong> {loading.toString()}</p>
      <p><strong>Token:</strong> {localStorage.getItem('token') ? 'Present' : 'Missing'}</p>
    </div>
  );
};

export default DebugAuth;
