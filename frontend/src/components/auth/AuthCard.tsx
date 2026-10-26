import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Mail,
  Lock,
  User as UserIcon,
  Eye,
  EyeOff,
  Sparkles,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  KeyRound,
} from 'lucide-react'
import { useSignIn, useSignUp } from '@clerk/react/legacy'
import logoImg from '../../assets/logo.jpg'
import { soundClick, soundSuccess } from '../../utils/sound'

const HAS_CLERK_KEY = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY)

function GoogleIcon() {
  return (
    <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
      />
    </svg>
  )
}

interface AuthCardProps {
  initialMode: 'sign-in' | 'sign-up'
}

export function AuthCard({ initialMode }: AuthCardProps) {
  if (!HAS_CLERK_KEY) {
    return <AuthCardUnconfigured mode={initialMode} />
  }

  return <ClerkAuthCard mode={initialMode} />
}

/**
 * Live Clerk-Integrated Form Component
 */
function ClerkAuthCard({ mode }: { mode: 'sign-in' | 'sign-up' }) {
  const navigate = useNavigate()
  const currentMode = mode

  // Sign In hooks
  const { isLoaded: isSignInLoaded, signIn, setActive: setSignInActive } = useSignIn()
  // Sign Up hooks
  const { isLoaded: isSignUpLoaded, signUp, setActive: setSignUpActive } = useSignUp()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [rememberMe, setRememberMe] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [infoMessage, setInfoMessage] = useState<string | null>(null)

  // Sign-up email verification state
  const [verifyingEmail, setVerifyingEmail] = useState(false)
  const [verificationCode, setVerificationCode] = useState('')

  // Password reset state
  const [resettingPassword, setResettingPassword] = useState(false)
  const [resetCode, setResetCode] = useState('')
  const [newPassword, setNewPassword] = useState('')

  async function handleSignInSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isSignInLoaded || !signIn) return
    setError(null)
    setInfoMessage(null)
    setLoading(true)
    soundClick()

    try {
      const result = await signIn.create({
        identifier: email.trim(),
        password,
      })

      if (result.status === 'complete') {
        soundSuccess()
        await setSignInActive({ session: result.createdSessionId })
        navigate('/dashboard')
      } else {
        setError(`Additional step required (${result.status}).`)
      }
    } catch (err: unknown) {
      const clerkErr = err as { errors?: Array<{ message?: string; longMessage?: string }> }
      const msg =
        clerkErr.errors?.[0]?.longMessage ||
        clerkErr.errors?.[0]?.message ||
        'Failed to sign in. Please check your email and password.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  async function handleSignUpSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isSignUpLoaded || !signUp) return
    setError(null)
    setInfoMessage(null)
    setLoading(true)
    soundClick()

    try {
      const [first, ...rest] = name.trim().split(' ')
      const last = rest.join(' ')

      await signUp.create({
        emailAddress: email.trim(),
        password,
        firstName: first || undefined,
        lastName: last || undefined,
      })

      // Send verification email
      await signUp.prepareEmailAddressVerification({ strategy: 'email_code' })
      setVerifyingEmail(true)
      setInfoMessage(`Verification code sent to ${email.trim()}.`)
    } catch (err: unknown) {
      const clerkErr = err as { errors?: Array<{ message?: string; longMessage?: string }> }
      const msg =
        clerkErr.errors?.[0]?.longMessage ||
        clerkErr.errors?.[0]?.message ||
        'Failed to create account. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  async function handleVerifyEmailSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isSignUpLoaded || !signUp) return
    setError(null)
    setLoading(true)
    soundClick()

    try {
      const completeSignUp = await signUp.attemptEmailAddressVerification({
        code: verificationCode.trim(),
      })

      if (completeSignUp.status === 'complete') {
        soundSuccess()
        await setSignUpActive({ session: completeSignUp.createdSessionId })
        navigate('/onboarding')
      } else {
        setError(`Verification status: ${completeSignUp.status}`)
      }
    } catch (err: unknown) {
      const clerkErr = err as { errors?: Array<{ message?: string }> }
      setError(clerkErr.errors?.[0]?.message || 'Invalid or expired code.')
    } finally {
      setLoading(false)
    }
  }

  async function handleForgotPassword() {
    if (!email.trim()) {
      setError('Please enter your email above, then click Forgot Password.')
      return
    }
    if (!isSignInLoaded || !signIn) return
    setError(null)
    setLoading(true)
    soundClick()

    try {
      const signInAttempt = await signIn.create({
        identifier: email.trim(),
      })
      const resetFactor = signInAttempt.supportedFirstFactors?.find(
        (factor) => factor.strategy === 'reset_password_email_code'
      ) as { emailAddressId?: string } | undefined

      if (resetFactor?.emailAddressId) {
        await signInAttempt.prepareFirstFactor({
          strategy: 'reset_password_email_code',
          emailAddressId: resetFactor.emailAddressId,
        })
      }
      setResettingPassword(true)
      setInfoMessage(`Password reset code sent to ${email.trim()}.`)
    } catch (err: unknown) {
      const clerkErr = err as { errors?: Array<{ message?: string }> }
      setError(clerkErr.errors?.[0]?.message || 'Could not initiate password reset.')
    } finally {
      setLoading(false)
    }
  }

  async function handleResetPasswordSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isSignInLoaded || !signIn) return
    setError(null)
    setLoading(true)
    soundClick()

    try {
      const result = await signIn.attemptFirstFactor({
        strategy: 'reset_password_email_code',
        code: resetCode.trim(),
        password: newPassword,
      })

      if (result.status === 'complete') {
        soundSuccess()
        await setSignInActive({ session: result.createdSessionId })
        navigate('/dashboard')
      } else {
        setError(`Reset status: ${result.status}`)
      }
    } catch (err: unknown) {
      const clerkErr = err as { errors?: Array<{ message?: string }> }
      setError(clerkErr.errors?.[0]?.message || 'Failed to reset password.')
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogleOAuth() {
    setError(null)
    soundClick()
    try {
      if (currentMode === 'sign-in') {
        if (!signIn) return
        await signIn.authenticateWithRedirect({
          strategy: 'oauth_google',
          redirectUrl: '/sso-callback',
          redirectUrlComplete: '/dashboard',
        })
      } else {
        if (!signUp) return
        await signUp.authenticateWithRedirect({
          strategy: 'oauth_google',
          redirectUrl: '/sso-callback',
          redirectUrlComplete: '/onboarding',
        })
      }
    } catch (err: unknown) {
      const clerkErr = err as { errors?: Array<{ message?: string }> }
      setError(clerkErr.errors?.[0]?.message || 'Google authentication failed.')
    }
  }

  return (
    <AuthLayout leftTitle="SkillSprint AI">
      {/* Top Branding Badge */}
      <div className="w-12 h-12 rounded-2xl bg-slate-100/90 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 shadow-sm flex items-center justify-center mb-6">
        <Sparkles className="w-5 h-5 text-pink-500" />
      </div>

      {/* Heading & Subtitle */}
      <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
        {currentMode === 'sign-in' ? 'Welcome Back' : 'Create an Account'}
      </h2>
      <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1.5 mb-7">
        {currentMode === 'sign-in'
          ? 'Sign in to access your unified learning roadmap'
          : 'Sign up to begin your personalized computational sprint'}
      </p>

      {/* Alert Notices */}
      {error && (
        <div className="mb-5 p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 flex items-start gap-2.5 text-xs text-rose-700 dark:text-rose-300">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {infoMessage && (
        <div className="mb-5 p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 flex items-start gap-2.5 text-xs text-emerald-700 dark:text-emerald-300">
          <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-600" />
          <span>{infoMessage}</span>
        </div>
      )}

      {/* Flow 1: Email Code Verification (Sign Up) */}
      {verifyingEmail ? (
        <form onSubmit={handleVerifyEmailSubmit} className="space-y-4">
          <div>
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5 block">
              6-Digit Verification Code
            </label>
            <div className="relative flex items-center rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 px-3.5 py-3 shadow-[0_2px_4px_rgba(0,0,0,0.02)] focus-within:border-pink-500 focus-within:ring-2 focus-within:ring-pink-500/20 transition">
              <KeyRound className="w-4 h-4 text-slate-400 shrink-0" />
              <input
                type="text"
                required
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="123456"
                className="w-full pl-2.5 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !verificationCode}
            className="w-full py-3.5 px-6 rounded-2xl font-semibold text-sm text-white transition-all transform active:scale-[0.98] flex items-center justify-center gap-2 bg-gradient-to-r from-[#DF288F] via-[#EB3499] to-[#E32B91] hover:brightness-105 shadow-[0_10px_25px_-5px_rgba(223,40,143,0.42)] disabled:opacity-60"
          >
            {loading ? 'Verifying...' : 'Complete Sign Up'}
          </button>
        </form>
      ) : resettingPassword ? (
        /* Flow 2: Password Reset */
        <form onSubmit={handleResetPasswordSubmit} className="space-y-4">
          <div>
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5 block">
              Reset Code
            </label>
            <div className="relative flex items-center rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 px-3.5 py-3 shadow-[0_2px_4px_rgba(0,0,0,0.02)] focus-within:border-pink-500 focus-within:ring-2 focus-within:ring-pink-500/20 transition">
              <KeyRound className="w-4 h-4 text-slate-400 shrink-0" />
              <input
                type="text"
                required
                value={resetCode}
                onChange={(e) => setResetCode(e.target.value)}
                placeholder="Enter reset code"
                className="w-full pl-2.5 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5 block">
              New Password
            </label>
            <div className="relative flex items-center rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 px-3.5 py-3 shadow-[0_2px_4px_rgba(0,0,0,0.02)] focus-within:border-pink-500 focus-within:ring-2 focus-within:ring-pink-500/20 transition">
              <Lock className="w-4 h-4 text-slate-400 shrink-0" />
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="New password"
                className="w-full pl-2.5 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !resetCode || !newPassword}
            className="w-full py-3.5 px-6 rounded-2xl font-semibold text-sm text-white transition-all transform active:scale-[0.98] flex items-center justify-center gap-2 bg-gradient-to-r from-[#DF288F] via-[#EB3499] to-[#E32B91] hover:brightness-105 shadow-[0_10px_25px_-5px_rgba(223,40,143,0.42)] disabled:opacity-60"
          >
            {loading ? 'Resetting...' : 'Set New Password'}
          </button>
        </form>
      ) : (
        /* Flow 3: Standard Sign In / Sign Up Form */
        <form
          onSubmit={currentMode === 'sign-in' ? handleSignInSubmit : handleSignUpSubmit}
          className="space-y-4"
        >
          {currentMode === 'sign-up' && (
            <div>
              <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5 block">
                Full Name
              </label>
              <div className="relative flex items-center rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 px-3.5 py-3 shadow-[0_2px_4px_rgba(0,0,0,0.02)] focus-within:border-pink-500 focus-within:ring-2 focus-within:ring-pink-500/20 transition">
                <UserIcon className="w-4 h-4 text-slate-400 shrink-0" />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Alex Rivera"
                  className="w-full pl-2.5 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none"
                />
              </div>
            </div>
          )}

          <div>
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5 block">
              Email
            </label>
            <div className="relative flex items-center rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 px-3.5 py-3 shadow-[0_2px_4px_rgba(0,0,0,0.02)] focus-within:border-pink-500 focus-within:ring-2 focus-within:ring-pink-500/20 transition">
              <Mail className="w-4 h-4 text-slate-400 shrink-0" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-2.5 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5 block">
              Password
            </label>
            <div className="relative flex items-center rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 px-3.5 py-3 shadow-[0_2px_4px_rgba(0,0,0,0.02)] focus-within:border-pink-500 focus-within:ring-2 focus-within:ring-pink-500/20 transition">
              <Lock className="w-4 h-4 text-slate-400 shrink-0" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-2.5 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 ml-2"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {currentMode === 'sign-in' && (
            <div className="flex items-center justify-between text-xs pt-1 pb-1">
              <label className="flex items-center gap-2 cursor-pointer text-slate-600 dark:text-slate-400 select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300 text-pink-600 focus:ring-pink-500"
                />
                <span>Remember me</span>
              </label>

              <button
                type="button"
                onClick={handleForgotPassword}
                className="text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 font-medium transition"
              >
                Forgot Password?
              </button>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !email || !password}
            className="w-full py-3.5 px-6 rounded-2xl font-semibold text-sm text-white transition-all transform active:scale-[0.98] flex items-center justify-center gap-2 bg-gradient-to-r from-[#DF288F] via-[#EB3499] to-[#E32B91] hover:brightness-105 shadow-[0_10px_25px_-5px_rgba(223,40,143,0.42)] disabled:opacity-60 cursor-pointer"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <span>{currentMode === 'sign-in' ? 'Sign In' : 'Sign Up'}</span>
            )}
          </button>

          {/* Divider */}
          <div className="relative my-6 text-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200/90 dark:border-slate-800" />
            </div>
            <span className="relative px-3 bg-[#FCFAFD] dark:bg-slate-900 text-xs font-medium text-slate-400">
              Or Continue With
            </span>
          </div>

          {/* Social Sign-in */}
          <button
            type="button"
            onClick={handleGoogleOAuth}
            className="w-full py-3 px-4 rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 text-xs sm:text-sm font-semibold flex items-center justify-center gap-2.5 shadow-sm hover:shadow transition cursor-pointer"
          >
            <GoogleIcon />
            <span>Google</span>
          </button>
        </form>
      )}

      {/* Switch Link */}
      <div className="text-center text-xs text-slate-500 dark:text-slate-400 mt-6">
        {currentMode === 'sign-in' ? (
          <>
            Don't have an account?{' '}
            <Link
              to="/sign-up"
              onClick={() => soundClick()}
              className="font-bold text-slate-900 dark:text-white hover:text-pink-600 dark:hover:text-pink-400 transition"
            >
              Sign up
            </Link>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <Link
              to="/sign-in"
              onClick={() => soundClick()}
              className="font-bold text-slate-900 dark:text-white hover:text-pink-600 dark:hover:text-pink-400 transition"
            >
              Sign in
            </Link>
          </>
        )}
      </div>
    </AuthLayout>
  )
}

