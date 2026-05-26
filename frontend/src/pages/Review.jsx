import { useEffect, useState } from 'react';
import api from '../api';

const STATUS_COLORS = {
  PENDING:  'bg-yellow-100 text-yellow-700',
  APPROVED: 'bg-green-100 text-green-700',
  FLAGGED:  'bg-red-100 text-red-700',
  REJECTED: 'bg-gray-100 text-gray-500',
  LOCKED:   'bg-blue-100 text-blue-700',
};

export default function Review() {
  const [records, setRecords] = useState([]);
  const [filters, setFilters] = useState({ scope: '', status: '', flagged: false });
  const [selected, setSelected] = useState(null);
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  const load = () => {
    const params = {};
    if (filters.scope) params.scope = filters.scope;
    if (filters.status) params.status = filters.status;
    if (filters.flagged) params.flagged = 'true';
    api.get('/records/', { params }).then(res => {
      setRecords(res.data.results || res.data);
    });
  };

  useEffect(load, [filters]);

  const doAction = async (id, endpoint) => {
    setLoading(true);
    await api.post(`/records/${id}/${endpoint}/`, { note });
    setSelected(null);
    setNote('');
    load();
    setLoading(false);
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Review Records</h2>
      <p className="text-gray-500 text-sm mb-4">
        Approve, flag, or reject records before locking for audit.
      </p>

      {/* Filters */}
      <div className="flex gap-3 mb-5 flex-wrap items-center">
        <select
          className="border rounded-lg p-2 text-sm"
          onChange={e => setFilters(f => ({ ...f, scope: e.target.value }))}>
          <option value="">All Scopes</option>
          <option value="1">Scope 1 — Fuel</option>
          <option value="2">Scope 2 — Electricity</option>
          <option value="3">Scope 3 — Travel</option>
        </select>

        <select
          className="border rounded-lg p-2 text-sm"
          onChange={e => setFilters(f => ({ ...f, status: e.target.value }))}>
          <option value="">All Statuses</option>
          <option value="PENDING">Pending</option>
          <option value="APPROVED">Approved</option>
          <option value="FLAGGED">Flagged</option>
          <option value="REJECTED">Rejected</option>
          <option value="LOCKED">Locked</option>
        </select>

        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            onChange={e => setFilters(f => ({ ...f, flagged: e.target.checked }))}
          />
          ⚠️ Warnings only
        </label>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 border-b">
            <tr>
              {['Category','Scope','Period','Activity','CO₂e (kg)','Status',''].map(h => (
                <th key={h} className="px-4 py-3 text-left font-medium text-xs uppercase tracking-wide">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {records.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-400">
                  No records found. Upload a CSV file first.
                </td>
              </tr>
            )}
            {records.map(r => (
              <tr key={r.id}
                className={`border-t hover:bg-gray-50 ${r.has_warning ? 'bg-amber-50' : ''}`}>
                <td className="px-4 py-3 font-medium text-gray-800">
                  {r.has_warning && <span className="mr-1" title={r.warning_reason}>⚠️</span>}
                  {r.category}
                </td>
                <td className="px-4 py-3 text-gray-600">Scope {r.scope}</td>
                <td className="px-4 py-3 text-gray-600">{r.period_start}</td>
                <td className="px-4 py-3 text-gray-600">
                  {Number(r.activity_value).toFixed(2)} {r.activity_unit}
                </td>
                <td className="px-4 py-3 text-gray-800 font-medium">
                  {Number(r.co2e_kg).toFixed(2)}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[r.review_status]}`}>
                    {r.review_status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => { setSelected(r); setNote(''); }}
                    className="text-blue-600 hover:underline text-xs font-medium"
                  >
                    Review →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Side panel */}
      {selected && (
        <div className="fixed inset-0 bg-black/40 flex justify-end z-50">
          <div className="bg-white w-full max-w-md h-full overflow-y-auto shadow-xl">
            <div className="p-6">
              <button
                onClick={() => setSelected(null)}
                className="mb-4 text-gray-400 hover:text-black text-sm"
              >
                ✕ Close
              </button>

              <h3 className="text-lg font-bold text-gray-800">{selected.category}</h3>
              <p className="text-sm text-gray-500 mb-4">
                {selected.period_start} → {selected.period_end}
              </p>

              <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Activity</p>
                  <p className="font-medium">{Number(selected.activity_value).toFixed(2)} {selected.activity_unit}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">CO₂e</p>
                  <p className="font-medium">{Number(selected.co2e_kg).toFixed(2)} kg</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Scope</p>
                  <p className="font-medium">Scope {selected.scope}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Source</p>
                  <p className="font-medium">{selected.source_type}</p>
                </div>
              </div>

              {selected.has_warning && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800 mb-4">
                  ⚠️ <strong>Warning:</strong> {selected.warning_reason}
                </div>
              )}

              <details className="mb-4 border rounded-lg overflow-hidden">
                <summary className="cursor-pointer text-sm font-medium text-gray-600 p-3 bg-gray-50">
                  📄 Raw Source Data
                </summary>
                <pre className="text-xs bg-white p-3 overflow-x-auto text-gray-600">
                  {JSON.stringify(selected.raw_data, null, 2)}
                </pre>
              </details>

              <label className="block text-sm font-medium text-gray-700 mb-1">
                Note (optional)
              </label>
              <textarea
                className="w-full border rounded-lg p-2 text-sm mb-4"
                placeholder="Add a review note..."
                value={note}
                onChange={e => setNote(e.target.value)}
                rows={2}
              />

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => doAction(selected.id, 'approve')}
                  disabled={loading}
                  className="bg-green-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50"
                >
                  ✓ Approve
                </button>
                <button
                  onClick={() => doAction(selected.id, 'flag')}
                  disabled={loading}
                  className="bg-amber-500 text-white py-2 rounded-lg text-sm font-medium hover:bg-amber-600 disabled:opacity-50"
                >
                  ⚠ Flag
                </button>
                <button
                  onClick={() => doAction(selected.id, 'reject')}
                  disabled={loading}
                  className="bg-red-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50"
                >
                  ✕ Reject
                </button>
                <button
                  onClick={() => doAction(selected.id, 'lock')}
                  disabled={loading}
                  className="bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
                >
                  🔒 Lock
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}