import { useState } from 'react'

interface FAQItem {
  q: string
  a: string
}

interface FAQProps {
  items: FAQItem[]
}

export default function FAQ({ items }: FAQProps) {
  const [openIdx, setOpenIdx] = useState<number | null>(null)

  return (
    <section className="section">
      <div className="section-inner">
        <h2 className="section-title">常见问题</h2>
        <p className="section-sub">关于简历优化，你可能想了解这些</p>
        <div className="faq-list">
          {items.map((item, i) => (
            <div key={i} className="faq-item">
              <div
                className={`faq-q ${openIdx === i ? 'open' : ''}`}
                onClick={() => setOpenIdx(openIdx === i ? null : i)}
              >
                {item.q}
                <span className="faq-arrow">▼</span>
              </div>
              {openIdx === i && <div className="faq-a">{item.a}</div>}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}