export default function FeatureGrid() {
  const features = [
    { icon: '🎯', title: 'JD 精准对齐', desc: 'AI 深度对比简历与职位描述，逐条找出差距和优化方向', color: 'purple' },
    { icon: '✏️', title: '逐条修改建议', desc: '每条建议显示原文→改法→原因，可单独采纳或拒绝', color: 'amber' },
    { icon: '📄', title: '保留原始排版', desc: '基于原始 Word 文件修改，导出 PDF 与原文档排版一致', color: 'emerald' },
    { icon: '⚡', title: '一键导出 PDF', desc: '采纳建议后一键下载修改后的 PDF 简历，即改即用', color: 'sky' },
  ]

  return (
    <>
      <section id="steps" className="section section-alt">
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

      <section className="section">
        <div className="section-inner">
          <h2 className="section-title">核心功能</h2>
          <p className="section-sub">覆盖简历优化的每一个关键环节</p>
          <div className="feature-grid">
            {features.map((f, i) => (
              <div key={i} className="feature-card">
                <div className={`feature-icon ${f.color}`}>{f.icon}</div>
                <div className="feature-title">{f.title}</div>
                <div className="feature-desc">{f.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section section-alt">
        <div className="section-inner">
          <h2 className="section-title">满足多样化求职场景</h2>
          <p className="section-sub">无论你是求职新人还是职场老手，都能找到适合的方案</p>
          <div className="scenario-grid">
            {[
              { icon: '🎓', title: '应届生求职', desc: '缺乏工作经验？AI 帮你挖掘校园经历和项目中的亮点。' },
              { icon: '🚀', title: '职场晋升跳槽', desc: '工作多年经历丰富？AI 帮你梳理核心竞争力。' },
              { icon: '🔄', title: '跨行业转行', desc: '转行困难？AI 帮你匹配目标岗位关键词。' },
              { icon: '✨', title: '简历翻新升级', desc: '简历样式过时？AI 帮你优化措辞。' },
            ].map((s, i) => (
              <div key={i} className="scenario-card">
                <div className="scenario-icon">{s.icon}</div>
                <div className="scenario-title">{s.title}</div>
                <div className="scenario-desc">{s.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}