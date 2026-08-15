import { create } from 'zustand'
import type { Suggestion, Summary } from '../types'
import * as api from '../services/api'

interface AppState {
  // Step
  step: number
  setStep: (step: number) => void

  // API status
  apiReady: boolean | null
  checkApiStatus: () => Promise<void>

  // Resume input
  resumeText: string
  setResumeText: (text: string) => void
  uploadedFile: { name: string; format: string } | null
  setUploadedFile: (file: { name: string; format: string } | null) => void
  fileId: string
  setFileId: (id: string) => void
  fileExt: string
  setFileExt: (ext: string) => void

  // JD input
  jdText: string
  setJdText: (text: string) => void

  // Analysis results
  suggestions: Suggestion[]
  setSuggestions: (suggestions: Suggestion[]) => void
  analysisSummary: Summary | null
  setAnalysisSummary: (summary: Summary | null) => void

  // UI state
  loading: boolean
  setLoading: (loading: boolean) => void
  error: string
  setError: (error: string) => void

  // Actions
  uploadFile: (file: File) => Promise<void>
  analyze: () => Promise<void>
  toggleSuggestion: (id: string) => void
  exportPdf: () => Promise<void>
}

export const useAppStore = create<AppState>((set, get) => ({
  // Step
  step: 0,
  setStep: (step) => set({ step }),

  // API status
  apiReady: null,
  checkApiStatus: async () => {
    try {
      const status = await api.getStatus()
      set({ apiReady: status.api_configured })
      if (!status.api_configured) {
        console.warn('[Beta] API Key 未配置，部分功能不可用')
      }
    } catch {
      // Beta 阶段：后端未启动时也不阻塞，打印警告即可
      console.warn('[Beta] 后端服务未连接，请确保 backend 已启动')
      set({ apiReady: true })
    }
  },

  // Resume input
  resumeText: '',
  setResumeText: (text) => set({ resumeText: text }),
  uploadedFile: null,
  setUploadedFile: (file) => set({ uploadedFile: file }),
  fileId: '',
  setFileId: (id) => set({ fileId: id }),
  fileExt: '',
  setFileExt: (ext) => set({ fileExt: ext }),

  // JD input
  jdText: '',
  setJdText: (text) => set({ jdText: text }),

  // Analysis results
  suggestions: [],
  setSuggestions: (suggestions) => set({ suggestions }),
  analysisSummary: null,
  setAnalysisSummary: (summary) => set({ analysisSummary: summary }),

  // UI state
  loading: false,
  setLoading: (loading) => set({ loading }),
  error: '',
  setError: (error) => set({ error }),

  // Actions
  uploadFile: async (file: File) => {
    set({ loading: true, error: '' })
    try {
      const result = await api.uploadFile(file)
      set({
        resumeText: result.text,
        fileId: result.file_id,
        fileExt: result.ext,
        uploadedFile: { name: file.name, format: result.ext },
      })
    } catch (err) {
      set({ error: (err as Error).message })
    } finally {
      set({ loading: false })
    }
  },

  analyze: async () => {
    const { resumeText, jdText } = get()
    if (!resumeText.trim() || !jdText.trim()) return
    set({ loading: true, error: '' })
    try {
      const result = await api.analyzeResume(resumeText, jdText)
      set({
        suggestions: (result.suggestions || []).map((s: Record<string, unknown>) => ({ ...s, accepted: false })) as unknown as Suggestion[],
        analysisSummary: result.summary as unknown as Summary,
        step: 3,
      })
    } catch (err) {
      set({ error: (err as Error).message })
    } finally {
      set({ loading: false })
    }
  },

  toggleSuggestion: (id: string) => {
    set((state) => ({
      suggestions: state.suggestions.map((s) =>
        s.id === id ? { ...s, accepted: !s.accepted } : s
      ),
    }))
  },

  exportPdf: async () => {
    const { suggestions, fileId, fileExt } = get()
    set({ loading: true, error: '' })
    try {
      const accepted = suggestions.filter((s) => s.accepted)
      const formData = new FormData()
      formData.append('file_id', fileId)
      formData.append('ext', fileExt)
      formData.append('replacements_json', JSON.stringify(
        accepted.map((s) => ({ original: s.original, suggested: s.suggested }))
      ))
      formData.append('title', '简历')
      const blob = await api.exportPdf(formData)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = '优化简历.pdf'
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      set({ error: (err as Error).message })
    } finally {
      set({ loading: false })
    }
  },
}))