import { describe, it, expect, beforeEach, vi } from 'vitest'

// mock 掉 API 层，store 测试不触网络
vi.mock('../services/api', () => ({
  getStatus: vi.fn(),
  uploadFile: vi.fn(),
  analyzeResume: vi.fn(),
  exportPdf: vi.fn(),
}))

import { useAppStore } from './appStore'
import * as api from '../services/api'

const initial = {
  step: 0,
  apiReady: null as boolean | null,
  resumeText: '',
  jdText: '',
  suggestions: [] as unknown[],
  analysisSummary: null,
  loading: false,
  error: '',
  fileId: '',
  fileExt: '',
  uploadedFile: null as unknown,
}

beforeEach(() => {
  useAppStore.setState(initial)
  vi.clearAllMocks()
})

describe('appStore setters', () => {
  it('setStep 更新步骤', () => {
    useAppStore.getState().setStep(2)
    expect(useAppStore.getState().step).toBe(2)
  })

  it('setResumeText 更新简历文本', () => {
    useAppStore.getState().setResumeText('hello')
    expect(useAppStore.getState().resumeText).toBe('hello')
  })
})

describe('checkApiStatus', () => {
  it('成功时 apiReady=true', async () => {
    vi.mocked(api.getStatus).mockResolvedValue({ api_configured: true } as never)
    await useAppStore.getState().checkApiStatus()
    expect(useAppStore.getState().apiReady).toBe(true)
  })

  it('失败时 apiReady=false', async () => {
    vi.mocked(api.getStatus).mockRejectedValue(new Error('网络错误'))
    await useAppStore.getState().checkApiStatus()
    expect(useAppStore.getState().apiReady).toBe(false)
  })
})

describe('analyze', () => {
  it('简历或 JD 为空时提前返回，不调用 API', async () => {
    await useAppStore.getState().analyze()
    expect(api.analyzeResume).not.toHaveBeenCalled()
  })

  it('输入完整时调用 API 并推进到 step 3', async () => {
    useAppStore.setState({ resumeText: '三年后端经验', jdText: '需要 Python' })
    vi.mocked(api.analyzeResume).mockResolvedValue({
      suggestions: [{ id: '1', original: 'a', suggested: 'b', reason: 'c' }],
      summary: null,
    } as never)
    await useAppStore.getState().analyze()
    const s = useAppStore.getState()
    expect(s.step).toBe(3)
    expect(s.suggestions).toHaveLength(1)
    expect(s.suggestions[0]).toMatchObject({ accepted: false })
  })
})

describe('toggleSuggestion', () => {
  it('翻转建议的 accepted 状态', () => {
    useAppStore.setState({
      suggestions: [{ id: '1', original: 'a', suggested: 'b', reason: 'c', accepted: false }],
    })
    useAppStore.getState().toggleSuggestion('1')
    expect(useAppStore.getState().suggestions[0]).toMatchObject({ accepted: true })
  })
})
