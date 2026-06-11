import { useState, useEffect } from 'react'

export function useAnimatedValue(target: number, delay = 100, duration = 1200) {
  const [value, setValue] = useState(0)
  useEffect(() => {
    const timer = setTimeout(() => {
      const start = Date.now()
      const tick = () => {
        const elapsed = Date.now() - start
        const progress = Math.min(elapsed / duration, 1)
        const ease = 1 - Math.pow(1 - progress, 4)
        setValue(Math.round(ease * target))
        if (progress < 1) requestAnimationFrame(tick)
      }
      requestAnimationFrame(tick)
    }, delay)
    return () => clearTimeout(timer)
  }, [target, delay, duration])
  return value
}
