import { useState } from 'react';
import api from '../api';

const SOURCE_TYPES = [
  { value: 'SAP_FLAT', label: '🏭 SAP Flat File — Fuel & Procurement (Scope 1)' },
  { value: 'UTILITY_CSV', label: '⚡ Utility Portal CSV — Electricity (Scope 2)' },
  { value: 'TRAVEL_CSV', label: '✈️ Travel Platform CSV — Concur/Navan (Scope 3)' },
];

export default function Upload() {
  const [sourceType, setSourceType] = useState('SAP_FLAT');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return alert('Please select a CSV file first');
    const form = new FormData();
    form.append('file', file);
    form.append('source_type', sourceType);
    form.append('tenant_id', 1);
    setLoading(true);
    setResult(null);
    try {
      const res = await api.post('/upload/', form);
      setResult(res.data);
    } catch (e) {
      setResult({ error: e.response?.data || 'Upload failed' });
    }
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-2xl">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Upload Data</h2>
      <p className="text-gray-500 text-sm mb-6">
        Upload a CSV file from any of the three supported sources.
      </p>

      <label className="block text-sm font-medium text-gray-700 mb-1">
        Data Source
      </label>
      <select
        className="w-full border rounded-lg p-2 mb-5 text-sm"
        value={sourceType}
        onChange={e => setSourceType(e.target.value)}
      >
        {SOURCE_TYPES.map(s => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>

      <label className="block text-sm font-medium text-gray-700 mb-1">
        CSV File
      </label>
      <input
        type="file"
        accept=".csv"
        className="w-full border rounded-lg p-2 mb-5 text-sm bg-white"
        onChange={e => setFile(e.target.files[0])}
      />

      <button
        onClick={handleUpload}
        disabled={loading}
        className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm font-medium"
      >
        {loading ? '⏳ Processing...' : '📤 Upload & Process'}
      </button>

      {result && (
        <div className="mt-6 p-4 rounded-xl border bg-gray-50">
          {result.error ? (
            <p className="text-red-600 text-sm">
              ❌ {JSON.stringify(result.error)}
            </p>
          ) : (
            <>
              <p className="text-green-700 font-medium text-sm">
                ✅ {result.rows_imported} rows imported successfully
              </p>
              {result.errors?.length > 0 && (
                <div className="mt-3">
                  <p className="text-red-600 font-medium text-sm">
                    ⚠️ {result.errors.length} rows had errors:
                  </p>
                  <ul className="mt-1 space-y-1">
                    {result.errors.map((e, i) => (
                      <li key={i} className="text-xs text-red-500">
                        Row {e.row}: {e.error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}