import { useState, useEffect } from 'react';
import { transitionsApi, type TransitionsResponse } from '../api/transitions';

export function TransitionsTable() {
  const [data, setData] = useState<TransitionsResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTransitions();
  }, [page]);

  const loadTransitions = async () => {
    setLoading(true);
    setError(null);
    const result = await transitionsApi.list(page, 10);
    if (result.data) {
      setData(result.data);
    } else {
      setError(result.error || 'Failed to load');
    }
    setLoading(false);
  };

  if (loading && !data) {
    return (
      <div className="card p-12">
        <div className="flex flex-col items-center justify-center gap-3">
          <svg className="w-6 h-6 text-[var(--accent-purple)] spinner" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-sm text-[var(--text-muted)]">Loading signals...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-error">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{error}</span>
      </div>
    );
  }

  if (!data || data.events.length === 0) {
    return (
      <div className="card p-12">
        <div className="empty-state">
          <svg className="empty-state-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
          </svg>
          <h3 className="text-base font-medium text-[var(--text-primary)] mb-1">No Signals Yet</h3>
          <p className="text-sm">Configure your targets and sync data to start detecting founders.</p>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(data.total / data.page_size);

  return (
    <div className="card overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-[var(--border-color)] flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-[var(--text-primary)]">Recent Signals</h3>
          <p className="text-xs text-[var(--text-muted)] mt-0.5">{data.total} total</p>
        </div>
        <button onClick={loadTransitions} className="btn btn-secondary py-1.5 px-3 text-xs">
          <svg className="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Table */}
      <table>
        <thead>
          <tr>
            <th>Person</th>
            <th>Location</th>
            <th>Transition</th>
            <th>Detected</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {data.events.map((event) => (
            <tr key={event.id}>
              <td>
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-[var(--accent-purple-light)] flex items-center justify-center text-xs font-medium text-[var(--accent-purple)]">
                    {event.profile_name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                  </div>
                  <span className="font-medium text-[var(--text-primary)]">{event.profile_name}</span>
                </div>
              </td>
              <td>{event.profile_location || '—'}</td>
              <td>
                <div className="flex items-center gap-2">
                  <span className="text-[var(--text-muted)]">{event.old_title || '—'}</span>
                  <svg className="w-3.5 h-3.5 text-[var(--text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                  <span className="badge badge-purple">{event.new_title}</span>
                </div>
                {event.new_company && (
                  <span className="text-xs text-[var(--text-muted)] mt-1 block">@ {event.new_company}</span>
                )}
              </td>
              <td>
                <span className="text-xs">{new Date(event.detected_at).toLocaleDateString()}</span>
              </td>
              <td>
                {event.notified ? (
                  <span className="badge badge-green">Sent</span>
                ) : (
                  <span className="badge badge-blue">Pending</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-6 py-3 border-t border-[var(--border-color)] flex items-center justify-between bg-[var(--bg-secondary)]">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn btn-secondary py-1.5 px-3 text-xs disabled:opacity-40"
          >
            ← Previous
          </button>
          <span className="text-xs text-[var(--text-muted)]">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= totalPages}
            className="btn btn-secondary py-1.5 px-3 text-xs disabled:opacity-40"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
