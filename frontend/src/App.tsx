import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import TracksPage from './pages/TracksPage'
import TrackDetailPage from './pages/TrackDetailPage'
import OnboardingPage from './pages/OnboardingPage'
import RoadmapPage from './pages/RoadmapPage'
import DashboardPage from './pages/DashboardPage'
import WorkspacePage from './pages/WorkspacePage'
import ReplanningPage from './pages/ReplanningPage'
import SignInPage from './pages/SignInPage'
import SignUpPage from './pages/SignUpPage'
import SSOCallbackPage from './pages/SSOCallbackPage'
import ProtectedRoute from './components/auth/ProtectedRoute'
import DemoToolbar from './components/dev/DemoToolbar'

function App() {
  return (
    <BrowserRouter>
      {/* Ambient Radial Backlights (Spatial Tablo Pastel Mesh in Light Mode, Preserved Ambient Backlights in Dark Mode) */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        {/* Top-Right: Warm Pastel Yellow */}
        <div className="absolute -top-24 -right-20 w-[580px] h-[480px] bg-[#F2C560]/28 dark:bg-indigo-600/10 rounded-full blur-[140px] animate-subtle-pulse" />
        {/* Lower-Left: Cotton-Candy Pink */}
        <div className="absolute top-1/2 -left-28 w-[560px] h-[520px] bg-[#EE9DCC]/35 dark:bg-purple-600/10 rounded-full blur-[140px]" />
        {/* Center: Soft Peach Transition */}
        <div className="absolute top-1/4 left-1/3 w-[460px] h-[420px] bg-[#F2B392]/20 dark:hidden rounded-full blur-[130px]" />
        {/* Lower-Right: Subtle Pale Mint / Cyan Tint */}
        <div className="absolute -bottom-24 -right-24 w-[480px] h-[480px] bg-[#D9EDE8]/35 dark:bg-cyan-600/10 rounded-full blur-[130px]" />
      </div>

      <div className="relative z-10 flex min-h-screen flex-col bg-transparent">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/tracks" element={<TracksPage />} />
          <Route path="/tracks/:slug" element={<TrackDetailPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />

          {/* Authentication Routes */}
          <Route path="/sign-in" element={<SignInPage />} />
          <Route path="/sign-up" element={<SignUpPage />} />
          <Route path="/login" element={<SignInPage />} />
          <Route path="/register" element={<SignUpPage />} />
          <Route path="/sso-callback" element={<SSOCallbackPage />} />

          {/* Protected Application Routes */}
          <Route
            path="/roadmap"
            element={
              <ProtectedRoute>
                <RoadmapPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/workspace"
            element={
              <ProtectedRoute>
                <WorkspacePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/replanning"
            element={
              <ProtectedRoute>
                <ReplanningPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
      <DemoToolbar />
    </BrowserRouter>
  )
}

export default App
