/** Transitions API endpoints. */
import { api } from './client';

export interface FounderEvent {
  id: number;
  profile_id: string;
  profile_name: string;
  profile_location: string | null;
  old_title: string | null;
  new_title: string;
  new_company: string | null;
  detected_at: string;
  notified: boolean;
}

export interface TransitionsResponse {
  events: FounderEvent[];
  total: number;
  page: number;
  page_size: number;
}

export const transitionsApi = {
  list: (page = 1, pageSize = 50, notified?: boolean) => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (notified !== undefined) {
      params.append('notified', notified.toString());
    }
    return api.get<TransitionsResponse>(`/api/transitions?${params}`);
  },
};

