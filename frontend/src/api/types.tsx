export interface UserProfile {
  nickname: string;
  points: number;
  role: string;
  company?: string | null;
  notify_three_days?: boolean;
}

export interface EventItem {
  id: number;
  name: string;
  tags: string[];
  points: number;
  date: string;
  is_archived: boolean;
  is_registered?: boolean | null; // необязательно, вычисляется на сервере
  description?: string | null;
  link?: string | null;
}
export interface NotificationItem {
  id: number;
  title: string;
  body?: string | null;
  created_at: string;
}