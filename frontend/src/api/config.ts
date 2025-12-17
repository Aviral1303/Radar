/** Configuration API endpoints. */
import { api } from './client';

export interface Config {
  target_companies: string[];
  target_states: string[];
  last_ingestion: string | null;
  last_detection: string | null;
}

export const configApi = {
  get: () => api.get<Config>('/api/config'),
  setCompanies: (companies: string[]) =>
    api.post('/api/config/companies', { companies }),
  setStates: (states: string[]) =>
    api.patch('/api/config/states', { states }),
};

