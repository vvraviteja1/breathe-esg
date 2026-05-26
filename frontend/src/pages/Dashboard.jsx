import { useEffect, useState } from 'react';
import api from '../api';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    api.get('/dashboard/')
      .then(res => setSummary(res.data))
      .catch(() => setSummary({}));
  }, []);

  if (!summary) return (
    <div className="p-6 text-gray-500">Loading dashboard...</div>
  );

  const cards = [
    { label: 'Scope 1 — Direct Emissions', value: `${Number(summary.scope1_co2e || 0).toFixed(1)} kg`, color: 'bg-orange-50 border-orange-200 text-orange-700' },
    { label: 'Scope 2 — Electricity', value: `${Number(summary.scope2_co2e || 0).toFixed(1)} kg`, color: 'bg-blue-50 border-blue-200 text-blue-700' },
    { label: 'Scope 3 — Travel', value: `${Number(summary.scope3_co2e || 0).toFixed(1)} kg`, color: 'bg-purple-50 border-purple-200 text-purple-700' },
    { label: 'Pending Review', value: summary.pending || 0, color: 'bg-yellow-50 border-yellow-200 text-yellow-700' },
    { label: 'Flagged ⚠️', value: summary.flagged || 0, color: 'bg-red-50 border-red-200 text-red-700' },
    { label: 'Approved ✓', value: summary.approved || 0, color: 'bg-green-50 border-green-200 text-green-700' },
  ];

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Dashboard</h2>
      <p className="text-gray-500 text-sm mb-6">
        Total records: <strong>{summary.total || 0}</strong>
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {cards.map(c => (
          <div key={c.label} className={`rounded-xl p-5 border ${c.color}`}>
            <p className="text-xs font-medium uppercase tracking-wide opacity-70">{c.label}</p>
            <p className="text-3xl font-bold mt-2">{c.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}