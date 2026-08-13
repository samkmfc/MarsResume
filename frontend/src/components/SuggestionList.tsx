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
  const severityColors: Record<string, string> = {
    high: '#e03131',
    medium: '#f59f00',
    low: '#2b8a3e',
  }

  return (
    <div className="suggestion-list">
      {analysisSummary && (
        <div className="summary-card">
          <div className="summary-header">
            <span>匹配度评分</span>
            <span className="score">{analysisSummary.match_score}/100</span>
          </div>
          <div className="summary-body">
            <div><strong>优势：</strong>{analysisSummary.strengths.join('、')}</div>
            <div><strong>差距：</strong>{analysisSummary.gaps.join('、')}</div>
            <div><strong>改进方向：</strong>{analysisSummary.key_improvements}</div>
          </div>
        </div>
      )}

      {suggestions.map((s) => (
        <div key={s.id} className={`suggestion-card ${s.accepted ? 'accepted' : ''}`}>
          <div className="suggestion-header">
            <span className="suggestion-section">{s.section}</span>
            <span className="suggestion-severity" style={{ color: severityColors[s.severity] }}>
              {s.severity === 'high' ? '重要' : s.severity === 'medium' ? '建议' : '可优化'}
            </span>
          </div>
          <div className="suggestion-original">
            <div className="label">原文</div>
            <div>{s.original}</div>
          </div>
          <div className="suggestion-suggested">
            <div className="label">建议修改</div>
            <div>{s.suggested}</div>
          </div>
          <div className="suggestion-reason">
            <div className="label">原因</div>
            <div>{s.reason}</div>
          </div>
          <div className="suggestion-actions">
            <button
              className={`btn ${s.accepted ? 'btn-outline' : 'btn-primary'} btn-sm`}
              onClick={() => toggleSuggestion(s.id)}
            >
              {s.accepted ? '已采纳' : '采纳'}
            </button>
          </div>
        </div>
      ))}

      <div className="suggestion-actions-bar">
        <button className="btn btn-outline" onClick={onBack}>返回修改</button>
        <button
          className="btn btn-primary"
          onClick={onExportPdf}
          disabled={loading || !suggestions.some((s) => s.accepted)}
        >
          {loading ? '导出中...' : '导出 PDF'}
        </button>
      </div>
    </div>
  )
}