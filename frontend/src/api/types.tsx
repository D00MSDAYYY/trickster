export interface UserProfile {
  nickname: string;
  points: number;
  role: string;            // 'user' или 'admin'
  company?: string | null; // может отсутствовать или быть null
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