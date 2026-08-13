import { useRef } from 'react'

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

export default function ResumeInput({
  resumeText, setResumeText, uploadedFile, setUploadedFile,
  setFileId, setFileExt, jdText, setJdText,
  onUpload, onAnalyze, loading, error,
}: ResumeInputProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadedFile({ name: file.name, format: file.name.split('.').pop() || '' })
    await onUpload(file)
  }

  return (
    <div className="resume-input">
      <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.png,.jpg,.jpeg"
          hidden
          onChange={handleFileChange}
        />
        {uploadedFile ? (
          <div className="uploaded-file">
            📄 {uploadedFile.name}
            <button className="btn btn-sm" onClick={(e) => { e.stopPropagation(); setUploadedFile(null); setFileId(''); setFileExt('') }}>
              更换
            </button>
          </div>
        ) : (
          <div className="upload-placeholder">
            <div className="upload-icon">📤</div>
            <div>点击上传简历（PDF / Word / 图片）</div>
          </div>
        )}
      </div>

      {resumeText && (
        <div className="form-group">
          <label>简历文本（可编辑）</label>
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            rows={8}
            placeholder="简历文本将在此显示..."
          />
        </div>
      )}

      <div className="form-group">
        <label>粘贴职位描述 (JD)</label>
        <textarea
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          rows={6}
          placeholder="将目标职位的描述粘贴到这里..."
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      <button
        className="btn btn-primary btn-block"
        onClick={onAnalyze}
        disabled={loading || !resumeText.trim() || !jdText.trim()}
      >
        {loading ? '分析中...' : '开始分析'}
      </button>
    </div>
  )
}