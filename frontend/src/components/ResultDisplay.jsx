import React, { useState } from 'react'

export default function ResultDisplay({ result, originalContent, onReset }) {
  const [copied, setCopied] = useState(false)
  const [showDetails, setShowDetails] = useState(false)

  const text = result?.final_text || ''
  const changes = result?.changes_summary || []
  const rr = result?.results || {}
  const s4 = rr.step4 || {}
  const s5 = rr.step5 || {}
  const checks = s5?.checks || []
  const suggestions = s5?.suggestions || []

  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <>
      {/* 优化结果对照 */}
      <div className="card slide-up">
        <div className="card-title">✨ 优化结果</div>

        <div className="result-grid">
          {/* 原内容 */}
          <div className="result-panel">
            <div className="result-panel-head">
              <span>📄 原内容</span>
              <span className="text-xs text-slate-400">
                {originalContent?.length || 0} 字
              </span>
            </div>
            <div className="result-panel-body orig">
              {originalContent || <span className="text-slate-400">未提供原内容</span>}
            </div>
          </div>
          {/* 优化后 */}
          <div className="result-panel">
            <div className="result-panel-head">
              <span>✨ 优化后</span>
              <button className="copy-btn" onClick={handleCopy}>
                {copied ? '✓ 已复制' : '📋 复制'}
              </button>
            </div>
            <div className="result-panel-body optim">
              {text || <span className="text-slate-400">暂无结果</span>}
            </div>
          </div>
        </div>
      </div>

      {/* 改动摘要 */}
      {changes.length > 0 && (
        <div className="card fade-in" style={{ animationDelay: '0.15s' }}>
          <div className="card-title">📋 关键改动</div>
          <ul className="diff-list">
            {changes.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        </div>
      )}

      {/* 详细流程 */}
      <div className="card fade-in" style={{ animationDelay: '0.3s' }}>
        <button
          className="btn btn-ghost w-full"
          onClick={() => setShowDetails(!showDetails)}
          style={{ justifyContent: 'center' }}
        >
          {showDetails ? '收起详细流程' : '查看 5 步详细流程'}
        </button>

        {showDetails && (
          <div className="mt-16 fade-in">
            {/* Step 4 */}
            {s4?.issues?.length > 0 && (
              <div className="mb-16">
                <div className="card-title" style={{ fontSize: 14, marginBottom: 10 }}>
                  🔬 技术指标准确性检查
                </div>
                {s4.issues.map((issue, i) => (
                  <div key={i} className="issue-card">
                    <div><strong>原文：</strong>{issue.original}</div>
                    <div><strong>建议：</strong>{issue.suggestion}</div>
                    <div className="text-xs text-slate-500 mt-8">{issue.reason}</div>
                  </div>
                ))}
              </div>
            )}
            {s4?.has_issues === false && (
              <div style={{
                background: 'var(--success-bg)', borderLeft: '3px solid var(--success)',
                padding: '10px 14px', borderRadius: 'var(--radius)', marginBottom: 16,
                fontSize: 13, color: 'var(--success)',
              }}>
                ✅ 技术指标检查通过
              </div>
            )}

            {/* Step 5 */}
            {checks.length > 0 && (
              <div className="mb-16">
                <div className="card-title" style={{ fontSize: 14, marginBottom: 10 }}>
                  ✅ 交付前自检 {s5?.passed ? '✓ 全部通过' : '⚠ 需改进'}
                </div>
                <div className="check-grid">
                  {checks.map((ch, i) => (
                    <div key={i} className={`check-item ${ch.result === '通过' ? 'pass' : 'fail'}`}>
                      {ch.result === '通过' ? '✓' : '✗'} {ch.item}
                      {ch.detail && <span className="text-xs" style={{ opacity: 0.7 }}> — {ch.detail}</span>}
                    </div>
                  ))}
                </div>
                {suggestions.length > 0 && (
                  <div className="mt-12 text-sm text-slate-600">
                    <strong>改进建议：</strong>
                    <ul className="mt-8" style={{ paddingLeft: 16 }}>
                      {suggestions.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 操作 */}
      <div className="flex justify-center mt-24">
        <button className="btn btn-primary btn-lg" onClick={onReset}>
          🔄 继续优化其他模块
        </button>
      </div>
    </>
  )
}