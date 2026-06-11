import AnimatedHeading from './AnimatedHeading'
import FadeIn from './FadeIn'
import { VIDEO_URL } from '../constants'

interface Props {
  onStart: () => void
}

export default function HeroSection({ onStart }: Props) {
  return (
    <section className="relative w-full h-screen overflow-hidden bg-black">
      {/* Raw undimmed video */}
      <video
        className="absolute inset-0 w-full h-full object-cover"
        src={VIDEO_URL}
        autoPlay
        loop
        muted
        playsInline
      />

      {/* Content — bottom aligned */}
      <div className="relative z-10 h-full flex flex-col justify-end pb-16 px-6 md:px-12 lg:px-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-end">
          {/* Left column */}
          <div className="flex flex-col gap-6">
            <AnimatedHeading
              text="Autonomous Lending Intelligence"
              className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal text-white leading-tight"
            />
            <AnimatedHeading
              text="for the next generation of banking."
              className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal text-white leading-tight"
            />

            <FadeIn delay={800} duration={1000}>
              <p className="text-base md:text-lg text-gray-300 max-w-lg">
                Multi-agent AI underwriting with explainability, fraud detection and human oversight.
              </p>
            </FadeIn>

            <FadeIn delay={1200} duration={800}>
              <div className="flex items-center gap-4 flex-wrap">
                <button
                  onClick={onStart}
                  className="btn-white px-8 py-3 text-base"
                >
                  Start Evaluation
                </button>
                <button className="btn-glass px-8 py-3 text-base liquid-glass">
                  Explore Platform
                </button>
              </div>
            </FadeIn>
          </div>

          {/* Right column */}
          <FadeIn delay={1400} duration={1000} className="flex justify-end">
            <div className="liquid-glass rounded-2xl p-8 max-w-sm w-full">
              <p className="text-lg md:text-xl lg:text-2xl font-light text-white leading-relaxed">
                Underwriting. Fraud Intelligence. Explainability.
              </p>
              <div className="mt-6 flex flex-col gap-2">
                {[
                  ['7 AI Agents', 'Operating in parallel'],
                  ['Real-time', 'Fraud detection'],
                  ['Full audit', 'Cryptographic trail'],
                ].map(([title, sub]) => (
                  <div key={title} className="flex items-center justify-between py-2 border-b border-white/10 last:border-0">
                    <span className="text-sm font-medium text-white">{title}</span>
                    <span className="text-xs text-gray-400">{sub}</span>
                  </div>
                ))}
              </div>
            </div>
          </FadeIn>
        </div>
      </div>
    </section>
  )
}
