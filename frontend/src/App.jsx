import React, { useEffect, useState } from 'react'
import { FormProvider, useFormContext } from './context/FormContext'
import StepIndicator from './components/StepIndicator'
import ResumeInput from './components/ResumeInput'
import SuggestionList from './components/SuggestionList'
import ApiConfig from './components/ApiConfig'

function WorkflowSection() {
  const {
    step, setStep, apiReady, handleConfigured,
    resumeText, setResumeText, uploadedFile, setUploadedFile,
    setFileId, setFileExt, jdText, setJdText,
    suggestions, analysisSummary, toggleSuggestion, handleExportPdf,
    loading, error, handleUploadFile, handleAnalyze,
  } = useFormContext()

  if (apiReady === null) {
    return null // 正在检查 API 状态
  }
  if (apiReady === false) {
    return <ApiConfig onConfigured={handleConfigured} />
  }

  return (
    <div className="tool-container">
      {step >= 1 && <StepIndicator currentStep={step} />}

      {step === 0 && (
        <div className="card text-center" style={{ padding: 48 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}></div>
          <h3 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>开始优化你的简历</h3>
          <p className="text-slate-500 text-sm" style={{ marginBottom: 24, maxWidth: 400, margin: '0 auto 24px' }}>
            上传简历 + 粘贴目标 JD，AI 将逐条分析并给出精准修改建议
          </p>
          <button className="btn btn-primary btn-xl" onClick={() => setStep(1)}>
            立即开始
          </button>
        </div>
      )}

      {step === 1 && (
        <ResumeInput
          resumeText={resumeText} setResumeText={setResumeText}
          uploadedFile={uploadedFile} setUploadedFile={setUploadedFile}
          setFileId={setFileId} setFileExt={setFileExt}
          jdText={jdText} setJdText={setJdText}
          onUpload={handleUploadFile} onAnalyze={handleAnalyze}
          loading={loading} error={error}
        />
      )}

      {step === 3 && (
        <SuggestionList
          suggestions={suggestions}
          toggleSuggestion={toggleSuggestion}
          onExportPdf={handleExportPdf}
          onBack={() => setStep(1)}
          loading={loading}
          analysisSummary={analysisSummary}
        />
      )}
    </div>
  )
}

// ── FAQ 组件 ──
function FAQ({ items }) {
  const [openIdx, setOpenIdx] = useState(null)
  return (
    <div className="faq-list">
      {items.map((item, i) => (
        <div key={i} className="faq-item">
          <div className={`faq-q${openIdx === i ? ' open' : ''}`} onClick={() => setOpenIdx(openIdx === i ? null : i)}>
            {item.q}
            <span className="faq-arrow">▼</span>
          </div>
          {openIdx === i && <div className="faq-a">{item.a}</div>}
        </div>
      ))}
    </div>
  )
}

// ── 主应用 ──
function AppContent() {
  const { step, setStep, checkApiStatus } = useFormContext()
  useEffect(() => { checkApiStatus() }, [checkApiStatus])

  return (
    <>
      {/* ── Header ── */}
      <header className="header">
        <div className="header-inner">
          <a className="header-logo" href="/">
            <img src="/Mars.png" alt="火星简历" className="header-logo-img" />
            <span className="header-logo-text">火星<span>简历</span></span>
          </a>
          <nav className="header-nav">
            <a href="#" className="active">首页</a>
            <a href="#">AI简历优化</a>
            <a href="#">AI简历打分</a>
          </nav>
          <div className="header-actions">
            <span className="badge-status online">
              <span className="badge-dot" /> 系统就绪
            </span>
            <button className="btn btn-primary" onClick={() => setStep(1)}>开始制作</button>
          </div>
        </div>
      </header>

      {/* ── Hero Section ── */}
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
        </div>
      </section>

      {/* ── 三大步骤 ── */}
      <section className="section section-alt">
        <div className="section-inner">
          <h2 className="section-title">三步搞定简历优化</h2>
          <p className="section-sub">上传简历 → AI 对齐分析 → 采纳建议导出 PDF</p>
          <div className="steps-grid">
            <div className="step-card">
              <div className="step-num">01</div>
              <div className="step-title">上传简历 + 粘贴 JD</div>
              <div className="step-desc">支持 PDF、Word、图片格式，粘贴目标职位描述</div>
            </div>
            <div className="step-card">
              <div className="step-num">02</div>
              <div className="step-title">AI 逐条分析优化</div>
              <div className="step-desc">AI 逐条对比简历与 JD，给出精准的修改建议</div>
            </div>
            <div className="step-card">
              <div className="step-num">03</div>
              <div className="step-title">采纳建议导出 PDF</div>
              <div className="step-desc">每条建议可单独采纳/拒绝，一键导出排版一致的 PDF</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 功能亮点 ── */}
      <section className="section">
        <div className="section-inner">
          <h2 className="section-title">核心功能</h2>
          <p className="section-sub">覆盖简历优化的每一个关键环节</p>
          <div className="feature-grid">
            <div className="feature-card">
              <div className="feature-icon purple">🎯</div>
              <div className="feature-title">JD 精准对齐</div>
              <div className="feature-desc">AI 深度对比简历与职位描述，逐条找出差距和优化方向</div>
            </div>
            <div className="feature-card">
              <div className="feature-icon amber">✏️</div>
              <div className="feature-title">逐条修改建议</div>
              <div className="feature-desc">每条建议显示原文→改法→原因，可单独采纳或拒绝</div>
            </div>
            <div className="feature-card">
              <div className="feature-icon emerald">📄</div>
              <div className="feature-title">保留原始排版</div>
              <div className="feature-desc">基于原始 Word 文件修改，导出 PDF 与原文档排版一致</div>
            </div>
            <div className="feature-card">
              <div className="feature-icon sky">⚡</div>
              <div className="feature-title">一键导出 PDF</div>
              <div className="feature-desc">采纳建议后一键下载修改后的 PDF 简历，即改即用</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 适用场景 ── */}
      <section className="section section-alt">
        <div className="section-inner">
          <h2 className="section-title">满足多样化求职场景</h2>
          <p className="section-sub">无论你是求职新人还是职场老手，都能找到适合的方案</p>
          <div className="scenario-grid">
            <div className="scenario-card">
              <div className="scenario-icon">🎓</div>
              <div className="scenario-title">应届生求职</div>
              <div className="scenario-desc">缺乏工作经验？AI 帮你挖掘校园经历和项目中的亮点，匹配目标岗位要求。</div>
            </div>
            <div className="scenario-card">
              <div className="scenario-icon">🚀</div>
              <div className="scenario-title">职场晋升跳槽</div>
              <div className="scenario-desc">工作多年经历丰富？AI 帮你梳理核心竞争力，量化工作成果。</div>
            </div>
            <div className="scenario-card">
              <div className="scenario-icon">🔄</div>
              <div className="scenario-title">跨行业转行</div>
              <div className="scenario-desc">转行困难？AI 帮你匹配目标岗位关键词，重构简历逻辑提升匹配度。</div>
            </div>
            <div className="scenario-card">
              <div className="scenario-icon">✨</div>
              <div className="scenario-title">简历翻新升级</div>
              <div className="scenario-desc">简历样式过时？AI 帮你优化措辞，让简历焕然一新专业度倍增。</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="section">
        <div className="section-inner">
          <h2 className="section-title">常见问题</h2>
          <p className="section-sub">关于简历优化，你可能想了解这些</p>
          <FAQ items={[
            { q: '支持哪些文件格式？', a: '支持 PDF、Word (.docx)、图片 (PNG/JPG) 格式上传。Word 格式可保留原始排版导出 PDF，其他格式同样可以提取文字进行 AI 优化。' },
            { q: '优化需要多长时间？', a: 'AI 分析通常在 10-30 秒内完成。上传文件后粘贴目标 JD，点击分析按钮即可获得逐条修改建议。' },
            { q: '修改建议准确吗？', a: '每条建议都基于 JD 要求 + 简历内容的深度对比生成，并附带修改原因。你可以逐条审阅，自由采纳或拒绝。' },
            { q: '导出 PDF 排版会乱吗？', a: 'Word 格式上传的简历，我们基于原始文件做精确文本替换后通过 Word 引擎导出 PDF，排版与原文件完全一致。' },
          ]} />
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="footer">
        <div className="footer-inner">
          <div>
            <div className="footer-brand">火星<span>简历</span></div>
            <div className="footer-desc">
              专业的 AI 简历优化工具，帮助求职者精准对齐目标职位，提高面试邀约率。
              已服务 5 万+ 求职者。
            </div>
          </div>
          <div>
            <div className="footer-title">产品</div>
            <a href="#">AI简历优化</a>
            <a href="#">AI简历打分</a>
            <a href="#">JD对齐分析</a>
          </div>
          <div>
            <div className="footer-title">支持</div>
            <a href="#">samkmfc@163.com</a>
            <a href="#">隐私政策</a>
            <a href="#">服务条款</a>
          </div>
        </div>
        <div className="footer-bottom">© 2026 火星简历. All rights reserved.</div>
      </footer>
    </>
  )
}

export default function App() {
  return (
    <FormProvider>
      <AppContent />
    </FormProvider>
  )
}