import React, { useState, useRef, useEffect } from 'react'

export default function QuestionFlow({ questions, knownInfo, onSubmit, onBack, loading, streaming, streamingText, error }) {
  const [answers, setAnswers] = useState('')
  const taRef = useRef(null)
  const endRef = useRef(null)

  useEffect(() => {
    if (taRef.current && !streaming) taRef.current.focus()
  }, [streaming])

  useEffect(() => {
    if (endRef.current) endRef.current.scrollIntoView({ behavior: 'smooth' })
  }, [streamingText])

  const handleSubmit = () => {
    if (!answers.trim()) return
    onSubmit(answers)
  }

  const handleKey = (e) => {
    if (e.ctrlKey && e.key === 'Enter') handleSubmit()
  }

  return (
    <div className="card slide-up">
      <div className="card-title">
        💬 项目深挖 — 补充信息
      </div>
      <p className="card-sub">
        根据你的简历，AI 还需要了解以下信息才能写出高质量的优化版本。
        请逐条回答，尽量提供具体项目名、量化数据和工具细节。
      </p>

      {error && (
        <div className="error-box">
          <span>❌</span>
          <span>{error}</span>
        </div>
      )}

      {/* 已知信息 */}
      {knownInfo && (
        <div className="info-box">
          <strong>✅ 简历中已有的信息</strong>
          {knownInfo}
        </div>
      )}

      {/* 问题列表 */}
      <div className="mb-16">
        <div className="form-label" style={{ marginBottom: 10 }}>需要补充的问题</div>
        {questions.map((q, i) => (
          <div key={i} className="q-item fade-in" style={{ animationDelay: `${i * 0.07}s` }}>
            <div className="q-label">问题 {i + 1}</div>
            <div className="q-text">{q}</div>
          </div>
        ))}
      </div>

      {/* 回答输入 */}
      <div className="form-group">
        <label className="form-label">你的回答</label>
        <textarea
          ref={taRef}
          value={answers}
          onChange={e => setAnswers(e.target.value)}
          onKeyDown={handleKey}
          placeholder="请逐条回答上面的问题，尽量提供具体信息..."
          rows={6}
          disabled={loading}
        />
        <div className="form-hint">
          Ctrl+Enter 快速提交 · 提供具体项目名、量化数据能让优化效果更好
        </div>
      </div>

      {/* 流式生成 */}
      {streaming && (
        <div className="fade-in" style={{ marginBottom: 16 }}>
          <div className="flex gap-8 items-center" style={{ fontSize: 14, fontWeight: 600, color: 'var(--slate-700)', marginBottom: 10 }}>
            <span className="spinner" />
            AI 正在实时生成...
          </div>
          <div className="stream-box">
            {streamingText || '正在准备生成...'}
            <span className="cursor" />
            <div ref={endRef} />
          </div>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex justify-end gap-12">
        <button className="btn btn-ghost" onClick={onBack} disabled={loading}>
          ← 返回修改
        </button>
        <button
          className="btn btn-primary btn-lg"
          onClick={handleSubmit}
          disabled={loading || !answers.trim()}
        >
          {streaming ? (
            <><span className="spinner" />生成中...</>
          ) : loading ? (
            '⏳ 分析中...'
          ) : (
            '🚀 生成优化结果'
          )}
        </button>
      </div>
    </div>
  )
}