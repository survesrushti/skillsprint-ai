import { useEffect, useState } from 'react'
import {
  useLocation,
  useNavigate,
  useSearchParams,
} from 'react-router-dom'
import {
  BookOpen,
  ExternalLink,
  GitBranch,
  Zap,
  SlidersHorizontal,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Sparkles,
  Flame,
  Lock,
  Flag,
  Award,
  ChevronDown,
} from 'lucide-react'

import Navbar from '../components/layout/Navbar'
import {
  completeTask,
  generateRoadmap,
  getActiveRoadmap,
  getProgressSummary,
  getTodayTasks,
  rescheduleRoadmap,
  skipTask,
  swapTaskResource,
  type ProgressSummaryResponse,
  type TodayTasksResponse,
  type RoadmapResponse,
  type DailyTask,
} from '../api/client'
import { soundClick, soundSuccess, soundAlert } from '../utils/sound'

type PreviewTask = {
  topic_id?: number
  name?: string
  topic_name?: string
  minutes?: number
  planned_minutes?: number
  difficulty?: number
  is_optional?: boolean
  status?: string
}

type PreviewDay = {
  day?: number
  day_number?: number
  date?: string
  total_minutes?: number
  tasks?: PreviewTask[]
}

type ReplanPreviewResponse = {
  status?: string
  message?: string
  replanned?: boolean
  preview?: boolean
  saved?: boolean
  strategy?: string
  roadmap_id?: number | null
  roadmap_version?: number
  tasks_replanned?: number
  plan_end_date?: string
  target_date?: {
    old?: string
    new?: string
    changed?: boolean
  }
  warnings?: string[]
  metrics?: Record<string, unknown>
  ci?: {
    fuzzy?: unknown
    expert?: {
      selected_strategy?: string
      [key: string]: unknown
    }
    adaptation?: unknown
    search?: unknown
  }
  roadmap?: PreviewDay[]
}

