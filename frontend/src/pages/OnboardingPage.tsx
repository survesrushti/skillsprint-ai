import { useState } from 'react'
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import {
  Code2,
  BarChart3,
  Palette,
  Sparkles,
  Calendar,
  Clock,
  AlertCircle,
  Lightbulb,
} from 'lucide-react'
import { createGoal } from '../api/client'
import { soundClick, soundSuccess, soundAlert } from '../utils/sound'

const TRACK_CONFIG: Record<
  string,
  { id: number; name: string; subtitle: string; icon: typeof Code2; color: string; suggestions: string[] }
> = {
  'full-stack': {
    id: 1,
    name: 'Full Stack Development',
    subtitle: 'React, Flask, SQL, API architectures',
    icon: Code2,
    color: 'accent-violet',
    suggestions: ['HTML', 'CSS', 'JavaScript', 'React', 'Git', 'SQL'],
  },
  'data-analytics': {
    id: 2,
    name: 'Data Analytics & Engineering',
    subtitle: 'Python, Pandas, SQL joins, Tableau / BI',
    icon: BarChart3,
    color: 'accent-cyan',
    suggestions: ['Python', 'SQL', 'Excel', 'Statistics', 'Pandas'],
  },
  'ui-ux': {
    id: 3,
    name: 'UI/UX Product Design',
    subtitle: 'Figma, Design Systems, UX research & wireframing',
    icon: Palette,
    color: 'accent-rose',
    suggestions: ['Figma', 'Wireframing', 'User Research', 'Design Systems'],
  },
}

function normalizeTrackSlug(raw: string | null): string {
  if (!raw) return 'full-stack'
  if (raw === 'full-stack-development') return 'full-stack'
  if (raw === 'ui-ux-design') return 'ui-ux'
  if (TRACK_CONFIG[raw]) return raw
  return 'full-stack'
}

function OnboardingPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()

  const initialTrack = normalizeTrackSlug(
    searchParams.get('track') || location.state?.track || 'full-stack'
  )

  const [selectedTrack, setSelectedTrack] = useState<string>(initialTrack)
  const [level, setLevel] = useState<'Beginner' | 'Intermediate' | 'Advanced'>('Beginner')
  const [studyHours, setStudyHours] = useState<string>('2.0')
  const [targetDate, setTargetDate] = useState<string>('')
  const [reminderTime, setReminderTime] = useState<string>(
    typeof window !== 'undefined'
      ? localStorage.getItem('skillsprint_reminder_time') || '19:30'
      : '19:30'
  )
  const [knownTopics, setKnownTopics] = useState<string>('')
  const [commitment, setCommitment] = useState<boolean>(true)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  const activeTrackMeta = TRACK_CONFIG[selectedTrack] || TRACK_CONFIG['full-stack']

  function addSuggestedTopic(topic: string) {
    soundClick()
    const current = knownTopics
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)
    if (!current.includes(topic)) {
      current.push(topic)
      setKnownTopics(current.join(', '))
    }
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!targetDate) {
      soundAlert()
      setError('Please choose a valid target completion date.')
      return
    }

    if (!commitment) {
      soundAlert()
      setError('Please agree to the Goal Commitment pledge to proceed.')
      return
    }

    setIsSubmitting(true)
    setError('')
    soundClick()

    const [year, month, day] = targetDate.split('-')
    const formattedTargetDate = `${day}/${month}/${year}`

    const knownTopicsList = knownTopics
      .split(',')
      .map((topic) => topic.trim())
      .filter((topic) => topic.length > 0)

    try {
      const response = await createGoal({
        track_id: activeTrackMeta.id,
        skill_level: level,
        study_hours_per_day: parseFloat(studyHours),
        target_date: formattedTargetDate,
        known_topics: knownTopicsList,
        commitment,
      })

      const createdGoal = response.goal
      localStorage.setItem('skillsprint_active_goal_id', String(createdGoal.id))
      localStorage.setItem('skillsprint_reminder_time', reminderTime)

      soundSuccess()

      navigate(`/roadmap?goal_id=${createdGoal.id}`, {
        state: {
          track: selectedTrack,
          track_id: activeTrackMeta.id,
          level,
          studyHours: parseFloat(studyHours),
          targetDate: formattedTargetDate,
          knownTopics: knownTopicsList,
          commitment,
          goalId: createdGoal.id,
        },
      })
    } catch (submitError) {
      soundAlert()
      console.error('Goal creation error:', submitError)
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Could not connect to the backend to generate your roadmap.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <Navbar />

      <main className="min-h-screen text-slate-100 px-4 sm:px-6 lg:px-8 py-10 max-w-4xl mx-auto w-full">
        <div className="glass-panel rounded-3xl p-6 sm:p-10 border border-slate-800 gradient-border shadow-2xl space-y-8">
          {/* Header */}
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-violet/10 text-accent-violet text-xs font-mono mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Step 1 of 1: Goal Commitment Formulation</span>
            </div>

            <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              Configure Your Adaptive Roadmap
            </h1>

            <p className="text-sm text-slate-400 mt-2 leading-relaxed">
              SkillSprint AI will synthesize your inputs through our heuristic search engine to construct an
              optimized, re-schedulable study path.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* 1. Track Selector */}
            <div className="space-y-3">
              <label className="text-xs font-bold uppercase font-mono tracking-wider text-slate-300">
                1. Select Curated Learning Track
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {Object.entries(TRACK_CONFIG).map(([slug, meta]) => {
                  const isSelected = selectedTrack === slug
                  const IconComponent = meta.icon

                  return (
                    <button
                      key={slug}
                      type="button"
                      onClick={() => {
                        soundClick()
                        setSelectedTrack(slug)
                      }}
                      className={`text-left p-4 rounded-xl border transition flex flex-col justify-between ${
                        isSelected
                          ? 'border-accent-violet bg-accent-violet/10 shadow-glow-violet'
                          : 'border-slate-800 bg-obsidian-900/60 hover:border-slate-700'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <IconComponent
                            className={`w-5 h-5 ${
                              isSelected ? 'text-accent-violet' : 'text-slate-400'
                            }`}
                          />
                          <span
                            className={`w-2.5 h-2.5 rounded-full transition ${
                              isSelected ? 'bg-accent-violet shadow-sm' : 'bg-slate-700'
                            }`}
                          />
                        </div>
                        <p className="font-bold text-sm text-white">{meta.name}</p>
                        <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                          {meta.subtitle}
                        </p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* 2. Prior Knowledge Level */}
            <div className="space-y-3">
              <label className="text-xs font-bold uppercase font-mono tracking-wider text-slate-300">
                2. Current Experience Level
              </label>

              <div className="grid grid-cols-3 gap-3">
                {[
                  { id: 'Beginner', label: 'Beginner', sub: 'Full Foundations' },
                  { id: 'Intermediate', label: 'Intermediate', sub: 'Skips Basics' },
                  { id: 'Advanced', label: 'Fast-Tracker', sub: 'Focus on Projects' },
                ].map((tier) => {
                  const isSelected = level === tier.id

                  return (
                    <button
                      key={tier.id}
                      type="button"
                      onClick={() => {
                        soundClick()
                        setLevel(tier.id as 'Beginner' | 'Intermediate' | 'Advanced')
                      }}
                      className={`p-3 rounded-xl border text-center transition ${
                        isSelected
                          ? 'border-accent-violet bg-accent-violet/10 text-accent-violet font-bold shadow-sm'
                          : 'border-slate-800 bg-obsidian-900/60 hover:border-slate-700 text-slate-300'
                      }`}
                    >
                      <p className="text-xs font-semibold">{tier.label}</p>
                      <p className="text-[10px] text-slate-500 font-mono mt-0.5">{tier.sub}</p>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* 3. Daily Study Hours (Slider) */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <label className="font-bold uppercase tracking-wider text-slate-300">
                  3. Daily Available Study Hours
                </label>
                <span className="text-accent-violet font-bold text-sm">
                  {studyHours} Hours / Day
                </span>
              </div>

              <input
                type="range"
                min="0.5"
                max="5.0"
                step="0.5"
                value={studyHours}
                onChange={(e) => setStudyHours(e.target.value)}
                className="w-full h-2 bg-obsidian-800 rounded-lg appearance-none cursor-pointer accent-accent-violet"
              />

              <div className="flex justify-between text-[10px] font-mono text-slate-500">
                <span>0.5h (Micro-sprints)</span>
                <span>2.0h (Recommended)</span>
                <span>5.0h (Intensive)</span>
              </div>
            </div>

            {/* 4. Target Date & Reminder Time */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label
                  htmlFor="targetDate"
                  className="text-xs font-bold uppercase font-mono tracking-wider text-slate-300 flex items-center gap-1.5"
                >
                  <Calendar className="w-3.5 h-3.5 text-accent-violet" />
                  <span>4. Target Completion Date</span>
                </label>
                <input
                  id="targetDate"
                  type="date"
                  value={targetDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => setTargetDate(e.target.value)}
                  required
                  className="w-full bg-obsidian-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-accent-violet font-mono"
                />
              </div>

              <div className="space-y-1.5">
                <label
                  htmlFor="reminderTime"
                  className="text-xs font-bold uppercase font-mono tracking-wider text-slate-300 flex items-center gap-1.5"
                >
                  <Clock className="w-3.5 h-3.5 text-cyan-400" />
                  <span>5. Gentle Reminder Schedule</span>
                </label>
                <input
                  id="reminderTime"
                  type="time"
                  value={reminderTime}
                  onChange={(e) => setReminderTime(e.target.value)}
                  className="w-full bg-obsidian-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-accent-violet font-mono"
                />
              </div>
            </div>

            {/* 6. Known Topics */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label
                  htmlFor="knownTopics"
                  className="text-xs font-bold uppercase font-mono tracking-wider text-slate-300"
                >
                  6. Topics You Already Know (Optional)
                </label>
                <span className="text-[10px] text-slate-500 font-mono">Comma-separated</span>
              </div>

              <textarea
                id="knownTopics"
                value={knownTopics}
                onChange={(e) => setKnownTopics(e.target.value)}
                placeholder="Example: HTML, CSS, basic JavaScript"
                rows={3}
                className="w-full bg-obsidian-900 border border-slate-800 rounded-xl px-4 py-3 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-accent-violet resize-none"
              />

              {/* Suggestions Chips */}
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                <span className="text-[11px] text-slate-500 font-mono flex items-center gap-1 mr-1">
                  <Lightbulb className="w-3 h-3 text-amber-400" />
                  Quick add:
                </span>
                {activeTrackMeta.suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => addSuggestedTopic(suggestion)}
                    className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-obsidian-900 border border-slate-800 hover:border-accent-violet hover:text-accent-violet text-slate-400 transition"
                  >
                    + {suggestion}
                  </button>
                ))}
              </div>
            </div>

            {/* 7. Goal Commitment Pledge Contract */}
            <div className="p-4 rounded-xl bg-obsidian-900/80 border border-slate-800 flex items-start gap-3">
              <input
                id="pledgeCheck"
                type="checkbox"
                checked={commitment}
                onChange={(e) => setCommitment(e.target.checked)}
                required
                className="mt-0.5 w-4 h-4 rounded text-accent-violet bg-obsidian-950 border-slate-700 cursor-pointer accent-accent-violet"
              />
              <label htmlFor="pledgeCheck" className="text-xs text-slate-300 leading-relaxed cursor-pointer">
                <strong>Goal Commitment Contract:</strong> I pledge to study consistently toward my selected
                track. If I miss study sessions, I agree to let SkillSprint AI's Rule-Based Expert System and
                Fuzzy Logic engine intelligently re-route my syllabus without penalty.
              </label>
            </div>

            {/* Error Banner */}
            {error && (
              <div
                role="alert"
                className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs text-rose-800 dark:text-rose-300 flex items-center gap-2"
              >
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-accent-violet via-indigo-600 to-cyan-500 hover:from-accent-violet/90 hover:to-cyan-400 text-white font-semibold text-sm shadow-glow-violet transition flex items-center justify-center gap-2 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  <span>Synthesizing Adaptive Roadmap...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Synthesize Roadmap with Computational Search</span>
                </>
              )}
            </button>
          </form>
        </div>
      </main>
    </>
  )
}

export default OnboardingPage