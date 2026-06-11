import { useEffect, useState } from 'react'

interface Props {
  text: string
  className?: string
}

export default function AnimatedHeading({ text, className = '' }: Props) {
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 200)
    return () => clearTimeout(t)
  }, [])

  return (
    <h1 className={className}>
      {text.split('').map((char, i) => (
        <span
          key={i}
          className="inline-block transition-all duration-500"
          style={{
            opacity: visible ? 1 : 0,
            transform: visible ? 'translateX(0)' : 'translateX(-18px)',
            transitionDelay: visible ? `${200 + i * 30}ms` : '0ms',
          }}
        >
          {char === ' ' ? '\u00A0' : char}
        </span>
      ))}
    </h1>
  )
}
