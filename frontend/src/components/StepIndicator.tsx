interface StepIndicatorProps {
  currentStep: number
}

const STEPS = [
  { num: 1, label: '上传简历', desc: 'PDF / Word / 图片' },
  { num: 2, label: 'AI 分析', desc: '智能匹配 JD' },
  { num: 3, label: '采纳建议', desc: '逐条挑选修改' },
  { num: 4, label: '导出 PDF', desc: '一键下载' },
]

export default function StepIndicator({ currentStep }: StepIndicatorProps) {
  return (
    <div className="steps-row">
      {STEPS.map((s, i) => {
        const status = currentStep > s.num ? 'done' : currentStep === s.num ? 'active' : ''
        return (
          <>
            {i > 0 && <div className={`step-line ${currentStep > i ? 'done' : ''}`} />}
            <div key={s.num} className={`step-item ${status}`}>
              <div className="step-dot">
                {currentStep > s.num ? '✓' : s.num}
              </div>
              <span className="step-label">{s.label}</span>
            </div>
          </>
        )
      })}
    </div>
  )
}