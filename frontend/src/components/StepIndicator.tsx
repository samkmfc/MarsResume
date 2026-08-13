interface StepIndicatorProps {
  currentStep: number
}

export default function StepIndicator({ currentStep }: StepIndicatorProps) {
  const steps = ['输入简历', 'AI 分析', '采纳建议', '导出 PDF']
  return (
    <div className="step-indicator">
      {steps.map((s, i) => (
        <div key={i} className={`step-item ${i + 1 <= currentStep ? 'active' : ''}`}>
          <div className="step-dot">{i + 1}</div>
          <span>{s}</span>
        </div>
      ))}
    </div>
  )
}