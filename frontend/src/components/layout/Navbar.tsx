import { useState, useEffect } from 'react'
import {
  LayoutGrid,
  Map,
  BookOpen,
  Volume2,
  VolumeX,
  Sparkles,
  Timer,
  Zap,
  Sun,
  Moon,
} from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { UserButton, useAuth } from '@clerk/react'
import logoImg from '../../assets/logo.jpg'
import { isAudioEnabled, setAudioEnabled, soundClick, soundSuccess } from '../../utils/sound'
import { getTheme, toggleTheme, THEME_TOGGLE_EVENT, type ThemeMode } from '../../utils/theme'

const HAS_CLERK_KEY = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY)

function ClerkNavAuth() {
  const { isLoaded, isSignedIn } = useAuth()

  if (!isLoaded) {
    return <div className="h-8 w-20 animate-pulse rounded-lg bg-slate-800" />
  }

  if (isSignedIn) {
    return (
      <div className="flex items-center gap-3">
        <UserButton />
      </div>
    )
  }

  return (
    <Link
      to="/sign-in"
      onClick={() => soundClick()}
      className="rounded-xl bg-gradient-to-r from-accent-violet to-indigo-600 hover:from-accent-violet/90 hover:to-indigo-500 text-white px-3.5 py-1.5 text-xs font-semibold shadow-glow-violet transition inline-flex items-center"
    >
      Sign In
    </Link>
  )
}

function Navbar() {
  const location = useLocation()
  const currentPath = location.pathname
  const [audioActive, setAudioActive] = useState<boolean>(isAudioEnabled())
  const [theme, setThemeState] = useState<ThemeMode>(getTheme)

  useEffect(() => {
    function handleAudioChange(e: Event) {
      const customEvent = e as CustomEvent<{ enabled: boolean }>
      setAudioActive(customEvent.detail.enabled)
    }

    function handleThemeChange(e: Event) {
      const customEvent = e as CustomEvent<{ theme: ThemeMode }>
      if (customEvent.detail?.theme) {
        setThemeState(customEvent.detail.theme)
      }
    }

    window.addEventListener('skillsprint_audio_toggled', handleAudioChange)
    window.addEventListener(THEME_TOGGLE_EVENT, handleThemeChange)
    return () => {
      window.removeEventListener('skillsprint_audio_toggled', handleAudioChange)
      window.removeEventListener(THEME_TOGGLE_EVENT, handleThemeChange)
    }
  }, [])

  function handleToggleSound() {
    const nextState = !audioActive
    setAudioEnabled(nextState)
    setAudioActive(nextState)
    if (nextState) {
      soundSuccess()
    }
  }

  function handleToggleTheme() {
    soundClick()
    const nextTheme = toggleTheme()
    setThemeState(nextTheme)
  }

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <Link
          to="/"
          onClick={() => soundClick()}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="relative w-9 h-9 rounded-xl bg-gradient-to-tr from-accent-violet via-indigo-500 to-cyan-400 p-[1.5px] shadow-glow-violet transition group-hover:scale-105 shrink-0">
            <div className="w-full h-full bg-white rounded-[10px] overflow-hidden flex items-center justify-center">
              <img
                src={logoImg}
                alt="SkillSprint AI Logo"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                SkillSprint<span className="text-accent-violet">AI</span>
              </span>
              <span className="text-[9px] uppercase font-mono px-1.5 py-0.5 rounded bg-accent-violet/10 text-accent-violet border border-accent-violet/20 font-semibold">
                V1 Beta
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono tracking-tight hidden sm:block">
              Computational Adaptive Coach
            </p>
          </div>
        </Link>

        {/* Central Nav Tabs */}
        <nav className="hidden md:flex items-center gap-1 p-1 bg-obsidian-900/90 border border-slate-800 rounded-xl text-xs font-medium">
          <Link
            to="/tracks"
            onClick={() => soundClick()}
            className={`px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
              currentPath.startsWith('/tracks')
                ? 'bg-accent-violet text-white font-bold shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span>Tracks</span>
          </Link>

          <Link
            to="/dashboard"
            onClick={() => soundClick()}
            className={`px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
              currentPath === '/dashboard'
                ? 'bg-accent-violet text-white font-bold shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5 text-accent-violet" />
            <span>Dashboard</span>
          </Link>

          <Link
            to="/roadmap"
            onClick={() => soundClick()}
            className={`px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
              currentPath === '/roadmap'
                ? 'bg-accent-violet text-white font-bold shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Map className="w-3.5 h-3.5 text-indigo-400" />
            <span>Roadmap</span>
          </Link>

          <Link
            to="/workspace"
            onClick={() => soundClick()}
            className={`px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
              currentPath === '/workspace'
                ? 'bg-accent-violet text-white font-bold shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Timer className="w-3.5 h-3.5 text-emerald-400" />
            <span>Workspace</span>
          </Link>

          <Link
            to="/replanning"
            onClick={() => soundClick()}
            className={`px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
              currentPath === '/replanning'
                ? 'bg-accent-violet text-white font-bold shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Replanning</span>
          </Link>
        </nav>

        {/* Right Header Actions (Sound toggle, Theme toggle, Clerk / CTA) */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Sound FX toggle button */}
          <button
            onClick={handleToggleSound}
            title={audioActive ? 'Mute Sound Effects' : 'Enable Sound Effects'}
            aria-label="Toggle sound effects"
            className="p-2 rounded-xl bg-obsidian-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition"
          >
            {audioActive ? (
              <Volume2 className="w-4 h-4 text-accent-violet" />
            ) : (
              <VolumeX className="w-4 h-4 text-slate-500" />
            )}
          </button>

          {/* Theme Mode Toggle (Light / Dark) */}
          <button
            onClick={handleToggleTheme}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle theme mode"
            className="p-2 rounded-xl bg-obsidian-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition"
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4 text-accent-amber" />
            ) : (
              <Moon className="w-4 h-4 text-accent-violet" />
            )}
          </button>

          {/* User Auth or Get Started */}
          <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
            {HAS_CLERK_KEY ? (
              <ClerkNavAuth />
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/sign-in"
                  onClick={() => soundClick()}
                  className="px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white transition"
                >
                  Sign In
                </Link>
                <Link
                  to="/onboarding"
                  onClick={() => soundClick()}
                  className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-accent-violet to-indigo-600 hover:from-accent-violet/90 hover:to-indigo-500 text-white text-xs font-semibold shadow-glow-violet transition flex items-center gap-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Start Roadmap</span>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Navbar