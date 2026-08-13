export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div>
          <div className="footer-brand">火星<span>简历</span></div>
          <div className="footer-desc">
            专业的 AI 简历优化工具，帮助求职者精准对齐目标职位，提高面试邀约率。
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
          <a href="mailto:samkmfc@163.com">samkmfc@163.com</a>
          <a href="#">隐私政策</a>
          <a href="#">服务条款</a>
        </div>
      </div>
      <div className="footer-bottom">© 2026 火星简历. All rights reserved.</div>
    </footer>
  )
}