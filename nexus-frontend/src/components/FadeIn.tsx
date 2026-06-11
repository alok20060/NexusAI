import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'

interface Props {
  children: ReactNode
  delay?: number
  duration?: number
  className?: string
}

export default function FadeIn({ children, delay = 0, duration = 800, className = '' }: Props) {
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), delay)
    return () => clearTimeout(t)
  }, [delay])
  return (
    <div
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(12px)',
        transition: `opacity ${duration}ms ease, transform ${duration}ms ease`,
      }}
    >
      {children}
    </div>
  )
}
