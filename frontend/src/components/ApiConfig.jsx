import React, { useState } from 'react'

export default function ApiConfig({ onConfigured }) {
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState('https://api.openai.com/v1')
  const [model, setModel] = useState('gpt-4o')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const handle = async () => {
    if (!apiKey.trim()) { setError('请输入 API Key'); return }
    setBusy(true); setError('')
    try {
      const resp = await fetch('/api/status')
      if (!resp.ok) throw new Error('后端未启动')
      localStorage.setItem('api_configured', 'true')
      onConfigured()
    } catch {
      setError('无法连接后端服务，请确保后端已启动')
    } finally { setBusy(false) }
  }

  return (
    <div className="card fade-in" style={{ maxWidth: 520, margin: '40px auto' }}>
      <div className="card-title">⚙️ 配置 LLM API</div>
      <p className="card-sub">
        需要配置 LLM API 密钥。支持任何 OpenAI 兼容接口。
      </p>

      {error && (
        <div className="error-box"><span>❌</span><span>{error}</span></div>
      )}

      <div className="form-group">
        <label className="form-label">API Key</label>
        <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="sk-..." />
      </div>

      <div className="flex gap-12">
        <div className="form-group" style={{ flex: 1 }}>
          <label className="form-label">API 地址</label>
          <input value={baseUrl} onChange={e => setBaseUrl(e.target.value)} placeholder="https://api.openai.com/v1" />
        </div>
        <div className="form-group" style={{ flex: 1 }}>
          <label className="form-label">模型</label>
          <input value={model} onChange={e => setModel(e.target.value)} placeholder="gpt-4o" />
        </div>
      </div>

      <div className="flex justify-end mt-16">
        <button className="btn btn-primary" onClick={handle} disabled={busy}>
          {busy ? '⏳ 连接中...' : '✅ 确认配置'}
        </button>
      </div>

      <div style={{
        marginTop: 20, padding: '12px 16px', background: 'var(--slate-50)',
        borderRadius: 'var(--radius)', fontSize: 13, color: 'var(--slate-500)',
        border: '1px solid var(--slate-200)',
      }}>
        <strong>💡 提示：</strong>也可以在 <code>backend/.env</code> 中直接配置
      </div>
    </div>
  )
}