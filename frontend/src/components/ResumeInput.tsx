import { useRef, useState, useCallback } from 'react'

interface ResumeInputProps {
  resumeText: string
  setResumeText: (text: string) => void
  uploadedFile: { name: string; format: string } | null
  setUploadedFile: (file: { name: string; format: string } | null) => void
  setFileId: (id: string) => void
  setFileExt: (ext: string) => void
  jdText: string
  setJdText: (text: string) => void
  onUpload: (file: File) => Promise<void>
  onAnalyze: () => Promise<void>
  loading: boolean
  error: string
}

const FORMATS = [
  { ext: 'PDF', icon: '📄' },
  { ext: 'DOCX', icon: '📝' },
  { ext: 'PNG', icon: '🖼️' },
  { ext: 'JPG', icon: '🖼️' },
]

export default function ResumeInput({
  resumeText, setResumeText, uploadedFile, setUploadedFile,
  setFileId, setFileExt, jdText, setJdText,
  onUpload, onAnalyze, loading, error,
}: ResumeInputProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadedFile({ name: file.name, format: file.name.split('.').pop() || '' })
    await onUpload(file)
  }

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files?.[0]
    if (!file) return
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!['.pdf', '.docx', '.png', '.jpg', '.jpeg'].includes(ext)) {
      alert('请上传 PDF、Word 或图片格式的文件')
      return
    }
    setUploadedFile({ name: file.name, format: file.name.split('.').pop() || '' })
    await onUpload(file)
  }, [onUpload, setUploadedFile])

  const handleDragOver = (e: React.DragEvent) => { e.preventDefault(); setDragOver(true) }
  const handleDragLeave = (e: React.DragEvent) => { e.preventDefault(); setDragOver(false) }

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation()
    setUploadedFile(null)
    setFileId('')
    setFileExt('')
    setResumeText('')
  }

  const formatFileSize = (name: string) => {
    // rough estimate from name - we just show the format
    return name.split('.').pop()?.toUpperCase() || ''
  }

  return (
    <div className="resume-input">
      {/* ── 上传简历区 ── */}
      <div className="upload-section">
        <div className="upload-section-title">
          <span className="upload-section-icon">📤</span>
          上传简历
        </div>
        <p className="upload-section-desc">
          上传你的简历文件，AI 将自动提取文本内容进行分析
        </p>

        <div
          className={`upload-zone ${dragOver ? 'drag-over' : ''} ${uploadedFile ? 'has-file' : ''}`}
          onClick={() => !loading && fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.png,.jpg,.jpeg"
            hidden
            onChange={handleFileChange}
            disabled={loading}
          />

          {uploadedFile ? (
            /* ── 已上传状态 ── */
            <div className="uploaded-file">
              <div className="uploaded-file-icon">
                {uploadedFile.format === 'pdf' ? '📄' :
                 uploadedFile.format === 'docx' ? '📝' : '🖼️'}
              </div>
              <div className="uploaded-file-info">
                <div className="uploaded-file-name">{uploadedFile.name}</div>
                <div className="uploaded-file-meta">
                  <span className="badge badge-format">{formatFileSize(uploadedFile.name)}</span>
                  <span className="uploaded-file-status">✓ 上传成功</span>
                </div>
              </div>
              <button
                className="btn btn-ghost btn-sm"
                onClick={handleRemove}
                disabled={loading}
              >
                更换文件
              </button>
            </div>
          ) : (
            /* ── 未上传状态 ── */
            <div className="upload-placeholder">
              <div className="upload-icon">
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                  <rect x="8" y="6" width="32" height="36" rx="4" stroke="currentColor" strokeWidth="2" fill="none"/>
                  <path d="M24 18v12M18 24l6-6 6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M16 34h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              <div className="upload-title">点击上传或拖拽文件到此处</div>
              <div className="upload-hint">支持 PDF、Word (.docx)、图片 (PNG/JPG) 格式</div>
              <div className="upload-formats">
                {FORMATS.map((f) => (
                  <span key={f.ext} className="upload-format-badge">
                    {f.icon} {f.ext}
                  </span>
                ))}
              </div>
              <button className="btn btn-primary btn-lg upload-btn" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click() }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                选择文件上传
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ── 简历文本预览 ── */}
      {resumeText && (
        <div className="form-group">
          <div className="form-label-row">
            <label className="form-label">📋 简历文本预览</label>
            <span className="form-label-hint">可在此编辑文本</span>
          </div>
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            rows={8}
            placeholder="简历文本将在此显示..."
          />
        </div>
      )}

      {/* ── JD 粘贴区 ── */}
      <div className="jd-section">
        <div className="upload-section-title">
          <span className="upload-section-icon">📋</span>
          粘贴职位描述 (JD)
        </div>
        <p className="upload-section-desc">
          粘贴目标职位的描述文案，AI 将以此为标准对比你的简历
        </p>
        <div className="form-group">
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            rows={6}
            placeholder="将目标职位的描述粘贴到这里，例如：&#10;&#10;职位要求：&#10;1. 3年以上前端开发经验&#10;2. 精通 React / Vue 等主流框架&#10;3. 熟悉 TypeScript..."
          />
        </div>
      </div>

      {/* ── 错误提示 ── */}
      {error && <div className="error-box">⚠️ {error}</div>}

      {/* ── 提交按钮 ── */}
      <button
        className="btn btn-primary btn-xl btn-block"
        onClick={onAnalyze}
        disabled={loading || !resumeText.trim() || !jdText.trim()}
      >
        {loading ? (
          <>
            <span className="spinner" />
            AI 分析中...
          </>
        ) : (
          <>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
              <path d="M11 8v6"/>
              <path d="M8 11h6"/>
            </svg>
            开始分析匹配度
          </>
        )}
      </button>

      {!loading && resumeText.trim() && jdText.trim() && (
        <div className="analyze-ready-hint">
          ✅ 简历和 JD 已就绪，点击上方按钮开始分析
        </div>
      )}
    </div>
  )
}