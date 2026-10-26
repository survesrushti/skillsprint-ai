import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/react'
import './index.css'
import App from './App.tsx'
import { ClerkAuthSync } from './components/auth/ClerkAuthSync'

const rootElement = document.getElementById('root')
if (rootElement) {
  const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

  createRoot(rootElement).render(
    <StrictMode>
      {publishableKey ? (
        <ClerkProvider publishableKey={publishableKey}>
          <ClerkAuthSync />
          <App />
        </ClerkProvider>
      ) : (
        <App />
      )}
    </StrictMode>,
  )
}
