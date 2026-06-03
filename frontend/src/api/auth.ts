/** Auth API */

import client from './client';
import type { TokenResponse, User } from '../types';

export async function login(username: string, password: string): Promise<TokenResponse> {
  const { data } = await client.post('/auth/login', { username, password });
  return data;
}

export async function register(username: string, email: string, password: string): Promise<User> {
  const { data } = await client.post('/auth/register', { username, email, password });
  return data;
}

export async function refreshToken(refresh_token: string): Promise<TokenResponse> {
  const { data } = await client.post('/auth/refresh', { refresh_token });
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await client.get('/auth/me');
  return data;
}
