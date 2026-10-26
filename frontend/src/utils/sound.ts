// Web Audio API Synthesizer (Zero External Audio Dependencies)
// Generates gentle acoustic feedback for user interactions

const SOUND_ENABLED_KEY = 'skillsprint_audio_enabled'

let audioCtx: AudioContext | null = null

function getAudioCtx(): AudioContext | null {
  if (typeof window === 'undefined') return null
  if (!audioCtx) {
    const AudioCtxClass =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext
    if (AudioCtxClass) {
      audioCtx = new AudioCtxClass()
    }
  }
  return audioCtx
}

export function isAudioEnabled(): boolean {
  if (typeof window === 'undefined') return true
  const stored = localStorage.getItem(SOUND_ENABLED_KEY)
  return stored !== 'false'
}

export function setAudioEnabled(enabled: boolean): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(SOUND_ENABLED_KEY, enabled ? 'true' : 'false')
  window.dispatchEvent(
    new CustomEvent('skillsprint_audio_toggled', { detail: { enabled } })
  )
}

export function playTone(
  freq: number,
  type: OscillatorType = 'sine',
  duration = 0.12,
  gainVal = 0.05
): void {
  if (!isAudioEnabled()) return

  try {
    const ctx = getAudioCtx()
    if (!ctx) return
    if (ctx.state === 'suspended') {
      ctx.resume().catch(() => {})
    }

    const osc = ctx.createOscillator()
    const gain = ctx.createGain()

    osc.type = type
    osc.frequency.setValueAtTime(freq, ctx.currentTime)
    gain.gain.setValueAtTime(gainVal, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration)

    osc.connect(gain)
    gain.connect(ctx.destination)

    osc.start()
    osc.stop(ctx.currentTime + duration)
  } catch (err) {
    // Audio autoplay policy or device restrictions
    console.debug('Audio synthesis notice:', err)
  }
}

export function soundClick(): void {
  playTone(480, 'sine', 0.06, 0.04)
}

export function soundSuccess(): void {
  playTone(523.25, 'triangle', 0.1, 0.06) // C5
  setTimeout(() => playTone(659.25, 'sine', 0.15, 0.06), 90) // E5
  setTimeout(() => playTone(783.99, 'sine', 0.22, 0.06), 180) // G5
}

export function soundAlert(): void {
  playTone(330, 'sawtooth', 0.15, 0.04)
  setTimeout(() => playTone(220, 'sawtooth', 0.25, 0.04), 100)
}

