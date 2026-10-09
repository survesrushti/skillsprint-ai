import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'

function Navbar() {
  return (
    <header className="border-b border-slate-800 bg-slate-950">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-12">
        <Link
          to="/"
          className="flex items-center gap-3"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400 text-slate-950">
            <BookOpen size={22} />
          </div>

          <div>
            <h1 className="text-lg font-bold text-white">
              SkillSprint AI
            </h1>

            <p className="text-xs text-slate-400">
              Adaptive Learning Coach
            </p>
          </div>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          <a
            href="/#features"
            className="text-sm text-slate-300 transition hover:text-cyan-400"
          >
            Features
          </a>

          <a
            href="/#tracks"
            className="text-sm text-slate-300 transition hover:text-cyan-400"
          >
            Learning Tracks
          </a>

          <a
            href="/#how-it-works"
            className="text-sm text-slate-300 transition hover:text-cyan-400"
          >
            How It Works
          </a>

          <Link
            to="/tracks"
            className="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
          >
            Get Started
          </Link>
        </div>
      </nav>
    </header>
  )
}

export default Navbar