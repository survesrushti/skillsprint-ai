import { useState } from 'react'
import { Sparkles, Star, ThumbsUp, X, CheckCircle2 } from 'lucide-react'
import {
  submitWeeklyReflection,
  type WeeklyReflectionData,
} from '../../api/client'
import { soundClick, soundSuccess, soundAlert } from '../../utils/sound'

interface WeeklyReflectionModalProps {
  isOpen: boolean
  goalId: number
  weekNumber: number
  studyDay: number
  onClose: () => void
  onSuccess: (reflection: WeeklyReflectionData) => void
}

const CONFIDENCE_LEVELS = [
  { value: 1, label: 'Struggling', desc: 'Need significantly more practice' },
  { value: 2, label: 'Hesitant', desc: 'Understanding basics, but uncertain' },
  { value: 3, label: 'Developing', desc: 'Steady progress, grasping key concepts' },
  { value: 4, label: 'Confident', desc: 'Comfortable with topics and tasks' },
  { value: 5, label: 'Mastered', desc: 'High proficiency, ready to build' },
]

const DIFFICULTY_RATINGS = [
  { value: 1, label: 'Too Easy', desc: 'Finished with plenty of extra time' },
  { value: 2, label: 'Comfortable', desc: 'Manageable pace, little friction' },
  { value: 3, label: 'Balanced', desc: 'Optimal learning challenge' },
  { value: 4, label: 'Challenging', desc: 'Required intense focus and effort' },
  { value: 5, label: 'Overwhelming', desc: 'Fell behind on study time' },
]

