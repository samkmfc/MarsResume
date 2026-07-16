import React from 'react'

const STEPS = [
  { num: 1, label: '上传简历 + JD' },
  { num: 2, label: '对齐分析' },
  { num: 3, label: '采纳建议' },
]

export default function StepIndicator({ currentStep }) {
  return (
    <div className="steps-row">
      {STEPS.map((s, i) => {
        const done = currentStep > s.num
        const active = currentStep === s.num
        const cls = `step-item${active ? ' active' : ''}${done ? ' done' : ''}`
        return (
          <React.Fragment key={s.num}>
            <div className={cls}>
              <div className="step-dot">{done ? '✓' : s.num}</div>
              <span className="step-label">{s.label}</span>
            </div>
            {i < STEPS.length - 1 && <div className={`step-line${done ? ' done' : ''}`} />}
          </React.Fragment>
        )
      })}
    </div>
  )
}