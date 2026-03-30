import { LucideIcon } from 'lucide-react';

export interface Feature {
  title: string;
  description: string;
  icon: LucideIcon;
  color: string;
}

export interface NavItem {
  label: string;
  href: string;
}

export enum UserRole {
  USER = '用户',
  DEVELOPER = '开发者',
  ADMIN = '管理员'
}