import React, { useRef } from 'react'

export default function ResumeInput({
  resumeText, setResumeText,
  uploadedFile, setUploadedFile,
  setFileId, setFileExt,
  jdText, setJdText,
  onUpload, onAnalyze,
  loading, error,
}) {
  const fileInputRef = useRef(null)

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const valid = ['.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg']
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    if (!valid.includes(ext)) {
      alert(`不支持的文件格式: ${ext}`)
      return
    }
    await onUpload(file)
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) await onUpload(file)
  }
  const handleDragOver = (e) => e.preventDefault()

  const clearFile = () => {
    setResumeText('')
    setUploadedFile(null)
    setFileId('')
    setFileExt('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="card fade-in">
      <div className="card-title">📄 上传简历 + 输入 JD</div>
      <p className="card-sub">
        上传简历文件（PDF / Word / 图片），或直接粘贴文本。
        然后粘贴目标职位描述，AI 将进行对齐分析。
      </p>

      {error && (
        <div className="error-box"><span>❌</span><span>{error}</span></div>
      )}

      {/* 文件上传 */}
      <div
        className="form-group"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        style={{
          border: '2px dashed var(--slate-200)',
          borderRadius: 'var(--radius)', padding: '32px 20px',
          textAlign: 'center', cursor: 'pointer',
          transition: 'border-color 0.2s, background 0.2s',
          background: uploadedFile ? 'var(--primary-50)' : 'var(--slate-50)',
        }}
        onClick={() => fileInputRef.current?.click()}
      >
        <input ref={fileInputRef} type="file" accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
          onChange={handleFileChange} style={{ display: 'none' }} />
        {uploadedFile ? (
          <div>
            <div style={{ fontSize: 32, marginBottom: 8 }}>📎</div>
            <div style={{ fontWeight: 600, color: 'var(--primary-700)' }}>{uploadedFile.name}</div>
            <div className="text-xs text-slate-400 mt-8">
              文本已提取 ({resumeText.length} 字符)
            </div>
            <button className="btn btn-sm btn-ghost mt-8"
              onClick={(e) => { e.stopPropagation(); clearFile() }}>清除文件</button>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: 36, marginBottom: 8 }}>📤</div>
            <div style={{ fontWeight: 500, color: 'var(--slate-600)' }}>点击或拖拽上传简历</div>
            <div className="text-xs text-slate-400 mt-8">支持 PDF · Word · PNG · JPG（最大 10MB）</div>
          </div>
        )}
      </div>

      {/* 简历文本 */}
      <div className="form-group" style={{ marginTop: 20 }}>
        <label className="form-label">简历文本</label>
        <textarea value={resumeText} onChange={e => setResumeText(e.target.value)}
          placeholder="上传文件后将自动提取文本，你也可以直接粘贴..."
          rows={8} style={{ minHeight: 160 }} />
        <div className="form-hint">{resumeText.length > 0 ? `${resumeText.length} 字符` : ''}</div>
      </div>

      {/* JD */}
      <div className="form-group">
        <label className="form-label">📋 目标职位描述 (JD)</label>
        <textarea value={jdText} onChange={e => setJdText(e.target.value)}
          placeholder="粘贴目标职位的招聘要求/职位描述..."
          rows={6} style={{ minHeight: 120, borderColor: jdText ? 'var(--primary-200)' : undefined }} />
        <div className="form-hint">{jdText.length > 0 ? `${jdText.length} 字符` : '输入 JD 让 AI 精准对齐招聘需求'}</div>
      </div>

      {/* 操作 */}
      <div className="flex justify-end mt-16" style={{ gap: 12 }}>
        <button className="btn btn-primary btn-lg"
          onClick={onAnalyze}
          disabled={loading || !resumeText.trim() || !jdText.trim()}>
          {loading ? <><span className="spinner" />分析中...</> : '🔍 开始 JD 对齐分析'}
        </button>
      </div>
    </div>
  )
}