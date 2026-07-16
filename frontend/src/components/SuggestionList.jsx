import React from 'react'

export default function SuggestionList({ suggestions, toggleSuggestion, onExportPdf, onBack, loading, analysisSummary }) {
  const accepted = suggestions.filter(s => s.accepted).length
  const total = suggestions.length

  return (
    <>
      {/* 匹配概览 */}
      {analysisSummary && (
        <div className="card fade-in">
          <div className="card-title">📊 匹配概览</div>
          <div className="flex gap-20 items-center" style={{ marginBottom: 16 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 36, fontWeight: 700, color: 'var(--primary-700)' }}>
                {analysisSummary.match_score || '?'}%
              </div>
              <div className="text-xs text-slate-500">匹配度</div>
            </div>
            <div style={{ flex: 1 }}>
              <div className="text-sm font-semibold text-slate-700 mb-8">✅ 优势</div>
              {(analysisSummary.strengths || []).map((s, i) => (
                <div key={i} className="text-sm text-slate-600" style={{ marginBottom: 2 }}>· {s}</div>
              ))}
              <div className="text-sm font-semibold text-slate-700 mt-8 mb-8">⚠️ 差距</div>
              {(analysisSummary.gaps || []).map((g, i) => (
                <div key={i} className="text-sm text-slate-600" style={{ marginBottom: 2 }}>· {g}</div>
              ))}
            </div>
          </div>
          {analysisSummary.key_improvements && (
            <div style={{
              background: 'var(--primary-50)', padding: '10px 14px',
              borderRadius: 'var(--radius)', fontSize: 13, color: 'var(--primary-700)',
            }}>
              <strong>🎯 关键改进方向：</strong> {analysisSummary.key_improvements}
            </div>
          )}
        </div>
      )}

      {/* 修改建议列表 */}
      <div className="card slide-up">
        <div className="card-title">
          ✏️ 修改建议
          <span className="text-sm text-slate-400" style={{ fontWeight: 400 }}>
            ({accepted}/{total} 已采纳)
          </span>
        </div>

        <div className="flex gap-8 mb-16" style={{ flexWrap: 'wrap' }}>
          <button
            className={`btn btn-sm ${accepted === total ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => suggestions.forEach(s => !s.accepted && toggleSuggestion(s.id))}
            disabled={accepted === total}
          >
            全部采纳
          </button>
          <button
            className={`btn btn-sm ${accepted === 0 ? 'btn-ghost' : 'btn-ghost'}`}
            onClick={() => suggestions.forEach(s => s.accepted && toggleSuggestion(s.id))}
            disabled={accepted === 0}
          >
            全部取消
          </button>
          <span className="text-xs text-slate-400" style={{ alignSelf: 'center' }}>
            点击每条建议可单独采纳/拒绝
          </span>
        </div>

        {suggestions.map((s, i) => (
          <div
            key={s.id || i}
            className="fade-in"
            style={{
              border: `1.5px solid ${s.accepted ? 'var(--primary-200)' : 'var(--slate-200)'}`,
              borderRadius: 'var(--radius)',
              marginBottom: 12,
              overflow: 'hidden',
              transition: 'border-color 0.2s',
              background: s.accepted ? 'var(--primary-50)' : '#fff',
            }}
          >
            {/* 头部 */}
            <div
              className="flex justify-between items-center"
              style={{
                padding: '10px 14px',
                background: s.accepted ? 'var(--primary-100)' : 'var(--slate-50)',
                borderBottom: '1px solid var(--slate-200)',
                cursor: 'pointer',
              }}
              onClick={() => toggleSuggestion(s.id)}
            >
              <div className="flex gap-8 items-center">
                <span className={`badge ${s.severity === 'high' ? 'badge-warn' : 'badge-ok'}`}
                  style={{ fontSize: 11, padding: '2px 8px' }}>
                  {s.severity === 'high' ? '重要' : s.severity === 'medium' ? '建议' : '可选'}
                </span>
                <span className="text-xs font-semibold text-slate-500">{s.section}</span>
              </div>
              <span style={{
                fontSize: 20,
                color: s.accepted ? 'var(--success)' : 'var(--slate-300)',
                transition: 'color 0.2s',
              }}>
                {s.accepted ? '✅' : '⬜'}
              </span>
            </div>

            {/* 内容 */}
            <div style={{ padding: '12px 14px' }}>
              <div className="text-xs text-slate-400 mb-4">原文</div>
              <div style={{
                background: '#fefce8', padding: '8px 10px',
                borderRadius: 'var(--radius-sm)', fontSize: 13, marginBottom: 8,
                color: 'var(--slate-700)',
              }}>{s.original}</div>

              <div className="text-xs text-slate-400 mb-4">建议修改</div>
              <div style={{
                background: 'var(--success-bg)', padding: '8px 10px',
                borderRadius: 'var(--radius-sm)', fontSize: 13, marginBottom: 8,
                color: 'var(--slate-700)',
              }}>{s.suggested}</div>

              <div className="text-xs text-slate-500" style={{ marginTop: 4 }}>
                <strong>原因：</strong>{s.reason}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 操作按钮 */}
      <div className="flex justify-between items-center mt-8">
        <button className="btn btn-ghost" onClick={onBack}>← 返回修改简历</button>
        <button
          className="btn btn-primary btn-lg"
          onClick={onExportPdf}
          disabled={loading || accepted === 0}
        >
          {loading ? (
            <><span className="spinner" />生成中...</>
          ) : (
            '📄 导出修改后的 PDF'
          )}
        </button>
      </div>
    </>
  )
}