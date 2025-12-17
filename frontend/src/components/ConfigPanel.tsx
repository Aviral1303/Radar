import { useState, useEffect } from 'react';
import { configApi, type Config } from '../api/config';

interface ConfigPanelProps {
  section: 'companies' | 'locations' | 'notifications';
}

export function ConfigPanel({ section }: ConfigPanelProps) {
  const [config, setConfig] = useState<Config | null>(null);
  const [companies, setCompanies] = useState<string>('');
  const [states, setStates] = useState<string>('');
  const [loading, setLoading] = useState<'companies' | 'states' | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  const loadConfig = async () => {
    const result = await configApi.get();
    if (result.data) {
      setConfig(result.data);
      setCompanies(result.data.target_companies.join('\n'));
      setStates(result.data.target_states.join(', '));
    } else {
      setMessage({ type: 'error', text: result.error || 'Failed to load config' });
    }
  };

  const handleSaveCompanies = async () => {
    setLoading('companies');
    setMessage(null);
    const companyList = companies.split('\n').filter(c => c.trim());
    const result = await configApi.setCompanies(companyList);
    if (result.error) {
      setMessage({ type: 'error', text: result.error });
    } else {
      setMessage({ type: 'success', text: `Successfully saved ${companyList.length} companies` });
      loadConfig();
    }
    setLoading(null);
  };

  const handleSaveStates = async () => {
    setLoading('states');
    setMessage(null);
    const stateList = states.split(',').map(s => s.trim()).filter(s => s);
    const result = await configApi.setStates(stateList);
    if (result.error) {
      setMessage({ type: 'error', text: result.error });
    } else {
      setMessage({ type: 'success', text: `Successfully saved ${stateList.length} states` });
      loadConfig();
    }
    setLoading(null);
  };

  if (section === 'companies') {
    return (
      <div>
        <div className="section-header">
          <h1 className="section-title text-xl">Target Companies</h1>
          <p className="section-description">Define the companies you want to track for founder transitions</p>
        </div>

        {message && (
          <div className={`alert mb-6 ${message.type === 'success' ? 'alert-success' : 'alert-error'}`}>
            {message.type === 'success' ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
            <span>{message.text}</span>
          </div>
        )}

        <div className="card p-6">
          <div className="form-group">
            <label className="form-label">Company List</label>
            <textarea
              value={companies}
              onChange={(e) => setCompanies(e.target.value)}
              placeholder="Enter one company per line&#10;&#10;Example:&#10;Google&#10;Meta&#10;Stripe&#10;OpenAI"
              rows={12}
            />
            <p className="form-hint">
              Enter company names exactly as they appear on LinkedIn. One company per line.
            </p>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-[var(--border-subtle)]">
            <span className="text-sm text-[var(--text-muted)]">
              {companies.split('\n').filter(c => c.trim()).length} companies configured
            </span>
            <button
              onClick={handleSaveCompanies}
              disabled={loading !== null}
              className="btn btn-primary"
            >
              {loading === 'companies' ? (
                <>
                  <svg className="w-4 h-4 spinner" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Saving...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Save Changes
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (section === 'locations') {
    return (
      <div>
        <div className="section-header">
          <h1 className="section-title text-xl">Target Locations</h1>
          <p className="section-description">Specify US states to filter professionals by location</p>
        </div>

        {message && (
          <div className={`alert mb-6 ${message.type === 'success' ? 'alert-success' : 'alert-error'}`}>
            {message.type === 'success' ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
            <span>{message.text}</span>
          </div>
        )}

        <div className="card p-6">
          <div className="form-group">
            <label className="form-label">US State Codes</label>
            <input
              type="text"
              value={states}
              onChange={(e) => setStates(e.target.value)}
              placeholder="CA, NY, TX, WA, MA"
            />
            <p className="form-hint">
              Enter 2-letter US state codes separated by commas. Example: CA, NY, TX
            </p>
          </div>

          <div className="mt-4">
            <p className="form-label mb-3">Quick Select</p>
            <div className="flex flex-wrap gap-2">
              {['CA', 'NY', 'TX', 'WA', 'MA', 'IL', 'FL', 'CO', 'GA', 'NC'].map(state => {
                const isSelected = states.toUpperCase().includes(state);
                return (
                  <button
                    key={state}
                    onClick={() => {
                      if (isSelected) {
                        setStates(states.split(',').filter(s => s.trim().toUpperCase() !== state).join(', '));
                      } else {
                        setStates(states ? `${states}, ${state}` : state);
                      }
                    }}
                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                      isSelected 
                        ? 'bg-[var(--accent-purple)] text-white' 
                        : 'bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'
                    }`}
                  >
                    {state}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center justify-between pt-6 mt-6 border-t border-[var(--border-subtle)]">
            <span className="text-sm text-[var(--text-muted)]">
              {states.split(',').filter(s => s.trim()).length} states selected
            </span>
            <button
              onClick={handleSaveStates}
              disabled={loading !== null}
              className="btn btn-primary"
            >
              {loading === 'states' ? (
                <>
                  <svg className="w-4 h-4 spinner" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Saving...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Save Changes
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (section === 'notifications') {
    return (
      <div>
        <div className="section-header">
          <h1 className="section-title text-xl">Notification Settings</h1>
          <p className="section-description">Configure how and when you receive founder alerts</p>
        </div>

        <div className="card p-6 mb-6">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-4">Email Notifications</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-[var(--border-subtle)]">
              <div>
                <p className="text-sm font-medium text-[var(--text-primary)]">Daily Digest</p>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">Receive a summary of all new founder signals</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-9 h-5 bg-[var(--bg-hover)] peer-focus:ring-2 peer-focus:ring-[var(--accent-purple-light)] rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[var(--accent-purple)]"></div>
              </label>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-[var(--border-subtle)]">
              <div>
                <p className="text-sm font-medium text-[var(--text-primary)]">Instant Alerts</p>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">Get notified immediately when a founder is detected</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-9 h-5 bg-[var(--bg-hover)] peer-focus:ring-2 peer-focus:ring-[var(--accent-purple-light)] rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[var(--accent-purple)]"></div>
              </label>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm font-medium text-[var(--text-primary)]">Weekly Report</p>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">Comprehensive weekly summary with analytics</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-9 h-5 bg-[var(--bg-hover)] peer-focus:ring-2 peer-focus:ring-[var(--accent-purple-light)] rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[var(--accent-purple)]"></div>
              </label>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-4">System Status</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="stat-card">
              <p className="stat-label">Last Data Sync</p>
              <p className="stat-value text-lg">
                {config?.last_ingestion 
                  ? new Date(config.last_ingestion).toLocaleDateString()
                  : '—'
                }
              </p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Last Detection</p>
              <p className="stat-value text-lg">
                {config?.last_detection 
                  ? new Date(config.last_detection).toLocaleDateString()
                  : '—'
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
