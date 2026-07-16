import React, { createContext, useContext, useState, useCallback } from 'react'

const API_BASE = '/api'

async function apiFetch(url, options = {}) {
  const resp = await fetch(url, options)
  const body = await resp.json()
  if (!resp.ok) throw new Error(body.error || `请求失败 (${resp.status})`)
  if (body.success === false) throw new Error(body.error || '请求失败')
  return body.data
}

const FormContext = createContext(null)

export function FormProvider({ children }) {
  // ── 步骤状态 ──
  const [step, setStep] = useState(0) // 0=config, 1=input, 2=analyze, 3=suggestions, 4=result

  // ── API 状态 ──
  const [apiReady, setApiReady] = useState(null)

  // ── 简历输入 ──
  const [resumeText, setResumeText] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null) // { name, format }
  const [fileId, setFileId] = useState('')
  const [fileExt, setFileExt] = useState('')

  // ── JD 输入 ──
  const [jdText, setJdText] = useState('')

  // ── 分析结果 ──
  const [suggestions, setSuggestions] = useState([]) // [{id, section, original, suggested, reason, severity, accepted}]
  const [analysisSummary, setAnalysisSummary] = useState(null) // {match_score, strengths, gaps, key_improvements}

  // ── UI 状态 ──
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  const [result, setResult] = useState(null) // 优化结果（兼容旧流程）
  const [error, setError] = useState('')

  const sectionTypes = [
    { id: 'comprehensive_advantage', name: '综合优势' },
    { id: 'work_experience', name: '工作经历' },
    { id: 'project_experience', name: '项目经验' },
    { id: 'skills', name: '技能' },
  ]

  // 检查后端状态
  const checkApiStatus = useCallback(async () => {
    try { const d = await apiFetch(`${API_BASE}/status`); setApiReady(d.api_configured) }
    catch { setApiReady(false) }
  }, [])

  // ── 上传文件 ──
  const handleUploadFile = useCallback(async (file) => {
    setLoading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('file', file)
      const resp = await fetch(`${API_BASE}/resume/upload`, {
        method: 'POST',
        body: formData,
      })
      const body = await resp.json()
      if (!resp.ok || body.success === false) throw new Error(body.error || '上传失败')
      setResumeText(body.data.text)
      setFileId(body.data.file_id)
      setFileExt(body.data.ext)
      setUploadedFile({ name: file.name, format: body.data.ext })
      return body.data.text
    } catch (err) {
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  // ── JD 对齐分析 ──
  const handleAnalyze = useCallback(async () => {
    if (!resumeText.trim() || !jdText.trim()) return
    setLoading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('resume_text', resumeText)
      formData.append('jd_text', jdText)
      const resp = await fetch(`${API_BASE}/resume/analyze`, {
        method: 'POST',
        body: formData,
      })
      const body = await resp.json()
      if (!resp.ok || body.success === false) throw new Error(body.error || '分析失败')
      const data = body.data
      const items = (data.suggestions || []).map(s => ({ ...s, accepted: false }))
      setSuggestions(items)
      setAnalysisSummary(data.summary || null)
      setStep(3)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [resumeText, jdText])

  // ── 切换建议采纳状态 ──
  const toggleSuggestion = useCallback((id) => {
    setSuggestions(prev => prev.map(s => s.id === id ? { ...s, accepted: !s.accepted } : s))
  }, [])

  // ── 导出 PDF ──
  const handleExportPdf = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      // 构建替换列表
      const accepted = suggestions.filter(s => s.accepted)
      const replacements = accepted.map(s => ({
        original: s.original,
        suggested: s.suggested,
      }))

      const formData = new FormData()
      formData.append('file_id', fileId)
      formData.append('ext', fileExt)
      formData.append('replacements_json', JSON.stringify(replacements))
      formData.append('title', '简历')
      const resp = await fetch(`${API_BASE}/resume/export-pdf`, {
        method: 'POST',
        body: formData,
      })
      if (!resp.ok) throw new Error('导出失败')
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = '优化简历.pdf'
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [fileId, fileExt, suggestions])

  // ── 旧流程（兼容） ──
  const [sectionType, setSectionType] = useState('comprehensive_advantage')
  const [sectionContent, setSectionContent] = useState('')
  const [questions, setQuestions] = useState([])
  const [knownInfo, setKnownInfo] = useState('')

  const handleStartDeepDive = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const data = await apiFetch(`${API_BASE}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          section_type: sectionTypes.find(s => s.id === sectionType)?.name || sectionType,
          section_content: sectionContent,
        }),
      })
      if (data.need_answers) {
        setQuestions(data.questions || [])
        setKnownInfo(data.known_info || '')
        setStep(2)
      } else { setResult(data); setStep(4) }
    } catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }, [resumeText, sectionType, sectionContent])

  const handleSubmitAnswers = useCallback(async (answersText) => {
    setLoading(true); setStreaming(true); setStreamingText(''); setError('')
    try {
      const resp = await fetch(`${API_BASE}/optimize/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          section_type: sectionTypes.find(s => s.id === sectionType)?.name || sectionType,
          section_content: sectionContent,
          user_answers: answersText,
        }),
      })
      if (!resp.ok) throw new Error('流式请求失败')
      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      const parseEvent = (text) => {
        const lines = text.split('\n')
        let et = '', ds = ''
        for (const l of lines) {
          if (l.startsWith('event: ')) et = l.slice(7)
          else if (l.startsWith('data: ')) ds = l.slice(6)
        }
        if (!ds) return null
        try { return { event: et, data: JSON.parse(ds) } } catch { return null }
      }
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const blocks = buffer.split('\n\n')
        buffer = blocks.pop() || ''
        for (const block of blocks) {
          if (!block.trim()) continue
          const ev = parseEvent(block)
          if (!ev) continue
          switch (ev.event) {
            case 'step3_chunk': setStreamingText(ev.data.full); break
            case 'done':
              if (ev.data.final_text) setResult({ final_text: ev.data.final_text, changes_summary: ev.data.changes_summary || [], results: {} })
              setStreamingText(''); setStreaming(false); setLoading(false); setStep(4); return
            case 'error': throw new Error(ev.data.error)
          }
        }
      }
    } catch (err) { setError(err.message) } finally { setLoading(false); setStreaming(false) }
  }, [resumeText, sectionType, sectionContent])

  const handleConfigured = useCallback(() => setApiReady(true), [])
  const handleReset = useCallback(() => { setStep(1); setQuestions([]); setResult(null); setError(''); setStreamingText('') }, [])

  const value = {
    step, setStep, apiReady, checkApiStatus, handleConfigured,
    resumeText, setResumeText, uploadedFile, setUploadedFile,
    fileId, fileExt,
    jdText, setJdText,
    sectionType, setSectionType, sectionContent, setSectionContent, sectionTypes,
    suggestions, analysisSummary, toggleSuggestion, handleExportPdf,
    questions, setQuestions, knownInfo,
    loading, streaming, streamingText, result, error,
    handleUploadFile, handleAnalyze, handleStartDeepDive, handleSubmitAnswers, handleReset,
  }

  return <FormContext.Provider value={value}>{children}</FormContext.Provider>
}

export function useFormContext() {
  const ctx = useContext(FormContext)
  if (!ctx) throw new Error('useFormContext must be used within FormProvider')
  return ctx
}