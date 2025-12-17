/** Jobs API endpoints. */
import { api } from './client';

export interface DetectionResult {
  message: string;
  new_transitions_detected: number;
  notifications_sent: number;
}

export const jobsApi = {
  runDetection: () => api.post<DetectionResult>('/api/jobs/run-detection'),
  triggerIngestion: () => api.post('/api/profiles/ingest'),
};

