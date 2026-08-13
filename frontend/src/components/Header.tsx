interface HeaderProps {
  onStart: () => void
}

export default function Header({ onStart }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-inner">
        <a className="header-logo" href="/">
          <img src="/new2.png" alt="火星简历" className="header-logo-img" />
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
          <button className="btn btn-primary" onClick={onStart}>开始制作</button>
        </div>
      </div>
    </header>
  )
}