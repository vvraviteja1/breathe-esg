import { useState } from 'react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Review from './pages/Review';

const NAV = [
  { id: 'dashboard', label: '📊 Dashboard' },
  { id: 'upload',    label: '📤 Upload' },
  { id: 'review',    label: '🔍 Review' },
];

export default function App() {
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem('token'));
  const [page, setPage] = useState('dashboard');

  if (!loggedIn) return <Login onLogin={() => setLoggedIn(true)} />;

  const logout = () => {
    localStorage.removeItem('token');
    setLoggedIn(false);
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 bg-green-800 text-white flex flex-col flex-shrink-0">
        <div className="p-5 border-b border-green-700">
          <h1 className="font-bold text-lg">🌿 Breathe ESG</h1>
          <p className="text-xs text-green-300 mt-1">Data Review Platform</p>
        </div>
        <nav className="flex-1 p-3">
          {NAV.map(n => (
            <button
              key={n.id}
              onClick={() => setPage(n.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-colors
                ${page === n.id
                  ? 'bg-green-600 font-medium'
                  : 'hover:bg-green-700 text-green-100'}`}
            >
              {n.label}
            </button>
          ))}
        </nav>
        <div className="p-3 border-t border-green-700">
          <button
            onClick={logout}
            className="text-xs text-green-300 hover:text-white py-1"
          >
            Sign out →
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {page === 'dashboard' && <Dashboard />}
        {page === 'upload'    && <Upload />}
        {page === 'review'    && <Review />}
      </main>
    </div>
  );
}