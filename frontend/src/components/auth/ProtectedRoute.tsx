import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@clerk/react'
import { Loader2 } from 'lucide-react'

const HAS_CLERK_KEY = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY)

interface ProtectedRouteProps {
  children: ReactNode
}

function ClerkRouteGuard({ children }: ProtectedRouteProps) {
  const { isLoaded, isSignedIn } = useAuth()
  const location = useLocation()

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 text-accent-violet animate-spin" />
          <p className="text-sm text-slate-400 font-medium">Checking authentication...</p>
        </div>
      </div>
    )
  }

  if (!isSignedIn) {
    return <Navigate to="/sign-in" state={{ from: location }} replace />
  }

  return <>{children}</>
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  if (!HAS_CLERK_KEY) {
    // In demo / preview mode without Clerk publishable key, allow direct access
    return <>{children}</>
  }

  return <ClerkRouteGuard>{children}</ClerkRouteGuard>
}

export default ProtectedRoute
