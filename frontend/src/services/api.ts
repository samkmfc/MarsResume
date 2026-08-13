import type { ApiResponse } from '../types'

const API_BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  const body: ApiResponse<T> = await resp.json()
  if (!resp.ok || body.success === false) {
    throw new Error(body.error?.message || `请求失败 (${resp.status})`)
  }
  return body.data as T
}

export async function getStatus() {
  return request<{ status: string; api_configured: boolean; version: string }>('/status')
}

export async function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const resp = await fetch(`${API_BASE}/resume/upload`, { method: 'POST', body: formData })
  const body = await resp.json()
  if (!resp.ok || body.success === false) throw new Error(body.error?.message || '上传失败')
  return body.data as { file_id: string; ext: string; text: string; text_length: number }
}

export async function analyzeResume(resumeText: string, jdText: string) {
  const formData = new FormData()
  formData.append('resume_text', resumeText)
  formData.append('jd_text', jdText)
  const resp = await fetch(`${API_BASE}/resume/analyze`, { method: 'POST', body: formData })
  const body = await resp.json()
  if (!resp.ok || body.success === false) throw new Error(body.error?.message || '分析失败')
  return body.data as { suggestions: Array<Record<string, unknown>>; summary: Record<string, unknown> }
}

export async function optimizeResume(body: Record<string, unknown>) {
  return request<Record<string, unknown>>('/optimize', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function exportPdf(formData: FormData) {
  const resp = await fetch(`${API_BASE}/resume/export-pdf`, { method: 'POST', body: formData })
  if (!resp.ok) throw new Error('导出失败')
  return resp.blob()
}

export async function login(email: string, password: string) {
  return request<{ access_token: string; user: Record<string, unknown> }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export async function register(email: string, username: string, password: string) {
  return request<{ id: string }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, username, password }),
  })
}

export async function getMe() {
  return request<Record<string, unknown> | null>('/auth/me')
}