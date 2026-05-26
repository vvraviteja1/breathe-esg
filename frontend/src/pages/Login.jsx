import { useState } from 'react';
import api from '../api';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    try {
      const res = await api.post('/auth/login/', { username, password });
      localStorage.setItem('token', res.data.token);
      onLogin();
    } catch {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow w-full max-w-sm">
        <h1 className="text-2xl font-bold text-green-700 mb-2">🌿 Breathe ESG</h1>
        <p className="text-gray-500 text-sm mb-6">Emissions Data Review Platform</p>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <input
          className="w-full border rounded p-2 mb-3 text-sm"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />
        <input
          type="password"
          className="w-full border rounded p-2 mb-4 text-sm"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSubmit()}
        />
        <button
          onClick={handleSubmit}
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 text-sm font-medium"
        >
          Sign In
        </button>
      </div>
    </div>
  );
}