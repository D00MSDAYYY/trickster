/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type Role = "admin" | "user" | "observer";
export type Role1 = "admin" | "user" | "observer";

export interface EventInfoResponse {
  id: number | null;
  title: string;
  points: number;
  date: string;
  tags: TagInfoResponse[] | null;
  description: string | null;
  link: string | null;
  is_archived: boolean;
  is_registered: boolean;
  created_at: string;
}
export interface TagInfoResponse {
  id: number | null;
  name: string;
}
export interface LoginRequest {
  password: string;
}
export interface NotificationInfoResponse {
  id: number | null;
  title: string;
  body: string | null;
  created_at: string;
}
export interface UserInfoResponse {
  id: number | null;
  nickname: string;
  role: Role;
  firstname: string;
  middlename: string | null;
  lastname: string;
  points: number;
  company: string;
  password: string;
  created_at: string;
}
/**
 * Base class for Pydantic models supporting role-based field visibility.
 * (Class body unchanged)
 */
export interface VisibleFieldsModel {}
export interface Attendance {
  user_id: number;
  event_id: number;
  created_at?: string;
}
export interface Event {
  id?: number | null;
  title: string;
  points?: number;
  date: string;
  description?: string | null;
  link?: string | null;
  is_archived?: boolean;
  created_at?: string;
}
export interface EventTagLink {
  event_id: number;
  tag_id: number;
}
export interface Notification {
  id?: number | null;
  title: string;
  body?: string | null;
  created_at?: string;
}
export interface Registration {
  user_id: number;
  event_id: number;
  created_at?: string;
}
export interface SQLModel {}
export interface Tag {
  id?: number | null;
  name: string;
}
export interface User {
  id?: number | null;
  nickname: string;
  role?: Role1;
  firstname: string;
  middlename?: string | null;
  lastname: string;
  points?: number;
  company: string;
  password: string;
  created_at?: string;
}
