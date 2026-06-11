
interface NavbarProps {
  onLaunch: () => void
}

export default function Navbar({ onLaunch }: NavbarProps) {
  return (
    <div className="fixed top-0 left-0 right-0 z-50 pt-6 px-6 md:px-12 lg:px-16">
      <nav className="liquid-glass rounded-xl px-4 py-2 flex items-center justify-between">
        <span className="text-2xl font-semibold tracking-tight text-white">NexusAI</span>
        <div className="hidden md:flex items-center gap-8">
          {['Overview','Pipeline','Risk Engine','Audit Trail'].map(item => (
            <button key={item} className="text-sm text-gray-300 hover:text-white transition-colors">{item}</button>
          ))}
        </div>
        <button
          onClick={onLaunch}
          className="btn-white text-sm px-6 py-2"
        >
          Launch Analysis
        </button>
      </nav>
    </div>
  )
}