function formatDate(value?: string) {
  if (!value) return 'Not available'
  const parsed = new Date(`${value.slice(0, 10)}T12:00:00`)
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function RoadmapPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [roadmapData, setRoadmapData] = useState<RoadmapResponse | null>(null)
  const [todayData, setTodayData] = useState<TodayTasksResponse | null>(null)
  const [progressData, setProgressData] = useState<ProgressSummaryResponse | null>(null)

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [taskActionError, setTaskActionError] = useState('')
  const [taskActionId, setTaskActionId] = useState<number | null>(null)

  const [replanMessage, setReplanMessage] = useState('')
  const [isReplanning, setIsReplanning] = useState(false)
  const [isApplyingReplan, setIsApplyingReplan] = useState(false)
  const [replanPreview, setReplanPreview] = useState<ReplanPreviewResponse | null>(null)
  const [swappingTaskId, setSwappingTaskId] = useState<number | null>(null)

  const resolvedGoalId = Number(
    searchParams.get('goal_id') ||
    (location.state as { goalId?: number | string } | null)?.goalId ||
    localStorage.getItem('skillsprint_active_goal_id')
  )

  const hasValidGoalId = Number.isInteger(resolvedGoalId) && resolvedGoalId > 0

  async function refreshLearningData(goalId: number) {
    const [today, progress] = await Promise.all([
      getTodayTasks(goalId),
      getProgressSummary(goalId),
    ])
    setTodayData(today)
    setProgressData(progress)
  }

  useEffect(() => {
    if (!hasValidGoalId) {
      return
    }

    localStorage.setItem('skillsprint_active_goal_id', String(resolvedGoalId))
    let cancelled = false

    const loadRoadmap = async () => {
      try {
        let data: RoadmapResponse
        try {
          data = await getActiveRoadmap(resolvedGoalId)
        } catch {
          // If no active roadmap exists yet, generate it for the goal
          data = await generateRoadmap(resolvedGoalId)
        }

        if (cancelled) return
        setRoadmapData(data)

        try {
          const [today, progress] = await Promise.all([
            getTodayTasks(resolvedGoalId),
            getProgressSummary(resolvedGoalId),
          ])

          if (!cancelled) {
            setTodayData(today)
            setProgressData(progress)
          }
        } catch (statsError) {
          if (!cancelled) {
            setTaskActionError(
              statsError instanceof Error
                ? statsError.message
                : 'Could not load your progress.'
            )
          }
        }
      } catch (roadmapError) {
        if (cancelled) return
        console.error('Roadmap loading error:', roadmapError)
        setError(
          roadmapError instanceof Error
            ? roadmapError.message
            : 'Could not load your roadmap.'
        )
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    loadRoadmap()

    return () => {
      cancelled = true
    }
  }, [hasValidGoalId, resolvedGoalId])

  useEffect(() => {
    function handleDateChange() {
      if (hasValidGoalId && resolvedGoalId) {
        refreshLearningData(resolvedGoalId)
      }
    }

    window.addEventListener('skillsprint_date_changed', handleDateChange)
    return () => {
      window.removeEventListener('skillsprint_date_changed', handleDateChange)
    }
  }, [hasValidGoalId, resolvedGoalId])

  async function handleTaskAction(taskId: number, action: 'complete' | 'skip') {
    if (!roadmapData) return

    soundClick()
    setTaskActionId(taskId)
    setTaskActionError('')

    try {
      if (action === 'complete') {
        await completeTask(taskId)
        soundSuccess()
      } else {
        await skipTask(taskId)
      }

      await refreshLearningData(roadmapData.goal.id)
    } catch (actionError) {
      soundAlert()
      setTaskActionError(
        actionError instanceof Error
          ? actionError.message
          : 'Could not update the task. Please try again.'
      )
    } finally {
      setTaskActionId(null)
    }
  }

  async function handleSwapResource(taskId: number, resourceId: number) {
    if (!todayData) return

    soundClick()
    setSwappingTaskId(taskId)
    setTaskActionError('')

    try {
      const res = await swapTaskResource(taskId, resourceId)
      if (res.resource) {
        soundSuccess()
        setTodayData({
          ...todayData,
          tasks: todayData.tasks.map((t) =>
            t.id === taskId ? { ...t, resource: res.resource } : t
          ),
          overdue_tasks: todayData.overdue_tasks.map((t) =>
            t.id === taskId ? { ...t, resource: res.resource } : t
          ),
        })
      }
    } catch (swapErr) {
      soundAlert()
      setTaskActionError(
        swapErr instanceof Error
          ? swapErr.message
          : 'Could not swap resource. Please try again.'
      )
    } finally {
      setSwappingTaskId(null)
    }
  }

  async function handleReplan() {
    if (!roadmapData || isReplanning) return

    soundClick()
    setIsReplanning(true)
    setReplanMessage('')
    setReplanPreview(null)

    try {
      const result = (await rescheduleRoadmap(roadmapData.goal.id, {
        preview: true,
      })) as ReplanPreviewResponse

      setReplanPreview(result)

      if (!result.replanned) {
        setReplanPreview(null)
        setReplanMessage(result.message || 'No roadmap changes are needed.')
        return
      }

      soundSuccess()
      setReplanMessage(result.message || 'Adaptive preview generated.')
    } catch (replanError) {
      soundAlert()
      setReplanMessage(
        replanError instanceof Error
          ? replanError.message
          : 'Could not preview the revised roadmap. Please try again.'
      )
    } finally {
      setIsReplanning(false)
    }
  }

  async function handleApplyReplan() {
    if (!roadmapData || isApplyingReplan || !replanPreview) return

    soundClick()
    setIsApplyingReplan(true)
    setReplanMessage('')

    try {
      const result = (await rescheduleRoadmap(roadmapData.goal.id, {
        preview: false,
      })) as ReplanPreviewResponse

      setReplanPreview(null)
      const nextVer = result.roadmap_version
        ? `Version ${result.roadmap_version}`
        : 'Revised plan'
      setReplanMessage(
        `Adaptive roadmap applied successfully! ${nextVer} is now active.`
      )

      soundSuccess()
      const updatedRoadmap = await getActiveRoadmap(roadmapData.goal.id)
      setRoadmapData(updatedRoadmap)
      await refreshLearningData(roadmapData.goal.id)
    } catch (applyError) {
      soundAlert()
      setReplanMessage(
        applyError instanceof Error
          ? applyError.message
          : 'Could not apply the revised roadmap. Please try again.'
      )
    } finally {
      setIsApplyingReplan(false)
    }
  }

  // Fallback 1: No valid Goal ID
  if (!hasValidGoalId) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen text-slate-100 px-4 sm:px-6 lg:px-8 py-20 max-w-3xl mx-auto">
          <div className="glass-panel rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-center space-y-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-rose-300 font-mono">
              Roadmap Error
            </p>
            <h1 className="text-2xl sm:text-3xl font-bold text-white">
              No Learning Goal Found
            </h1>
            <p className="text-sm text-slate-300 max-w-md mx-auto">
              Please choose a learning track and configure your study goal to synthesize a personalized roadmap.
            </p>
            <div className="pt-2">
              <button
                onClick={() => {
                  soundClick()
                  navigate('/onboarding')
                }}
                className="px-6 py-2.5 rounded-xl bg-accent-violet hover:bg-accent-violet/90 text-white text-xs font-semibold shadow-glow-violet transition"
              >
                Set Up Learning Goal
              </button>
            </div>
          </div>
        </main>
      </>
    )
  }

  // Fallback 2: Loading
  if (isLoading) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen text-slate-100 px-4 sm:px-6 lg:px-8 py-20 max-w-4xl mx-auto">
          <div className="glass-panel rounded-3xl p-8 sm:p-12 border border-slate-800 text-center space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-violet/10 text-accent-violet text-xs font-mono">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Computational Search Engine</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
              Synthesizing Your Adaptive Roadmap...
            </h1>
            <p className="text-sm text-slate-400 max-w-lg mx-auto">
              A* Search is evaluating topic dependencies and packing your daily study capacity.
            </p>
            <div className="max-w-md mx-auto h-2 overflow-hidden rounded-full bg-obsidian-900 border border-slate-800">
              <div className="h-full w-2/3 animate-pulse rounded-full bg-gradient-to-r from-accent-violet to-cyan-400" />
            </div>
          </div>
        </main>
      </>
    )
  }

  // Fallback 3: Error
  if (error) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen text-slate-100 px-4 sm:px-6 lg:px-8 py-20 max-w-3xl mx-auto">
          <div className="glass-panel rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-center space-y-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-rose-300 font-mono">
              Roadmap Synthesis Notice
            </p>
            <h1 className="text-2xl sm:text-3xl font-bold text-white">
              Could Not Load Roadmap
            </h1>
            <p className="text-sm text-rose-200 max-w-md mx-auto">{error}</p>
            <div className="pt-2">
              <button
                onClick={() => {
                  soundClick()
                  navigate('/onboarding')
                }}
                className="px-6 py-2.5 rounded-xl bg-accent-violet hover:bg-accent-violet/90 text-white text-xs font-semibold shadow-glow-violet transition"
              >
                Create Goal Again
              </button>
            </div>
          </div>
        </main>
      </>
    )
  }

  if (!roadmapData) return null

  const completionPercentage = progressData?.summary.completion_percentage ?? 0
  const previewDays = replanPreview?.roadmap ?? []

  return (
    <>
      <Navbar />

      <main className="min-h-screen text-slate-100 px-4 sm:px-6 lg:px-8 py-8 max-w-7xl mx-auto w-full space-y-8">
        {/* ==================== TOP HEADER & ACTIONS ==================== */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-accent-violet shadow-sm" />
              <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                Personalized Adaptive Roadmap
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-accent-violet/10 text-accent-violet border border-accent-violet/20 font-semibold">
                Version {roadmapData.roadmap_version ?? 1}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Constructed via Heuristic A* Search considering topic dependencies, target date, and daily study capacity.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleReplan}
              disabled={isReplanning}
              className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-accent-violet to-indigo-600 hover:from-accent-violet/90 hover:to-indigo-500 text-white text-xs font-semibold shadow-glow-violet transition flex items-center gap-1.5 disabled:opacity-50"
            >
              <Zap className="w-3.5 h-3.5 text-cyan-300" />
              <span>{isReplanning ? 'Analyzing...' : 'Preview Adaptive Replan'}</span>
            </button>

            <button
              onClick={() => {
                soundClick()
                navigate('/onboarding')
              }}
              className="px-3 py-2 rounded-xl bg-obsidian-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white text-xs font-mono transition"
            >
              New Goal
            </button>
          </div>
        </div>

        {/* Status notification banner if any */}
        {replanMessage && (
          <div
            role="status"
            className="rounded-2xl border border-accent-violet/30 bg-accent-violet/10 p-4 text-xs font-mono text-accent-violet dark:text-indigo-200 flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4 text-accent-violet shrink-0" />
            <span>{replanMessage}</span>
          </div>
        )}

        {/* ==================== 4-STAT SUMMARY TILES ==================== */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="glass-card rounded-2xl p-4 border border-slate-800">
            <p className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
              Skill Level
            </p>
            <p className="text-lg font-bold text-white mt-1">
              {roadmapData.goal.skill_level}
            </p>
            <p className="text-[10px] text-slate-500 font-mono mt-0.5">Prior knowledge tier</p>
          </div>

          <div className="glass-card rounded-2xl p-4 border border-slate-800">
            <p className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
              Study Time
            </p>
            <p className="text-lg font-bold text-accent-violet mt-1">
              {roadmapData.goal.study_hours_per_day} hrs/day
            </p>
            <p className="text-[10px] text-slate-500 font-mono mt-0.5">Daily time budget</p>
          </div>

          <div className="glass-card rounded-2xl p-4 border border-slate-800">
            <p className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
              Target Date
            </p>
            <p className="text-lg font-bold text-cyan-400 mt-1">
              {formatDate(roadmapData.goal.target_date)}
            </p>
            <p className="text-[10px] text-slate-500 font-mono mt-0.5">Commitment deadline</p>
          </div>

          <div className="glass-card rounded-2xl p-4 border border-slate-800">
            <p className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
              Total Roadmap Days
            </p>
            <p className="text-lg font-bold text-accent-emerald mt-1">
              {roadmapData.ci.search.total_days} Days
            </p>
            <p className="text-[10px] text-slate-500 font-mono mt-0.5">
              {roadmapData.ci.search.total_minutes} total minutes
            </p>
          </div>
        </section>

        {/* ==================== OVERALL PROGRESS CARD ==================== */}
        <section className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase font-mono tracking-wider text-cyan-400 font-semibold">
                Your Progress
              </p>
              <h2 className="text-xl font-bold text-white mt-1">
                Curriculum Velocity & Trajectory
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                {progressData
                  ? `${progressData.summary.completed_tasks} of ${progressData.summary.total_tasks} topics completed`
                  : 'Tracking your study milestones...'}
              </p>
            </div>

            <div className="flex items-center gap-3">
              {progressData && (
                <div className="text-right">
                  <p className="text-xs text-slate-400 font-mono">Status</p>
                  <p
                    className={`text-xs font-mono font-bold ${
                      progressData.progress.progress_difference >= 0
                        ? 'text-accent-emerald'
                        : 'text-amber-400'
                    }`}
                  >
                    {progressData.progress.progress_difference >= 0
                      ? 'On Schedule'
                      : 'Behind Schedule'}
                  </p>
                </div>
              )}
              <div className="rounded-xl bg-obsidian-900 border border-slate-800 px-3.5 py-2 text-right">
                <span className="text-2xl font-bold font-mono text-cyan-400">
                  {completionPercentage}%
                </span>
                <p className="text-[10px] text-slate-500 font-mono">Completion</p>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="h-2.5 overflow-hidden rounded-full bg-obsidian-900 border border-slate-800">
            <div
              className="h-full rounded-full bg-gradient-to-r from-accent-violet via-indigo-500 to-cyan-400 transition-all duration-700"
              style={{
                width: `${Math.min(100, Math.max(0, completionPercentage))}%`,
              }}
            />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-left">
            <div className="p-3 rounded-xl bg-obsidian-900/60 border border-slate-800/80">
              <p className="text-[10px] text-slate-500 font-mono uppercase">Completed</p>
              <p className="text-base font-bold text-white mt-1">
                {String(progressData?.summary.completed_tasks ?? '—')}
              </p>
              <p className="text-[10px] text-slate-500 font-mono">Topics done</p>
            </div>

            <div className="p-3 rounded-xl bg-obsidian-900/60 border border-slate-800/80">
              <p className="text-[10px] text-slate-500 font-mono uppercase">Remaining</p>
              <p className="text-base font-bold text-slate-300 mt-1">
                {String(progressData?.summary.remaining_tasks ?? '—')}
              </p>
              <p className="text-[10px] text-slate-500 font-mono">Topics left</p>
            </div>

            <div className="p-3 rounded-xl bg-obsidian-900/60 border border-slate-800/80">
              <p className="text-[10px] text-slate-500 font-mono uppercase">Actual Study Time</p>
              <p className="text-base font-bold text-indigo-300 mt-1">
                {progressData
                  ? `${Math.round((progressData.summary.actual_study_minutes / 60) * 10) / 10}h`
                  : '—'}
              </p>
              <p className="text-[10px] text-slate-500 font-mono">Logged time</p>
            </div>

            <div className="p-3 rounded-xl bg-obsidian-900/60 border border-slate-800/80">
              <p className="text-[10px] text-slate-500 font-mono uppercase">Study Streak</p>
              <p className="text-base font-bold text-amber-800 dark:text-amber-300 mt-1 flex items-center gap-1">
                <span>{progressData?.streak.current_streak_days ?? '0'}</span>
                <Flame className="w-4 h-4 text-amber-400" />
              </p>
              <p className="text-[10px] text-slate-500 font-mono">Consecutive days</p>
            </div>
          </div>
        </section>

        {/* ==================== TODAY'S SPRINT TASKS ==================== */}
        <section className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                <h3 className="font-bold text-white text-base">Today's Study Sprint</h3>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {todayData
                  ? `Day ${todayData.current_day} of ${todayData.total_days} • ${todayData.date}`
                  : 'Fetching scheduled sprint...'}
              </p>
            </div>

            {todayData && (
              <div className="text-xs font-mono text-cyan-300 bg-cyan-400/10 px-3 py-1.5 rounded-xl border border-cyan-400/20">
                {todayData.summary.completed_minutes_today} / {todayData.summary.planned_minutes_today} min completed
              </div>
            )}
          </div>

          {taskActionError && (
            <div
              role="alert"
              className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300 flex items-center gap-2"
            >
              <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{taskActionError}</span>
            </div>
          )}

          {todayData && todayData.tasks.length === 0 && (
            <div className="rounded-xl bg-obsidian-900 border border-slate-800 p-6 text-center text-xs text-slate-400 font-mono">
              No tasks currently scheduled for today. You are caught up!
            </div>
          )}

          <div className="space-y-3">
            {todayData?.tasks.map((task: DailyTask) => {
              const isPending = task.status === 'pending'
              const isBusy = taskActionId === task.id

              return (
                <div
                  key={task.id}
                  className="glass-card rounded-2xl p-4 sm:p-5 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-bold text-sm text-white">{task.topic_name}</p>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-obsidian-900 text-slate-400 border border-slate-800">
                        {task.planned_minutes} min
                      </span>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase font-semibold ${
                          task.status === 'completed'
                            ? 'bg-accent-emerald/20 text-accent-emerald'
                            : task.status === 'skipped'
                              ? 'bg-amber-400/20 text-amber-800 dark:text-amber-300'
                              : 'bg-accent-violet/20 text-accent-violet'
                        }`}
                      >
                        {task.status}
                      </span>
                    </div>

                    {/* Assigned Resource */}
                    {task.resource && (
                      <div className="flex flex-wrap items-center gap-2 pt-0.5">
                        <a
                          href={task.resource.url}
                          target="_blank"
                          rel="noreferrer noopener"
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-accent-violet/10 border border-accent-violet/30 text-xs font-mono text-accent-violet hover:text-white hover:bg-accent-violet/20 transition"
                        >
                          <BookOpen className="w-3.5 h-3.5" />
                          <span>{task.resource.title}</span>
                          <ExternalLink className="w-3 h-3 opacity-70" />
                        </a>
                        <span className="text-[10px] font-mono text-slate-500 uppercase">
                          {task.resource.resource_type}
                        </span>
                      </div>
                    )}

                    {/* Swap Resource Dropdown */}
                    {task.available_resources && task.available_resources.length > 1 && (
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-slate-500 text-[11px] font-mono">Swap resource:</span>
                        <select
                          disabled={swappingTaskId === task.id || isBusy}
                          value={task.resource?.id ?? ''}
                          onChange={(e) => handleSwapResource(task.id, Number(e.target.value))}
                          className="bg-obsidian-900 border border-slate-800 rounded-lg px-2 py-1 text-xs text-slate-300 focus:outline-none focus:border-accent-violet"
                        >
                          {task.available_resources.map((r) => (
                            <option key={r.id ?? r.url} value={r.id}>
                              {r.title} ({r.resource_type})
                            </option>
                          ))}
                        </select>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      disabled={!isPending || isBusy}
                      onClick={() => handleTaskAction(task.id, 'complete')}
                      className="px-3.5 py-2 rounded-xl bg-accent-emerald hover:bg-emerald-400 text-slate-950 text-xs font-bold transition disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{isBusy ? 'Saving...' : 'Complete'}</span>
                    </button>

                    <button
                      disabled={!isPending || isBusy}
                      onClick={() => handleTaskAction(task.id, 'skip')}
                      className="px-3 py-2 rounded-xl bg-obsidian-900 border border-slate-800 hover:border-amber-400/50 text-slate-400 hover:text-amber-300 text-xs font-mono transition disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      Skip
                    </button>
                  </div>
                </div>
              )
            })}
          </div>

          {todayData && todayData.summary.overdue_count > 0 && (
            <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
              <div className="text-xs text-amber-800 dark:text-amber-200">
                <span className="font-bold">Attention:</span> You have {todayData.summary.overdue_count} overdue task(s) ({todayData.summary.overdue_minutes} min).
                Click <strong>"Preview Adaptive Replan"</strong> above to rebalance your timeline!
              </div>
            </div>
          )}
        </section>

        {/* ==================== MAIN ROADMAP TIMELINE & PREFERENCES ==================== */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Visual Roadmap Tree (2 Cols) */}
          <div className="lg:col-span-2 glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
                <GitBranch className="w-4 h-4 text-accent-violet" />
                <span>
                  Track Curriculum ({roadmapData.roadmap.length} Days •{' '}
                  {roadmapData.roadmap.reduce((acc, d) => acc + d.tasks.length, 0)} Tasks)
                </span>
              </div>

              <div className="flex items-center gap-3 text-[10px] font-mono text-slate-400">
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-accent-emerald" /> Done
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-accent-violet" /> Current
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-slate-600" /> Queued
                </span>
              </div>
            </div>

            {/* Vertical Timeline Nodes */}
            <div className="space-y-4 relative">
              {roadmapData.roadmap.map((day, idx) => {
                const isCurrent = todayData ? day.day === todayData.current_day : idx === 0
                const isPast = todayData ? day.day < todayData.current_day : false
                const isLast = idx === roadmapData.roadmap.length - 1

                return (
                  <div key={day.day} className="flex items-start gap-4">
                    {/* Node Pin & Vertical Connector */}
                    <div className="flex flex-col items-center">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-mono font-bold transition ${
                          isPast
                            ? 'bg-accent-emerald/20 border-2 border-accent-emerald text-accent-emerald'
                            : isCurrent
                              ? 'bg-accent-violet border-2 border-white text-white shadow-glow-violet animate-subtle-pulse'
                              : isLast
                                ? 'bg-obsidian-900 border-2 border-slate-800 text-slate-500'
                                : 'bg-obsidian-900 border-2 border-slate-700 text-slate-500'
                        }`}
                      >
                        {isPast ? (
                          <CheckCircle2 className="w-4 h-4" />
                        ) : isCurrent ? (
                          <span>{day.day}</span>
                        ) : isLast ? (
                          <Flag className="w-3.5 h-3.5" />
                        ) : (
                          <Lock className="w-3 h-3 text-slate-600" />
                        )}
                      </div>

                      {!isLast && (
                        <div
                          className={`w-0.5 h-16 mt-1 transition ${
                            isPast
                              ? 'bg-accent-emerald/40'
                              : isCurrent
                                ? 'bg-gradient-to-b from-accent-violet to-slate-800'
                                : 'bg-slate-800'
                          }`}
                        />
                      )}
                    </div>

                    {/* Day Task Details Card */}
                    <div
                      className={`glass-card rounded-2xl p-4 flex-1 border transition ${
                        isCurrent
                          ? 'border-accent-violet/60 bg-accent-violet/5'
                          : 'border-slate-800/80 bg-obsidian-900/60'
                      }`}
                    >
                      <div className="flex items-center justify-between pb-2 border-b border-slate-800/60">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-slate-200">
                            Day {day.day} {day.date ? `• ${formatDate(day.date)}` : ''}
                          </h4>
                          {isCurrent && (
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-accent-violet text-white font-bold">
                              Current Sprint
                            </span>
                          )}
                          {isLast && (
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                              Terminal Capstone
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] font-mono text-cyan-400">
                          {day.total_minutes} min
                        </span>
                      </div>

                      {/* Day Tasks List */}
                      <div className="mt-3 space-y-2">
                        {day.tasks.map((task, tIdx) => (
                          <div
                            key={`${day.day}-${task.topic_id}-${tIdx}`}
                            className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2.5 rounded-xl bg-obsidian-950/60 border border-slate-800/60"
                          >
                            <div>
                              <p className="text-xs font-bold text-slate-200">{task.name}</p>
                              <div className="flex flex-wrap items-center gap-2 mt-1">
                                <span className="text-[10px] font-mono text-slate-500">
                                  Difficulty {task.difficulty}
                                </span>
                                {task.is_optional && (
                                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-amber-400/10 text-amber-800 dark:text-amber-300">
                                    Optional
                                  </span>
                                )}
                                {task.resource && (
                                  <a
                                    href={task.resource.url}
                                    target="_blank"
                                    rel="noreferrer noopener"
                                    className="inline-flex items-center gap-1 text-[11px] font-mono text-cyan-400 hover:underline"
                                  >
                                    <BookOpen className="w-3 h-3" />
                                    <span>{task.resource.title}</span>
                                    <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                                  </a>
                                )}
                              </div>
                            </div>
                            <span className="text-xs font-mono text-slate-400 shrink-0">
                              {task.minutes} min
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Right: Study Preferences Sidebar (1 Col) */}
          <div className="space-y-6">
            <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-5">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
                <SlidersHorizontal className="w-4 h-4 text-accent-violet" />
                <h3 className="font-bold text-white text-sm">Study Preferences</h3>
              </div>

              {/* Preference 1: Daily Study Hours */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-300">Daily Study Hours</span>
                  <span className="text-accent-violet font-bold">
                    {roadmapData.goal.study_hours_per_day} hrs/day
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 leading-tight">
                  Configured capacity used by A* search to calculate milestones and prevent overload.
                </p>
              </div>

              {/* Preference 2: Gentle Reminder */}
              <div className="space-y-2 pt-2 border-t border-slate-800/80">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-200">Gentle Reminder Time</span>
                  <span className="text-[10px] font-mono text-accent-emerald">Active</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-mono text-slate-300 bg-obsidian-900 border border-slate-800 rounded-xl px-3 py-2">
                  <Clock className="w-3.5 h-3.5 text-accent-violet" />
                  <span>
                    {typeof window !== 'undefined'
                      ? localStorage.getItem('skillsprint_reminder_time') || '19:30'
                      : '19:30'}{' '}
                    Daily
                  </span>
                </div>
                <p className="text-[10px] text-slate-500">
                  Pre-sprint acoustic notification primes your study session on time.
                </p>
              </div>

              {/* Preference 3: Target Goal Pledge */}
              <div className="p-4 rounded-2xl bg-indigo-950/20 border border-indigo-800/30 text-xs text-slate-300 space-y-2">
                <div className="flex items-center gap-2 text-indigo-300 font-bold">
                  <Award className="w-4 h-4 text-accent-violet" />
                  <span>Active Goal Pledge</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Target completion: <strong className="text-slate-200">{formatDate(roadmapData.goal.target_date)}</strong>.
                  Status: <strong className="text-accent-emerald">Active Commitment Contract</strong>.
                </p>
              </div>
            </div>

            {/* CI Engine Metrics Card */}
            <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <h3 className="font-bold text-white text-sm">Computational Intelligence</h3>
              </div>

              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-obsidian-900 border border-slate-800/80">
                  <p className="text-[10px] font-mono uppercase text-accent-violet font-semibold">
                    1. A* Path Search
                  </p>
                  <p className="text-xs text-slate-300 mt-1">
                    Nodes explored: <strong>{roadmapData.ci.search.nodes_expanded}</strong>
                  </p>
                  <p className="text-[10px] font-mono text-slate-500 mt-0.5">
                    Admissible heuristic guaranteed
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-obsidian-900 border border-slate-800/80">
                  <p className="text-[10px] font-mono uppercase text-cyan-400 font-semibold">
                    2. Expert Rule Engine
                  </p>
                  <p className="text-xs text-slate-300 mt-1">
                    Strategy:{' '}
                    <strong className="text-cyan-300">
                      {String(
                        (roadmapData.ci.expert as { selected_strategy?: string })?.selected_strategy ||
                          'STANDARD_FLOW'
                      )}
                    </strong>
                  </p>
                  <p className="text-[10px] font-mono text-slate-500 mt-0.5">
                    Trigger-based adaptation
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-obsidian-900 border border-slate-800/80">
                  <p className="text-[10px] font-mono uppercase text-accent-emerald font-semibold">
                    3. Fuzzy Workload Logic
                  </p>
                  <p className="text-xs text-slate-300 mt-1">
                    Mamdani inference:{' '}
                    <strong className="text-accent-emerald dark:text-emerald-300">Continuous Workload Scaling</strong>
                  </p>
                  <p className="text-[10px] font-mono text-slate-500 mt-0.5">
                    Fatigue & capacity membership
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ==================== ADAPTIVE REPLAN PREVIEW SECTION ==================== */}
        {replanPreview && (
          <section
            className="rounded-3xl border border-accent-violet/40 bg-obsidian-900/90 p-6 sm:p-8 space-y-6 shadow-2xl"
            aria-label="Adaptive replan preview"
          >
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-accent-violet/10 text-accent-violet text-[11px] font-mono font-semibold mb-1">
                  <Zap className="w-3.5 h-3.5" />
                  <span>Adaptive Replan Preview</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-bold text-white">
                  Revised Roadmap Proposal
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Review the expert system adjustments below. Confirm to apply and activate the revised plan.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={handleApplyReplan}
                  disabled={isApplyingReplan}
                  className="px-4 py-2 rounded-xl bg-accent-emerald hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-glow-emerald transition disabled:opacity-50"
                >
                  {isApplyingReplan ? 'Applying...' : 'Apply Schedule'}
                </button>
                <button
                  onClick={() => {
                    soundClick()
                    setReplanPreview(null)
                    setReplanMessage('Preview dismissed. Your current roadmap was kept unchanged.')
                  }}
                  disabled={isApplyingReplan}
                  className="px-3.5 py-2 rounded-xl border border-slate-700 hover:border-slate-500 text-slate-400 hover:text-white text-xs font-mono transition"
                >
                  Discard
                </button>
              </div>
            </div>

            {/* Stat comparison grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-2xl bg-obsidian-950 border border-slate-800">
                <p className="text-[10px] font-mono uppercase text-slate-500">Selected Strategy</p>
                <p className="text-sm font-bold text-cyan-400 mt-1">
                  {replanPreview.strategy || 'Not provided'}
                </p>
                <p className="text-[10px] text-slate-500 font-mono">Expert system</p>
              </div>

              <div className="p-3.5 rounded-2xl bg-obsidian-950 border border-slate-800">
                <p className="text-[10px] font-mono uppercase text-slate-500">Tasks to Replan</p>
                <p className="text-sm font-bold text-white mt-1">
                  {String(replanPreview.tasks_replanned ?? '—')}
                </p>
                <p className="text-[10px] text-slate-500 font-mono">Proposed tasks</p>
              </div>

              <div className="p-3.5 rounded-2xl bg-obsidian-950 border border-slate-800">
                <p className="text-[10px] font-mono uppercase text-slate-500">Proposed Completion</p>
                <p className="text-sm font-bold text-accent-emerald mt-1">
                  {formatDate(replanPreview.plan_end_date)}
                </p>
                <p className="text-[10px] text-slate-500 font-mono">Calculated end date</p>
              </div>

              <div className="p-3.5 rounded-2xl bg-obsidian-950 border border-slate-800">
                <p className="text-[10px] font-mono uppercase text-slate-500">Next Version</p>
                <p className="text-sm font-bold text-accent-violet mt-1">
                  Version {String(replanPreview.roadmap_version ?? '—')}
                </p>
                <p className="text-[10px] text-slate-500 font-mono">Proposed version</p>
              </div>
            </div>

            {/* Deadline Comparison */}
            {replanPreview.target_date && (
              <div className="p-4 rounded-2xl bg-obsidian-950 border border-slate-800 text-xs">
                <h4 className="font-bold text-slate-200">Deadline Comparison</h4>
                <div className="flex flex-wrap items-center gap-6 mt-2">
                  <p className="text-slate-400">
                    Current target: <strong className="text-slate-200">{formatDate(replanPreview.target_date.old)}</strong>
                  </p>
                  <p className="text-slate-400">
                    Proposed target: <strong className="text-slate-200">{formatDate(replanPreview.target_date.new)}</strong>
                  </p>
                </div>
              </div>
            )}

            {/* Warnings if any */}
            {replanPreview.warnings && replanPreview.warnings.length > 0 && (
              <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-800 dark:text-amber-200 space-y-1">
                <div className="flex items-center gap-2 font-bold text-amber-800 dark:text-amber-300">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Planning Heuristic Warnings</span>
                </div>
                <ul className="list-disc pl-5 space-y-0.5">
                  {replanPreview.warnings.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Proposed Daily Schedule */}
            {previewDays.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-bold text-sm text-white">Proposed Daily Schedule Preview</h4>
                <div className="space-y-3">
                  {previewDays.map((day, dIdx) => {
                    const dayNum = day.day ?? day.day_number ?? dIdx + 1
                    const tasks = day.tasks ?? []

                    return (
                      <div key={dayNum} className="p-4 rounded-2xl bg-obsidian-950 border border-slate-800">
                        <div className="flex items-center justify-between pb-2 border-b border-slate-800/60 text-xs font-mono">
                          <span className="font-bold text-slate-200">
                            Day {dayNum} {day.date ? `(${formatDate(day.date)})` : ''}
                          </span>
                          <span className="text-cyan-400">{day.total_minutes ?? 0} min</span>
                        </div>
                        <div className="mt-2 space-y-1.5">
                          {tasks.map((task, tIdx) => (
                            <div
                              key={tIdx}
                              className="flex items-center justify-between text-xs text-slate-300 p-2 rounded-lg bg-obsidian-900"
                            >
                              <span>{task.name || task.topic_name || `Topic ${task.topic_id}`}</span>
                              <span className="font-mono text-slate-500">
                                {task.minutes ?? task.planned_minutes} min
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Collapsible CI decisions */}
            <details className="p-4 rounded-2xl bg-obsidian-950 border border-slate-800 text-xs">
              <summary className="cursor-pointer font-mono font-semibold text-slate-300 flex items-center justify-between">
                <span>View Raw CI Decision Metadata</span>
                <ChevronDown className="w-3.5 h-3.5" />
              </summary>
              <pre className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-xl bg-obsidian-900 p-3 text-[11px] font-mono text-indigo-300">
                {JSON.stringify(replanPreview.ci ?? {}, null, 2)}
              </pre>
            </details>

            {/* Confirmation actions */}
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={handleApplyReplan}
                disabled={isApplyingReplan}
                className="px-6 py-2.5 rounded-xl bg-accent-emerald hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-glow-emerald transition disabled:opacity-50"
              >
                {isApplyingReplan ? 'Activating New Schedule...' : 'Confirm & Apply Revised Schedule'}
              </button>
              <button
                onClick={() => {
                  soundClick()
                  setReplanPreview(null)
                  setReplanMessage('Preview dismissed. Your current roadmap was kept unchanged.')
                }}
                disabled={isApplyingReplan}
                className="px-4 py-2.5 rounded-xl border border-slate-700 text-slate-400 hover:text-white text-xs font-mono transition"
              >
                Discard
              </button>
            </div>
          </section>
        )}
      </main>
    </>
  )
}

export default RoadmapPage
