export interface Suggestion {
  id: string
  section: string
  original: string
  suggested: string
  reason: string
  severity: 'high' | 'medium' | 'low'
  accepted: boolean
}

export interface Summary {
  match_score: number
  strengths: string[]
  gaps: string[]
  key_improvements: string
}

export interface SectionType {
  id: string
  name: string
  description: string
}

export interface UploadResult {
  file_id: string
  filename: string
  ext: string
  text: string
  text_length: number
}

export interface OptimizationResult {
  need_answers: boolean
  final_text?: string
  changes_summary?: string[]
  questions?: string[]
  known_info?: string
  results?: Record<string, unknown>
}

export interface UserInfo {
  id: string
  email: string
  username: string
  plan: 'free' | 'pro' | 'enterprise'
  usage_count: number
  usage_limit: number
  is_active: boolean
}

export interface ApiResponse<T> {
  success: boolean
  data: T | null
  error: { code: string; message: string; detail?: Record<string, unknown> } | null
  meta: Record<string, unknown>
}

export interface SearchResult {
  id: string
  text: string
  metadata: Record<string, unknown>
  score: number
}

export interface RAGStats {
  resume_examples: number
  jd_templates: number
  optimization_history: number
}