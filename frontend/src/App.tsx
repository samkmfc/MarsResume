import { useEffect } from 'react'
import { useAppStore } from './stores/appStore'
import Header from './components/Header'
import FeatureGrid from './components/FeatureGrid'
import StepIndicator from './components/StepIndicator'
import ResumeInput from './components/ResumeInput'
import SuggestionList from './components/SuggestionList'
import Footer from './components/Footer'
import FAQ from './components/FAQ'

function WorkflowSection() {
  const {
    step, setStep, apiReady,
    resumeText, setResumeText, uploadedFile, setUploadedFile,
    setFileId, setFileExt, jdText, setJdText,
    suggestions, analysisSummary, toggleSuggestion, exportPdf,
    loading, error, uploadFile, analyze,
  } = useAppStore()

  if (apiReady === null) return null

  // Beta 阶段：API 未配置时也不阻塞，显示提示条即可
  return (
    <div className="tool-container">
      {/* 工作流步骤指示器 */}
      {step >= 1 && <StepIndicator currentStep={step} />}

      {/* Step 0: 欢迎/开始 */}
      {step === 0 && (
        <div className="card text-center" style={{ padding: 48 }}>
          <h3 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>开始优化你的简历</h3>
          <p className="text-slate-500 text-sm" style={{ marginBottom: 24, maxWidth: 400, margin: '0 auto 24px' }}>
            上传简历 + 粘贴目标 JD，AI 将逐条分析并给出精准修改建议
          </p>
          <button className="btn btn-primary btn-xl" onClick={() => setStep(1)}>
            立即开始
          </button>
        </div>
      )}

      {/* Step 1: 上传简历 + 输入 JD */}
      {step === 1 && (
        <ResumeInput
          resumeText={resumeText}
          setResumeText={setResumeText}
          uploadedFile={uploadedFile}
          setUploadedFile={setUploadedFile}
          setFileId={setFileId}
          setFileExt={setFileExt}
          jdText={jdText}
          setJdText={setJdText}
          onUpload={uploadFile}
          onAnalyze={analyze}
          loading={loading}
          error={error}
        />
      )}

      {/* Step 3: 结果展示 */}
      {step === 3 && (
        <SuggestionList
          suggestions={suggestions}
          toggleSuggestion={toggleSuggestion}
          onExportPdf={exportPdf}
          onBack={() => setStep(1)}
          loading={loading}
          analysisSummary={analysisSummary}
        />
      )}
    </div>
  )
}

export default function App() {
  const { step, setStep, checkApiStatus } = useAppStore()
  useEffect(() => { checkApiStatus() }, [checkApiStatus])

  return (
    <>
      <Header onStart={() => setStep(1)} />

      <section className="hero">
        <div className="hero-inner">
          <h1 className="hero-title">
            让你的简历与 <span className="gradient">JD 精准对齐</span>
          </h1>
          <p className="hero-sub">
            上传简历 + 粘贴职位描述，AI 逐条分析差距并给出修改建议。
            采纳后一键导出排版一致的 PDF。
          </p>

          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat-num">5万+</div>
              <div className="hero-stat-label">简历优化</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-num">98%</div>
              <div className="hero-stat-label">面试邀约率</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-num">3min</div>
              <div className="hero-stat-label">完成优化</div>
            </div>
          </div>

          <div className="card" style={{ maxWidth: 780, margin: '0 auto' }}>
            <div className="card-title" style={{ justifyContent: 'center' }}>📤 上传你的简历</div>
            <WorkflowSection />
          </div>

          <div className="scroll-arrow" onClick={() => document.getElementById('steps')?.scrollIntoView({ behavior: 'smooth' })}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 4v10M10 14l5-5M10 14l-5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </div>
      </section>

      <FeatureGrid />
      <FAQ items={[
        { q: '支持哪些文件格式？', a: '支持 PDF、Word (.docx)、图片 (PNG/JPG) 格式上传。' },
        { q: '优化需要多长时间？', a: 'AI 分析通常在 10-30 秒内完成。' },
        { q: '修改建议准确吗？', a: '每条建议都基于 JD 要求 + 简历内容的深度对比生成。' },
        { q: '导出 PDF 排版会乱吗？', a: 'Word 格式上传的简历，排版与原文件完全一致。' },
      ]} />
      <Footer />
    </>
  )
}