/** Data Sources API */

import client from './client';
import type { DataSource, DataSourceFormValues } from '../types';

export async function listDataSources(): Promise<DataSource[]> {
  const { data } = await client.get('/data-sources');
  return data;
}

export async function getDataSource(id: string): Promise<DataSource> {
  const { data } = await client.get(`/data-sources/${id}`);
  return data;
}

export async function createDataSource(values: DataSourceFormValues): Promise<DataSource> {
  const { data } = await client.post('/data-sources', values);
  return data;
}

export async function updateDataSource(id: string, values: Partial<DataSourceFormValues>): Promise<DataSource> {
  const { data } = await client.put(`/data-sources/${id}`, values);
  return data;
}

export async function deleteDataSource(id: string): Promise<void> {
  await client.delete(`/data-sources/${id}`);
}

export async function testConnection(values: DataSourceFormValues): Promise<any> {
  const { data } = await client.post('/data-sources/test', values);
  return data;
}
