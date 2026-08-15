import type { Suggestion, Summary } from '../types'

interface SuggestionListProps {
  suggestions: Suggestion[]
  toggleSuggestion: (id: string) => void
  onExportPdf: () => Promise<void>
  onBack: () => void
  loading: boolean
  analysisSummary: Summary | null
}

export default function SuggestionList({
  suggestions, toggleSuggestion, onExportPdf, onBack, loading, analysisSummary,
}: SuggestionListProps) {
  const severityLabels: Record<string, string> = {
    high: '重要',
    medium: '建议',
    low: '可优化',
  }
  const severityBadge: Record<string, string> = {
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low',
  }

  const acceptedCount = suggestions.filter((s) => s.accepted).length

  return (
    <div className="suggestion-list">
      {/* ── 匹配度摘要 ── */}
      {analysisSummary && (
        <div className="match-summary-card">
          <div className="match-summary-top">
            <div className="match-summary-label">匹配度评分</div>
            <div className="match-summary-score">{analysisSummary.match_score}</div>
          </div>
          <div className="match-summary-body">
            <div className="match-summary-item">
              <span className="match-summary-item-label">✅ 优势</span>
              <span>{analysisSummary.strengths.join('、')}</span>
            </div>
            <div className="match-summary-item">
              <span className="match-summary-item-label">⚠️ 差距</span>
              <span>{analysisSummary.gaps.join('、')}</span>
            </div>
            <div className="match-summary-item">
              <span className="match-summary-item-label">🎯 改进方向</span>
              <span>{analysisSummary.key_improvements}</span>
            </div>
          </div>
        </div>
      )}

      {/* ── 操作栏 ── */}
      <div className="results-toolbar">
        <div className="results-toolbar-info">
          <span className="results-count">{suggestions.length} 条修改建议</span>
          {acceptedCount > 0 && (
            <span className="results-accepted">已采纳 {acceptedCount} 条</span>
          )}
        </div>
        <div className="results-toolbar-actions">
          <button className="btn btn-ghost" onClick={onBack}>
            ← 返回修改
          </button>
          <button
            className="btn btn-primary"
            onClick={onExportPdf}
            disabled={loading || acceptedCount === 0}
          >
            {loading ? (
              <>
                <span className="spinner" /> 导出中...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                {acceptedCount > 0 ? `导出 PDF (${acceptedCount} 条)` : '导出 PDF'}
              </>
            )}
          </button>
        </div>
      </div>

      {/* ── 建议列表 ── */}
      {suggestions.map((s) => (
        <div key={s.id} className={`suggestion-card ${s.accepted ? 'accepted' : ''}`}>
          <div className="suggestion-head">
            <div className="suggestion-head-left">
              <span className="suggestion-section-tag">{s.section}</span>
              <span className={`badge ${severityBadge[s.severity]}`}>
                {severityLabels[s.severity]}
              </span>
            </div>
            <button
              className={`btn ${s.accepted ? 'btn-outline-primary' : 'btn-primary'} btn-sm`}
              onClick={() => toggleSuggestion(s.id)}
            >
              {s.accepted ? '✓ 已采纳' : '采纳'}
            </button>
          </div>
          <div className="suggestion-body">
            <div className="suggestion-diff">
              <div className="suggestion-diff-item original">
                <div className="suggestion-diff-label">原文</div>
                <div className="suggestion-diff-text">{s.original}</div>
              </div>
              <div className="suggestion-diff-arrow">→</div>
              <div className="suggestion-diff-item suggested">
                <div className="suggestion-diff-label">建议修改</div>
                <div className="suggestion-diff-text">{s.suggested}</div>
              </div>
            </div>
            <div className="suggestion-reason">
              <span className="suggestion-reason-icon">💡</span>
              {s.reason}
            </div>
          </div>
        </div>
      ))}

      {/* ── 底部操作 ── */}
      {suggestions.length > 0 && (
        <div className="results-bottom-bar">
          <button className="btn btn-ghost btn-lg" onClick={onBack}>← 返回修改</button>
          <button
            className="btn btn-primary btn-lg"
            onClick={onExportPdf}
            disabled={loading || acceptedCount === 0}
          >
            {loading ? (
              <>
                <span className="spinner" /> 导出中...
              </>
            ) : (
              `📎 导出 PDF${acceptedCount > 0 ? ` (${acceptedCount} 条建议)` : ''}`
            )}
          </button>
        </div>
      )}
    </div>
  )
}