export default function WeeklyReflectionModal({
  isOpen,
  goalId,
  weekNumber,
  studyDay,
  onClose,
  onSuccess,
}: WeeklyReflectionModalProps) {
  const [confidence, setConfidence] = useState<number>(4)
  const [difficulty, setDifficulty] = useState<number>(3)
  const [notes, setNotes] = useState<string>('')
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string>('')
  const [submitted, setSubmitted] = useState<boolean>(false)

  if (!isOpen) return null

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')

    try {
      const res = await submitWeeklyReflection({
        goal_id: goalId,
        week_number: weekNumber,
        study_day: studyDay,
        confidence_level: confidence,
        difficulty_rating: difficulty,
        notes: notes.trim() || undefined,
      })

      soundSuccess()
      setSubmitted(true)
      setTimeout(() => {
        onSuccess(res.reflection)
        onClose()
      }, 1200)
    } catch (err) {
      soundAlert()
      setError(
        err instanceof Error
          ? err.message
          : 'Could not submit your reflection. Please try again.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center bg-obsidian-950/80 px-4 py-6 backdrop-blur-md"
    >
      <div className="relative w-full max-w-2xl rounded-3xl border border-white/10 bg-obsidian-900/90 glass-panel p-6 shadow-2xl sm:p-8 backdrop-blur-xl overflow-hidden">
        {/* Ambient Top Glow */}
        <div className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 w-80 h-32 bg-rose-500/10 dark:bg-violet-600/15 rounded-full blur-3xl" />

        {/* Close Button */}
        <button
          onClick={() => {
            soundClick()
            onClose()
          }}
          className="absolute right-6 top-6 rounded-full p-2 text-slate-400 transition hover:bg-white/10 hover:text-white"
          aria-label="Close reflection modal"
        >
          <X size={20} />
        </button>

        {submitted ? (
          <div className="py-12 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-glow-emerald">
              <CheckCircle2 size={36} />
            </div>
            <h3 className="mt-4 text-2xl font-bold text-white tracking-tight">
              Weekly Reflection Recorded!
            </h3>
            <p className="mt-2 text-sm text-slate-400 max-w-md mx-auto">
              Great dedication! Your subjective insights help optimize your adaptive learning pace.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="relative space-y-6">
            {/* Header */}
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-3.5 py-1 text-xs font-semibold text-violet-300">
                <Sparkles size={13} className="text-violet-400" />
                <span>Weekly Reflection · Week {weekNumber} (Day {studyDay})</span>
              </div>
              <h2 className="mt-3 text-2xl font-bold text-white sm:text-3xl tracking-tight">
                How did this week feel?
              </h2>
              <p className="mt-1 text-sm text-slate-400">
                Reflect on your study habits and subjective confidence. This guides our adaptive recommendations.
              </p>
            </div>

            {error && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
                {error}
              </div>
            )}

            {/* 1. Subjective Confidence Level */}
            <div>
              <label className="block text-sm font-semibold text-slate-200">
                Subjective Confidence Level (1–5)
              </label>
              <p className="mt-0.5 text-xs text-slate-400">
                How confident do you feel with the technical topics studied this week?
              </p>
              <div className="mt-3 grid grid-cols-5 gap-2">
                {CONFIDENCE_LEVELS.map((item) => {
                  const isSelected = confidence === item.value
                  return (
                    <button
                      key={item.value}
                      type="button"
                      onClick={() => {
                        soundClick()
                        setConfidence(item.value)
                      }}
                      className={`flex flex-col items-center rounded-2xl border p-3 text-center transition duration-200 ${
                        isSelected
                          ? 'border-violet-500/80 bg-violet-500/15 text-white ring-1 ring-violet-500/50 shadow-glow-violet'
                          : 'border-white/10 bg-obsidian-950/60 text-slate-400 hover:border-white/20 hover:text-slate-200 hover:bg-obsidian-850'
                      }`}
                    >
                      <Star
                        size={18}
                        className={isSelected ? 'fill-violet-400 text-violet-400' : 'text-slate-500'}
                      />
                      <span className="mt-1 font-mono text-xs font-bold text-slate-200">
                        {item.value}
                      </span>
                      <span className="text-[10px] leading-tight text-slate-400">
                        {item.label}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* 2. Difficulty & Workload Rating */}
            <div>
              <label className="block text-sm font-semibold text-slate-200">
                Difficulty & Pacing Perception (1–5)
              </label>
              <p className="mt-0.5 text-xs text-slate-400">
                How was the workload and study challenge relative to your daily capacity?
              </p>
              <div className="mt-3 grid grid-cols-5 gap-2">
                {DIFFICULTY_RATINGS.map((item) => {
                  const isSelected = difficulty === item.value
                  return (
                    <button
                      key={item.value}
                      type="button"
                      onClick={() => {
                        soundClick()
                        setDifficulty(item.value)
                      }}
                      className={`flex flex-col items-center rounded-2xl border p-3 text-center transition duration-200 ${
                        isSelected
                          ? 'border-emerald-500/80 bg-emerald-500/15 text-white ring-1 ring-emerald-500/50 shadow-glow-emerald'
                          : 'border-white/10 bg-obsidian-950/60 text-slate-400 hover:border-white/20 hover:text-slate-200 hover:bg-obsidian-850'
                      }`}
                    >
                      <ThumbsUp
                        size={18}
                        className={isSelected ? 'text-emerald-400' : 'text-slate-500'}
                      />
                      <span className="mt-1 font-mono text-xs font-bold text-slate-200">
                        {item.value}
                      </span>
                      <span className="text-[10px] leading-tight text-slate-400">
                        {item.label}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* 3. Study Habit Notes */}
            <div>
              <label htmlFor="reflection-notes" className="block text-sm font-semibold text-slate-200">
                Study Habit Notes & Observations (Optional)
              </label>
              <textarea
                id="reflection-notes"
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g., Practiced JavaScript DOM manipulation for 2 hours daily; had some trouble with async/await but reviewed documentation."
                className="mt-2 w-full rounded-2xl border border-white/10 bg-obsidian-950/70 p-4 text-sm text-slate-200 placeholder-slate-500 outline-none transition focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/40"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  soundClick()
                  onClose()
                }}
                className="rounded-xl border border-white/10 bg-obsidian-800/60 px-5 py-2.5 text-sm font-semibold text-slate-300 transition hover:bg-white/5 hover:text-white"
              >
                Remind Me Later
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 px-6 py-2.5 text-sm font-semibold text-white shadow-glow-violet transition duration-200 hover:opacity-95 disabled:opacity-50"
              >
                {isSubmitting ? 'Saving...' : 'Save Weekly Reflection'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

