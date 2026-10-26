import { useEffect, useState, useRef } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import {
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  ExternalLink,
  Edit3,
  Sparkles,
  BookOpen,
  Coffee,
  Flame,
  ArrowRight,
  RefreshCw,
  Copy,
  Check,
  Award,
} from 'lucide-react'
import Navbar from '../components/layout/Navbar'
import {
  getActiveGoal,
  getTodayTasks,
  completeTask,
  swapTaskResource,
  getTopicResources,
  type GoalData,
  type DailyTask,
  type ResourceData,
} from '../api/client'
import { soundClick, soundSuccess, soundAlert } from '../utils/sound'

const DEFAULT_FOCUS_SECONDS = 25 * 60
const DEFAULT_BREAK_SECONDS = 5 * 60
const SCRATCHPAD_KEY = 'skillsprint_workspace_scratchpad'

export default function WorkspacePage() {
  const [searchParams] = useSearchParams()
  const goalIdParam = searchParams.get('goal_id')

  const [goal, setGoal] = useState<GoalData | null>(null)
  const [tasks, setTasks] = useState<DailyTask[]>([])
  const [currentDay, setCurrentDay] = useState<number>(1)
  const [totalDays, setTotalDays] = useState<number>(1)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshIndex, setRefreshIndex] = useState<number>(0)

  // Pomodoro Timer State
  const [timerMode, setTimerMode] = useState<'focus' | 'break'>('focus')
  const [timeLeft, setTimeLeft] = useState<number>(DEFAULT_FOCUS_SECONDS)
  const [isTimerRunning, setIsTimerRunning] = useState<boolean>(false)
  const [pomodoroCount, setPomodoroCount] = useState<number>(1)
  const timerIntervalRef = useRef<number | null>(null)

  // Scratchpad State
  const [scratchpad, setScratchpad] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(SCRATCHPAD_KEY) || ''
    }
    return ''
  })
  const [copiedNote, setCopiedNote] = useState<boolean>(false)

  // Micro-checklist state
  const [checklist, setChecklist] = useState<Record<string, boolean>>({})

  // Resources state for active task
  const [topicResources, setTopicResources] = useState<ResourceData[]>([])
  const [isSwappingResource, setIsSwappingResource] = useState<boolean>(false)
  const [isCompletingSession, setIsCompletingSession] = useState<boolean>(false)
  const [sessionCompleted, setSessionCompleted] = useState<boolean>(false)

  // Primary active task for today
  const activeTask: DailyTask | undefined = tasks.find((t) => t.status === 'pending') || tasks[0]

  useEffect(() => {
    let isMounted = true

    async function fetchWorkspace() {
      try {
        let activeGoalId: number | null = goalIdParam ? Number(goalIdParam) : null
        let resolvedGoal: GoalData | null = null

        const goalRes = await getActiveGoal()
        if (goalRes.goal) {
          if (!activeGoalId || goalRes.goal.id === activeGoalId) {
            activeGoalId = goalRes.goal.id
            resolvedGoal = goalRes.goal
          }
        }

        if (!activeGoalId) {
          if (isMounted) setIsLoading(false)
          return
        }

        if (isMounted && resolvedGoal) {
          setGoal(resolvedGoal)
        }

        const tasksRes = await getTodayTasks(activeGoalId)
        if (isMounted) {
          setTasks(tasksRes.tasks || [])
          setCurrentDay(tasksRes.current_day || 1)
          setTotalDays(tasksRes.total_days || 1)
        }

        // Fetch curated resources for today's primary topic
        const firstTask = (tasksRes.tasks || []).find((t) => t.status === 'pending') || (tasksRes.tasks || [])[0]
        if (firstTask?.topic_id) {
          // Load checklist for topic
          if (typeof window !== 'undefined') {
            const stored = localStorage.getItem(`skillsprint_checklist_${firstTask.topic_id}`)
            if (stored && isMounted) {
              try {
                setChecklist(JSON.parse(stored))
              } catch {
                setChecklist({})
              }
            }
          }

          try {
            const res = await getTopicResources(firstTask.topic_id)
            if (isMounted) {
              setTopicResources(res.resources || [])
            }
          } catch {
            if (isMounted) {
              setTopicResources(firstTask.available_resources || [])
            }
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load workspace data.')
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void fetchWorkspace()

    return () => {
      isMounted = false
    }
  }, [goalIdParam, refreshIndex])

  // Reload when demo date changes via DemoToolbar
  useEffect(() => {
    function handleDateChange() {
      setIsLoading(true)
      setRefreshIndex((prev) => prev + 1)
    }
    window.addEventListener('skillsprint_date_changed', handleDateChange)
    return () => {
      window.removeEventListener('skillsprint_date_changed', handleDateChange)
    }
  }, [])



  // Pomodoro Countdown Effect
  useEffect(() => {
    if (isTimerRunning) {
      timerIntervalRef.current = window.setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            soundSuccess()
            if (timerMode === 'focus') {
              setPomodoroCount((c) => c + 1)
              setTimerMode('break')
              return DEFAULT_BREAK_SECONDS
            } else {
              setTimerMode('focus')
              return DEFAULT_FOCUS_SECONDS
            }
          }
          return prev - 1
        })
      }, 1000)
    } else if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current)
    }

    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current)
      }
    }
  }, [isTimerRunning, timerMode])

  function handleToggleTimer() {
    soundClick()
    setIsTimerRunning((prev) => !prev)
  }

  function handleResetTimer() {
    soundClick()
    setIsTimerRunning(false)
    setTimeLeft(timerMode === 'focus' ? DEFAULT_FOCUS_SECONDS : DEFAULT_BREAK_SECONDS)
  }

  function handleSwitchTimerMode(mode: 'focus' | 'break') {
    soundClick()
    setIsTimerRunning(false)
    setTimerMode(mode)
    setTimeLeft(mode === 'focus' ? DEFAULT_FOCUS_SECONDS : DEFAULT_BREAK_SECONDS)
  }

  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }

  function handleScratchpadChange(value: string) {
    setScratchpad(value)
    if (typeof window !== 'undefined') {
      localStorage.setItem(SCRATCHPAD_KEY, value)
    }
  }

  function handleCopyScratchpad() {
    soundClick()
    if (typeof navigator !== 'undefined' && scratchpad) {
      navigator.clipboard.writeText(scratchpad)
      setCopiedNote(true)
      setTimeout(() => setCopiedNote(false), 2000)
    }
  }

  function handleToggleChecklistItem(key: string) {
    soundClick()
    const next = { ...checklist, [key]: !checklist[key] }
    setChecklist(next)
    if (activeTask?.topic_id && typeof window !== 'undefined') {
      localStorage.setItem(`skillsprint_checklist_${activeTask.topic_id}`, JSON.stringify(next))
    }
  }

  async function handleSwapResource(resourceId: number) {
    if (!activeTask) return
    soundClick()
    setIsSwappingResource(true)
    try {
      const res = await swapTaskResource(activeTask.id, resourceId)
      setTasks((prev) =>
        prev.map((t) => (t.id === activeTask.id ? { ...t, resource: res.resource } : t))
      )
      soundSuccess()
    } catch (err) {
      soundAlert()
      console.error('Resource swap failed:', err)
    } finally {
      setIsSwappingResource(false)
    }
  }

  async function handleCompleteSession() {
    if (!activeTask) return
    soundClick()
    setIsCompletingSession(true)
    try {
      await completeTask(activeTask.id)
      soundSuccess()
      setSessionCompleted(true)
      setTasks((prev) =>
        prev.map((t) => (t.id === activeTask.id ? { ...t, status: 'completed' } : t))
      )
    } catch (err) {
      soundAlert()
      console.error('Task completion failed:', err)
    } finally {
      setIsCompletingSession(false)
    }
  }

  // Micro checklist items tailored to active topic
  const checklistItems = [
    {
      id: 'c1',
      label: `Understand core principles of ${activeTask?.topic_name || 'the topic'}`,
    },
    {
      id: 'c2',
      label: 'Read official documentation and explore implementation patterns',
    },
    {
      id: 'c3',
      label: 'Write hands-on code examples in sandbox or local environment',
    },
    {
      id: 'c4',
      label: 'Verify edge cases and review syntax without looking at notes',
    },
  ]

  const completedChecklistCount = checklistItems.filter((item) => checklist[item.id]).length
  const checklistPercentage = Math.round((completedChecklistCount / checklistItems.length) * 100)

  return (
    <div className="min-h-screen bg-obsidian-950 pastel-focus-mode text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 px-4 sm:px-6 lg:px-8 py-8 max-w-7xl mx-auto w-full space-y-6">
        {/* Top Workspace Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-accent-violet/10 text-accent-violet border border-accent-violet/20 text-[10px] font-mono font-bold uppercase tracking-wider">
                Focus Mode
              </span>
              <span className="text-xs font-mono text-slate-400">
                • Day {currentDay} of {totalDays}
              </span>
              {goal && (
                <span className="text-xs font-mono text-slate-500 hidden sm:inline">
                  • {goal.study_hours_per_day}h Daily Quota
                </span>
              )}
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight mt-1.5">
              {activeTask ? activeTask.topic_name : 'Today’s Computational Focus Workspace'}
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Distraction-free environment for deep deliberate practice, resource study, and hands-on coding.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              onClick={() => soundClick()}
              className="px-4 py-2 rounded-xl border border-white/10 bg-obsidian-900/60 hover:bg-white/5 text-slate-300 text-xs font-semibold transition"
            >
              Dashboard
            </Link>

            {activeTask && (
              <button
                onClick={handleCompleteSession}
                disabled={isCompletingSession || activeTask.status === 'completed' || sessionCompleted}
                className={`px-4 py-2.5 rounded-xl text-xs font-semibold shadow-glow-emerald transition duration-200 flex items-center gap-2 ${
                  activeTask.status === 'completed' || sessionCompleted
                    ? 'bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border border-emerald-500/40 cursor-default'
                    : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white'
                }`}
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>
                  {activeTask.status === 'completed' || sessionCompleted
                    ? 'Session Completed (+100 XP)'
                    : isCompletingSession
                    ? 'Recording Completion...'
                    : 'Complete Session (+100 XP)'}
                </span>
              </button>
            )}
          </div>
        </div>

        {/* Loading / Error States */}
        {isLoading && (
          <div className="glass-panel rounded-3xl p-12 text-center border border-white/10">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-accent-violet border-t-transparent" />
            <p className="mt-3 text-xs font-mono text-slate-400">
              Loading focus workspace, active topic, and curated resources...
            </p>
          </div>
        )}

        {error && (
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs font-mono text-rose-800 dark:text-rose-300 flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={() => setRefreshIndex((prev) => prev + 1)}
              className="px-3 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-800 dark:text-rose-200 font-semibold"
            >
              Retry
            </button>
          </div>
        )}

        {!isLoading && !activeTask && (
          <div className="glass-panel rounded-3xl p-10 text-center border border-white/10 space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-accent-violet/10 text-accent-violet border border-accent-violet/20 flex items-center justify-center mx-auto">
              <BookOpen className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">No Active Sprint Task Today</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              You’re all caught up on scheduled tasks for this date! Visit your curriculum tracks to configure a goal, or view your roadmap.
            </p>
            <div className="pt-2 flex items-center justify-center gap-3">
              <Link
                to="/roadmap"
                className="px-4 py-2 rounded-xl bg-accent-violet text-white text-xs font-semibold shadow-glow-violet transition"
              >
                View Roadmap
              </Link>
              <Link
                to="/tracks"
                className="px-4 py-2 rounded-xl border border-white/10 bg-obsidian-900 text-slate-300 text-xs font-semibold hover:bg-white/5 transition"
              >
                Explore Tracks
              </Link>
            </div>
          </div>
        )}

        {/* Main 2-Column Split */}
        {!isLoading && activeTask && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Pomodoro Timer + Scratchpad (1 Col) */}
            <div className="space-y-6">
              {/* Pomodoro Timer Card */}
              <div className="glass-panel rounded-3xl p-6 border border-white/10 space-y-5">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400 pb-3 border-b border-white/10">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleSwitchTimerMode('focus')}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition ${
                        timerMode === 'focus'
                          ? 'bg-accent-violet text-white shadow-glow-violet'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      Focus (25m)
                    </button>
                    <button
                      onClick={() => handleSwitchTimerMode('break')}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition ${
                        timerMode === 'break'
                          ? 'bg-cyan-500 text-white shadow-glow-cyan'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      Break (5m)
                    </button>
                  </div>
                  <span className="text-accent-violet font-semibold">
                    Sprint #{pomodoroCount}
                  </span>
                </div>

                {/* Big Digital Countdown */}
                <div className="py-2 text-center">
                  <div className="font-mono text-6xl font-black tracking-tight bg-gradient-to-r from-white via-indigo-100 to-accent-violet bg-clip-text text-transparent">
                    {formatTime(timeLeft)}
                  </div>
                  <p className="text-[11px] font-mono text-slate-400 mt-2 flex items-center justify-center gap-1.5">
                    {timerMode === 'focus' ? (
                      <>
                        <Flame className="w-3.5 h-3.5 text-accent-amber" />
                        <span>High-retention interval • Minimize context-switching</span>
                      </>
                    ) : (
                      <>
                        <Coffee className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Rest & consolidate • Grab water and stretch</span>
                      </>
                    )}
                  </p>
                </div>

                {/* Timer Controls */}
                <div className="grid grid-cols-2 gap-2.5">
                  <button
                    onClick={handleToggleTimer}
                    className={`py-2.5 rounded-xl font-semibold text-xs transition duration-200 flex items-center justify-center gap-2 shadow-glow-violet ${
                      isTimerRunning
                        ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold'
                        : 'bg-accent-violet hover:bg-accent-violet/90 text-white'
                    }`}
                  >
                    {isTimerRunning ? (
                      <>
                        <Pause className="w-3.5 h-3.5 fill-current" />
                        <span>Pause</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-3.5 h-3.5 fill-current" />
                        <span>{timeLeft === DEFAULT_FOCUS_SECONDS ? 'Start Focus' : 'Resume'}</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleResetTimer}
                    className="py-2.5 rounded-xl bg-obsidian-900 border border-white/10 hover:bg-white/5 text-slate-300 text-xs font-medium transition flex items-center justify-center gap-1.5"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Reset</span>
                  </button>
                </div>
              </div>

              {/* Quick Session Scratchpad */}
              <div className="glass-card rounded-2xl p-5 border border-white/10 space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-slate-300">
                  <span className="flex items-center gap-1.5">
                    <Edit3 className="w-3.5 h-3.5 text-accent-violet" />
                    <span className="font-bold">Session Scratchpad</span>
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleCopyScratchpad}
                      title="Copy notes to clipboard"
                      className="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-white transition"
                    >
                      {copiedNote ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                    <span className="text-[10px] text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded border border-emerald-400/20 font-semibold">
                      Auto-saved
                    </span>
                  </div>
                </div>

                <textarea
                  value={scratchpad}
                  onChange={(e) => handleScratchpadChange(e.target.value)}
                  placeholder="Jot down syntax patterns, terminal commands, algorithmic complexities, or key take-aways for weekly reflection..."
                  className="w-full h-36 bg-obsidian-950/80 border border-white/10 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-accent-violet/60 focus:ring-1 focus:ring-accent-violet/30 resize-none font-mono"
                />
              </div>

              {/* Session XP Reward Card */}
              <div className="glass-card rounded-2xl p-5 border border-white/10 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-accent-amber">
                  <Award className="w-4 h-4" />
                  <span>Cognitive Sprint Rewards</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Completing today’s focus milestone contributes to your study consistency streak and updates your A* graph state without deadline drift.
                </p>
              </div>
            </div>

            {/* Right Column: Topic Curriculum & Curated Resources (2 Cols) */}
            <div className="lg:col-span-2 space-y-6">
              {/* Curated Resources Panel */}
              <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-white/10">
                  <div>
                    <h2 className="font-bold text-white text-lg">Curated Learning Curriculum & Resources</h2>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Hand-curated free resources matched to <strong className="text-slate-200">{activeTask.topic_name}</strong>
                    </p>
                  </div>
                  <span className="text-xs font-mono text-cyan-400 bg-cyan-400/10 px-2.5 py-1 rounded-full border border-cyan-400/20 w-fit">
                    {activeTask.planned_minutes} Mins Planned Load
                  </span>
                </div>

                {/* Primary Active Resource Card */}
                {activeTask.resource && (
                  <div className="p-5 rounded-2xl bg-obsidian-900/90 border border-accent-violet/40 shadow-glow-violet transition space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-accent-violet/20 text-accent-violet border border-accent-violet/30 font-bold uppercase">
                        Active Selection • {activeTask.resource.resource_type || 'Curated'}
                      </span>
                      {activeTask.resource.estimated_minutes && (
                        <span className="text-xs font-mono text-slate-400">
                          {activeTask.resource.estimated_minutes} Mins
                        </span>
                      )}
                    </div>

                    <h3 className="font-bold text-base text-white">{activeTask.resource.title}</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      Primary learning module selected by the computational coach for optimal retention.
                    </p>

                    <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-white/5">
                      <span className="text-[11px] font-mono text-slate-500">
                        Target Resource URL
                      </span>
                      <a
                        href={activeTask.resource.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 text-xs font-semibold text-accent-violet hover:underline"
                      >
                        <span>Launch Resource in New Tab</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                )}

                {/* Alternative Curated Resources List with One-Click Swapping */}
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                    <span className="flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Alternative Curated Resources for this Milestone</span>
                    </span>
                    {isSwappingResource && (
                      <span className="text-[11px] font-mono text-cyan-400 animate-pulse flex items-center gap-1">
                        <RefreshCw className="w-3 h-3 animate-spin" />
                        Updating Schedule...
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {topicResources.length > 0 ? (
                      topicResources.map((res, idx) => {
                        const isCurrent = activeTask.resource?.url === res.url || activeTask.resource?.id === res.id
                        return (
                          <div
                            key={res.id || idx}
                            className={`p-4 rounded-2xl border transition duration-200 space-y-2.5 ${
                              isCurrent
                                ? 'bg-accent-violet/10 border-accent-violet/50 shadow-sm'
                                : 'bg-obsidian-900/60 border-white/10 hover:border-white/20 hover:bg-obsidian-900'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span
                                className={`text-[9px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                                  res.resource_type === 'video'
                                    ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                    : res.resource_type === 'interactive'
                                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                                    : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                }`}
                              >
                                {res.resource_type}
                              </span>
                              {res.estimated_minutes && (
                                <span className="text-[10px] font-mono text-slate-500">
                                  {res.estimated_minutes}m
                                </span>
                              )}
                            </div>

                            <h4 className="font-bold text-xs text-slate-200 line-clamp-1">
                              {res.title}
                            </h4>

                            <div className="pt-2 flex items-center justify-between text-xs">
                              <a
                                href={res.url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-slate-400 hover:text-white flex items-center gap-1 text-[11px]"
                              >
                                <span>Preview</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>

                              {res.id && !isCurrent && (
                                <button
                                  onClick={() => handleSwapResource(res.id!)}
                                  disabled={isSwappingResource}
                                  className="px-2.5 py-1 rounded-lg bg-accent-violet/20 hover:bg-accent-violet/30 text-accent-violet text-[11px] font-semibold transition"
                                >
                                  Swap Resource
                                </button>
                              )}

                              {isCurrent && (
                                <span className="text-[11px] font-mono text-emerald-400 font-bold flex items-center gap-1">
                                  <Check className="w-3 h-3" /> Selected
                                </span>
                              )}
                            </div>
                          </div>
                        )
                      })
                    ) : (
                      <p className="text-xs text-slate-500 font-mono col-span-2 py-4">
                        Primary curated resource active for this topic.
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Practical Micro-Deliverable Checklist */}
              <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-white text-xs uppercase font-mono tracking-wider">
                      Session Micro-Deliverable Checklist
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Verify topic mastery before marking the session complete
                    </p>
                  </div>
                  <span className="font-mono text-xs font-bold text-accent-violet">
                    {checklistPercentage}% Done
                  </span>
                </div>

                {/* Progress bar */}
                <div className="h-1.5 w-full bg-obsidian-950 rounded-full overflow-hidden border border-white/5">
                  <div
                    className="h-full bg-gradient-to-r from-accent-violet to-emerald-400 transition-all duration-300"
                    style={{ width: `${checklistPercentage}%` }}
                  />
                </div>

                <div className="space-y-2.5 text-xs text-slate-300 pt-1">
                  {checklistItems.map((item) => {
                    const isChecked = Boolean(checklist[item.id])
                    return (
                      <label
                        key={item.id}
                        className={`flex items-center gap-3 p-3 rounded-xl border transition cursor-pointer ${
                          isChecked
                            ? 'bg-emerald-500/10 border-emerald-500/30 text-white'
                            : 'bg-obsidian-900/60 border-white/10 hover:border-white/20'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => handleToggleChecklistItem(item.id)}
                          className="w-4 h-4 rounded text-accent-violet bg-obsidian-950 border-white/20 focus:ring-accent-violet"
                        />
                        <span className={isChecked ? 'line-through text-slate-400' : 'text-slate-200'}>
                          {item.label}
                        </span>
                      </label>
                    )
                  })}
                </div>
              </div>

              {/* Quick Jump to Replanning */}
              <div className="p-4 rounded-2xl bg-gradient-to-r from-accent-amber/10 via-orange-500/10 to-transparent border border-accent-amber/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <span className="text-xs font-bold text-accent-amber flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Fell behind on study hours?</span>
                  </span>
                  <p className="text-xs text-slate-400">
                    Use the Expert System Adaptive Rescheduler to rebalance upcoming sessions without extending your target date.
                  </p>
                </div>
                <Link
                  to="/replanning"
                  onClick={() => soundClick()}
                  className="px-3.5 py-1.5 rounded-xl bg-accent-amber/20 hover:bg-accent-amber/30 text-amber-800 dark:text-amber-300 text-xs font-semibold whitespace-nowrap transition flex items-center gap-1 w-fit"
                >
                  <span>Open Rescheduler</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
