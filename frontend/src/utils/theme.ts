export type ThemeMode = 'light' | 'dark'

export const THEME_STORAGE_KEY = 'skillsprint_theme'
export const THEME_TOGGLE_EVENT = 'skillsprint_theme_changed'

/**
 * Reads initial theme from DOM or localStorage.
 * Defaults to device preference if dark, otherwise 'light'.
 */
export function getTheme(): ThemeMode {
  if (typeof document === 'undefined') return 'light'
  if (document.documentElement.classList.contains('dark')) {
    return 'dark'
  }
  return 'light'
}

/**
 * Applies the given theme to document.documentElement,
 * updates localStorage, and notifies listeners.
 */
export function setTheme(theme: ThemeMode): void {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  if (theme === 'dark') {
    root.classList.add('dark')
    root.classList.remove('light')
  } else {
    root.classList.remove('dark')
    root.classList.add('light')
  }

  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  } catch {
    // LocalStorage might be disabled or unavailable
  }

  window.dispatchEvent(
    new CustomEvent(THEME_TOGGLE_EVENT, { detail: { theme } })
  )
}

/**
 * Toggles between light and dark modes and returns the new theme.
 */
export function toggleTheme(): ThemeMode {
  const current = getTheme()
  const next: ThemeMode = current === 'dark' ? 'light' : 'dark'
  setTheme(next)
  return next
}

