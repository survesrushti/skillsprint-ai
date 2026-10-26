import { AuthenticateWithRedirectCallback } from '@clerk/react'
import { Navigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'

const HAS_CLERK_KEY = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY)

export default function SSOCallbackPage() {
  if (!HAS_CLERK_KEY) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="w-8 h-8 text-accent-violet animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Completing sign in...</p>
      </div>
      <AuthenticateWithRedirectCallback
        signInFallbackRedirectUrl="/dashboard"
        signUpFallbackRedirectUrl="/dashboard"
      />
    </div>
  )
}
