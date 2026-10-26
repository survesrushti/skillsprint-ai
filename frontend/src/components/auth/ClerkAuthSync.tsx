import { useEffect } from 'react'
import { useAuth } from '@clerk/react'
import { setAuthTokenGetter } from '../../api/client'

export function ClerkAuthSync() {
  const { getToken, isSignedIn } = useAuth()

  useEffect(() => {
    if (isSignedIn) {
      setAuthTokenGetter(async () => {
        try {
          return await getToken()
        } catch {
          return null
        }
      })
    } else {
      setAuthTokenGetter(() => Promise.resolve(null))
    }
  }, [getToken, isSignedIn])

  return null
}