/**
 * Preview / Unconfigured Clerk Fallback (Matches design 100% without throwing missing provider errors)
 */
function AuthCardUnconfigured({ mode }: { mode: 'sign-in' | 'sign-up' }) {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [rememberMe, setRememberMe] = useState(true)
  const [showPassword, setShowPassword] = useState(false)

  function handleDemoSubmit(e: React.FormEvent) {
    e.preventDefault()
    soundSuccess()
    navigate(mode === 'sign-in' ? '/dashboard' : '/onboarding')
  }

  return (
    <AuthLayout leftTitle="SkillSprint AI">
      {/* Top Branding Badge */}
      <div className="w-12 h-12 rounded-2xl bg-slate-100/90 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 shadow-sm flex items-center justify-center mb-6">
        <Sparkles className="w-5 h-5 text-pink-500" />
      </div>

      <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
        {mode === 'sign-in' ? 'Welcome Back' : 'Create an Account'}
      </h2>
      <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1.5 mb-5">
        {mode === 'sign-in'
          ? 'Sign in to access your unified learning roadmap'
          : 'Sign up to begin your personalized computational sprint'}
      </p>

      {/* Helpful Configuration Notice */}
      <div className="mb-5 p-3.5 rounded-2xl bg-amber-50/90 dark:bg-amber-950/40 border border-amber-200/80 dark:border-amber-800/50 text-[11px] text-amber-800 dark:text-amber-200 leading-relaxed">
        <div className="flex items-center gap-1.5 font-bold mb-0.5 text-amber-900 dark:text-amber-100">
          <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
          <span>Clerk Configuration Notice</span>
        </div>
        Add <code className="font-mono px-1 py-0.5 bg-amber-100/80 dark:bg-amber-900/40 rounded">VITE_CLERK_PUBLISHABLE_KEY</code> to your <code className="font-mono px-1 py-0.5 bg-amber-100/80 dark:bg-amber-900/40 rounded">frontend/.env</code> file for live authentication. You can explore in preview mode below.
      </div>

      <form onSubmit={handleDemoSubmit} className="space-y-4">
        {mode === 'sign-up' && (
          <div>
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5 block">
              Full Name
            </label>
            <div className="relative flex items-center rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 px-3.5 py-3 shadow-[0_2px_4px_rgba(0,0,0,0.02)] focus-within:border-pink-500 transition">
              <UserIcon className="w-4 h-4 text-slate-400 shrink-0" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alex Rivera"
                className="w-full pl-2.5 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none"
              />
            </div>
          </div>
        )}

        <div>
          <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5 block">
            Email
          </label>
          <div className="relative flex items-center rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 px-3.5 py-3 shadow-[0_2px_4px_rgba(0,0,0,0.02)] focus-within:border-pink-500 transition">
            <Mail className="w-4 h-4 text-slate-400 shrink-0" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full pl-2.5 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none"
            />
          </div>
        </div>

        <div>
          <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5 block">
            Password
          </label>
          <div className="relative flex items-center rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 px-3.5 py-3 shadow-[0_2px_4px_rgba(0,0,0,0.02)] focus-within:border-pink-500 transition">
            <Lock className="w-4 h-4 text-slate-400 shrink-0" />
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full pl-2.5 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 ml-2"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {mode === 'sign-in' && (
          <div className="flex items-center justify-between text-xs pt-1 pb-1">
            <label className="flex items-center gap-2 cursor-pointer text-slate-600 dark:text-slate-400 select-none">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-pink-600 focus:ring-pink-500"
              />
              <span>Remember me</span>
            </label>
            <span className="text-slate-400 text-xs">Forgot Password?</span>
          </div>
        )}

        <button
          type="submit"
          className="w-full py-3.5 px-6 rounded-2xl font-semibold text-sm text-white transition-all transform active:scale-[0.98] flex items-center justify-center gap-2 bg-gradient-to-r from-[#DF288F] via-[#EB3499] to-[#E32B91] hover:brightness-105 shadow-[0_10px_25px_-5px_rgba(223,40,143,0.42)] cursor-pointer"
        >
          <span>{mode === 'sign-in' ? 'Sign In (Explore Demo)' : 'Sign Up (Explore Demo)'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>

        <div className="relative my-6 text-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-200/90 dark:border-slate-800" />
          </div>
          <span className="relative px-3 bg-[#FCFAFD] dark:bg-slate-900 text-xs font-medium text-slate-400">
            Or Continue With
          </span>
        </div>

        <button
          type="button"
          onClick={() => navigate('/dashboard')}
          className="w-full py-3 px-4 rounded-2xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 text-xs sm:text-sm font-semibold flex items-center justify-center gap-2.5 shadow-sm hover:shadow transition cursor-pointer"
        >
          <GoogleIcon />
          <span>Google (Demo)</span>
        </button>
      </form>

      <div className="text-center text-xs text-slate-500 dark:text-slate-400 mt-6">
        {mode === 'sign-in' ? (
          <>
            Don't have an account?{' '}
            <Link
              to="/sign-up"
              onClick={() => soundClick()}
              className="font-bold text-slate-900 dark:text-white hover:text-pink-600 dark:hover:text-pink-400 transition"
            >
              Sign up
            </Link>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <Link
              to="/sign-in"
              onClick={() => soundClick()}
              className="font-bold text-slate-900 dark:text-white hover:text-pink-600 dark:hover:text-pink-400 transition"
            >
              Sign in
            </Link>
          </>
        )}
      </div>
    </AuthLayout>
  )
}

