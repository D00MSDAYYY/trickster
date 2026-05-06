/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type AppTheme = "dark" | "light";
export type Role = "admin" | "user" | "observer";

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
export interface SettingsResponse {
  app_theme: AppTheme;
  days_to_notify: number;
  do_notify: boolean;
}
export interface UserInfoResponse {
  id?: number | null;
  nickname?: string | null;
  role?: Role | null;
  firstname?: string | null;
  middlename?: string | null;
  lastname?: string | null;
  points?: number | null;
  company?: string | null;
  password?: string | null;
  created_at?: string | null;
}
/**
 * Base class for Pydantic models supporting role-based field visibility.
 * (Class body unchanged)
 */
export interface VisibleFieldsModel {}
