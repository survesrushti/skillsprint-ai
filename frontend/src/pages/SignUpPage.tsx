import Navbar from '../components/layout/Navbar'
import { AuthCard } from '../components/auth/AuthCard'

export default function SignUpPage() {
  return (
    <>
      <Navbar />
      <main className="relative flex-1 flex items-center justify-center px-4 sm:px-6 py-8 sm:py-14 overflow-hidden">
        {/* Soft background ambient glow matching the reference image */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[720px] h-[620px] bg-gradient-to-tr from-[#CBB6E5]/40 via-[#F3B0C7]/30 to-[#B8D7EB]/35 dark:from-indigo-600/15 dark:via-purple-600/10 dark:to-cyan-600/15 rounded-full blur-[140px] pointer-events-none" />

        <div className="relative z-10 w-full max-w-4xl">
          <AuthCard initialMode="sign-up" />
        </div>

        {/* 4-point sparkle accent in bottom-right corner as shown in reference */}
        <div className="fixed bottom-6 right-6 sm:bottom-10 sm:right-10 pointer-events-none z-20 opacity-80 select-none animate-pulse">
          <svg
            className="w-7 h-7 sm:w-9 sm:h-9 text-white/90 drop-shadow-[0_2px_12px_rgba(255,255,255,0.8)]"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M12 0L14.7 9.3L24 12L14.7 14.7L12 24L9.3 14.7L0 12L9.3 9.3L12 0Z" />
          </svg>
        </div>
      </main>
    </>
  )
}