/**
 * 2-Column Responsive Card Layout Matching Dribbble Reference
 */
function AuthLayout({
  leftTitle,
  children,
}: {
  leftTitle: string
  children: React.ReactNode
}) {
  return (
    <div className="relative w-full max-w-4xl mx-auto rounded-[32px] overflow-hidden shadow-[0_25px_70px_-15px_rgba(79,70,229,0.12),0_10px_30px_-10px_rgba(244,114,182,0.15)] border border-white/90 dark:border-slate-800/90 backdrop-blur-2xl grid grid-cols-1 md:grid-cols-2">
      {/* Left Branding Panel */}
      <div className="relative min-h-[320px] md:min-h-[580px] p-8 sm:p-12 flex flex-col items-center justify-center text-center overflow-hidden bg-gradient-to-br from-[#E8DCF5]/85 via-[#F7B7D2]/45 to-[#E1DAF0]/85 dark:from-indigo-950/70 dark:via-purple-950/50 dark:to-slate-900/90">
        {/* Soft Ambient Radial Accents */}
        <div className="absolute top-1/4 left-1/4 w-56 h-56 bg-pink-400/25 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-56 h-56 bg-cyan-400/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col items-center">
          {/* SkillSprint AI Heading */}
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-[#161938] dark:text-white mb-8 sm:mb-12">
            {leftTitle}
          </h1>

          {/* 3D Staircase Artwork Badge */}
          <div className="relative w-44 h-44 sm:w-56 sm:h-56 flex items-center justify-center p-3 rounded-3xl transition-transform duration-500 hover:scale-105">
            <img
              src={logoImg}
              alt="SkillSprint AI Staircase"
              className="w-full h-full object-contain rounded-2xl drop-shadow-[0_15px_30px_rgba(30,27,75,0.22)]"
            />
          </div>
        </div>
      </div>

      {/* Right Form Panel */}
      <div className="p-8 sm:p-12 flex flex-col justify-center bg-[#FCFAFD] dark:bg-slate-900">
        {children}
      </div>
    </div>
  )
}
