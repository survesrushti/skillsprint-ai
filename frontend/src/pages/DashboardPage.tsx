import { useEffect, useState, useCallback } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Calendar,
  CheckCircle2,
  Clock3,
  Compass,
  ExternalLink,
  Flame,
  RefreshCw,
  Sparkles,
  Star,
  Play,
  Zap,
  Award,
  Target,
  ChevronRight,
  SlidersHorizontal,
} from 'lucide-react'
import Navbar from '../components/layout/Navbar'
import WeeklyReflectionModal from '../components/reflections/WeeklyReflectionModal'
import {
  completeTask,
  getActiveGoal,
  getActiveRoadmap,
  getProgressSummary,
  getTodayTasks,
  getWeeklyReflections,
  getWeeklyReflectionStatus,
  skipTask,
  swapTaskResource,
  type DailyTask,
  type GoalData,
  type ProgressSummaryResponse,
  type ReflectionStatusResponse,
  type RoadmapResponse,
  type TodayTasksResponse,
  type WeeklyReflectionData,
} from '../api/client'
import { soundClick, soundSuccess, soundAlert } from '../utils/sound'

const TRACK_NAMES: Record<number, string> = {
  1: 'Full Stack Development',
  2: 'Data Analytics',
  3: 'UI/UX Design',
}

function formatDate(value?: string) {
  if (!value) return 'Not set'
  const parsed = new Date(`${value.slice(0, 10)}T12:00:00`)
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function calculateDaysRemaining(targetDateStr?: string): number | null {
  if (!targetDateStr) return null
  const parsed = new Date(`${targetDateStr.slice(0, 10)}T12:00:00`)
  if (Number.isNaN(parsed.getTime())) return null
  const now = new Date()
  const diffTime = parsed.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays > 0 ? diffDays : 0
}

function DashboardPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [goal, setGoal] = useState<GoalData | null>(null)
  const [todayData, setTodayData] = useState<TodayTasksResponse | null>(null)
  const [progressData, setProgressData] = useState<ProgressSummaryResponse | null>(null)
  const [roadmapData, setRoadmapData] = useState<RoadmapResponse | null>(null)
  const [reflections, setReflections] = useState<WeeklyReflectionData[]>([])
  const [reflectionStatus, setReflectionStatus] = useState<ReflectionStatusResponse | null>(null)
  const [reflectionModalOpen, setReflectionModalOpen] = useState(false)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [taskActionId, setTaskActionId] = useState<number | null>(null)
  const [taskActionError, setTaskActionError] = useState('')
  const [swappingTaskId, setSwappingTaskId] = useState<number | null>(null)

  const loadDashboardData = useCallback(async (targetGoalId: number) => {
    try {
      const [todayRes, progressRes, roadmapRes, reflRes] = await Promise.all([
        getTodayTasks(targetGoalId),
        getProgressSummary(targetGoalId),
        getActiveRoadmap(targetGoalId),
        getWeeklyReflections(targetGoalId).catch(() => ({
          status: 'success',
          count: 0,
          reflections: [],
        })),
      ])

      setTodayData(todayRes)
      setProgressData(progressRes)
      setRoadmapData(roadmapRes)
      setReflections(reflRes.reflections || [])

      try {
        const statusRes = await getWeeklyReflectionStatus(
          targetGoalId,
          todayRes.current_day
        )
        setReflectionStatus(statusRes)
        if (statusRes.should_prompt) {
          setReflectionModalOpen(true)
        }
      } catch (statusErr) {
        console.warn('Weekly reflection status check error:', statusErr)
      }
    } catch (fetchErr) {
      console.warn('Dashboard secondary data load error:', fetchErr)
    }
  }, [])

  useEffect(() => {
    let isMounted = true

    async function initializeDashboard() {
      setLoading(true)
      setError('')

      try {
        const queryGoalId = searchParams.get('goal_id')
        const storedGoalId = localStorage.getItem('skillsprint_active_goal_id')

        let resolvedGoalId: number | null = null

        if (queryGoalId && !Number.isNaN(Number(queryGoalId))) {
          resolvedGoalId = Number(queryGoalId)
        } else if (storedGoalId && !Number.isNaN(Number(storedGoalId))) {
          resolvedGoalId = Number(storedGoalId)
        }

        let fetchedGoal: GoalData | null = null
        try {
          const activeGoalRes = await getActiveGoal()
          if (activeGoalRes && activeGoalRes.goal) {
            fetchedGoal = activeGoalRes.goal
            resolvedGoalId = fetchedGoal.id
            localStorage.setItem(
              'skillsprint_active_goal_id',
              String(fetchedGoal.id)
            )
          }
        } catch {
          // If no active goal endpoint match, fallback to resolved ID if any
        }

        if (!resolvedGoalId && !fetchedGoal) {
          if (isMounted) {
            setLoading(false)
          }
          return
        }

        const effectiveGoalId = resolvedGoalId || fetchedGoal!.id

        if (isMounted && fetchedGoal) {
          setGoal(fetchedGoal)
        }

        await loadDashboardData(effectiveGoalId)
      } catch (err) {
        if (isMounted) {
          setError(
            err instanceof Error
              ? err.message
              : 'Could not load your dashboard data.'
          )
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    initializeDashboard()

    return () => {
      isMounted = false
    }
  }, [searchParams, loadDashboardData])

  useEffect(() => {
    function handleDateChange() {
      const targetGoalId =
        goal?.id ||
        todayData?.goal_id ||
        Number(localStorage.getItem('skillsprint_active_goal_id'))
      if (targetGoalId && Number.isInteger(targetGoalId) && targetGoalId > 0) {
        loadDashboardData(targetGoalId)
      }
    }

    window.addEventListener('skillsprint_date_changed', handleDateChange)
    return () => {
      window.removeEventListener('skillsprint_date_changed', handleDateChange)
    }
  }, [goal?.id, todayData?.goal_id, loadDashboardData])

  async function handleTaskAction(
    taskId: number,
    action: 'complete' | 'skip'
  ) {
    const targetGoalId = goal?.id || todayData?.goal_id
    if (!targetGoalId) return

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

      await loadDashboardData(targetGoalId)
    } catch (actionErr) {
      soundAlert()
      setTaskActionError(
        actionErr instanceof Error
          ? actionErr.message
          : 'Could not update task.'
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
          : 'Could not swap resource.'
      )
    } finally {
      setSwappingTaskId(null)
    }
  }

  const effectiveGoalId = goal?.id || todayData?.goal_id
  const targetDateStr = goal?.target_date || roadmapData?.goal.target_date
  const daysRemaining = calculateDaysRemaining(targetDateStr)
  const completionPercentage = progressData?.summary.completion_percentage ?? 0

  return (
    <>
      <Navbar />

      <main className="min-h-screen text-slate-100">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          {/* ==================== LOADING STATE ==================== */}
          {loading && (
            <div className="glass-panel rounded-3xl p-12 text-center border border-slate-800 space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-violet/10 text-accent-violet text-xs font-mono">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Loading Dashboard</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
                Preparing your learning dashboard...
              </h2>
              <div className="mx-auto mt-6 h-2 max-w-md overflow-hidden rounded-full bg-obsidian-900 border border-slate-800">
                <div className="h-full w-2/3 animate-pulse rounded-full bg-gradient-to-r from-accent-violet to-cyan-400" />
              </div>
            </div>
          )}

          {/* ==================== ERROR STATE ==================== */}
          {!loading && error && (
            <div className="glass-panel rounded-3xl border border-rose-500/30 bg-rose-500/10 p-6 text-rose-800 dark:text-rose-200">
              <p className="font-semibold text-white">{error}</p>
              <button
                onClick={() => {
                  soundClick()
                  navigate('/tracks')
                }}
                className="mt-4 rounded-xl bg-accent-violet hover:bg-accent-violet/90 px-4 py-2 text-xs font-semibold text-white shadow-glow-violet transition"
              >
                View Available Tracks
              </button>
            </div>
          )}

          {/* ==================== EMPTY STATE ==================== */}
          {!loading && !error && !goal && !todayData && (
            <div className="glass-panel rounded-3xl border border-slate-800 p-10 text-center space-y-4">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-accent-violet/10 text-accent-violet border border-accent-violet/20">
                <Compass className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold text-white">
                No active learning goal found
              </h2>
              <p className="mx-auto max-w-md text-xs sm:text-sm leading-relaxed text-slate-400">
                Get started by choosing a curated learning track. SkillSprint AI will build a personalized
                adaptive roadmap tailored to your target completion date and daily study availability.
              </p>
              <div className="pt-2">
                <Link
                  to="/tracks"
                  onClick={() => soundClick()}
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-accent-violet to-indigo-600 hover:from-accent-violet/90 hover:to-indigo-500 px-6 py-3 font-semibold text-white text-xs shadow-glow-violet transition"
                >
                  <span>Explore Learning Tracks</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          )}

          {/* ==================== ACTIVE DASHBOARD CONTENT ==================== */}
          {!loading && (goal || todayData) && (
            <>
              {/* Top Overview Banner (Prototype Screen 3) */}
              <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
                <div className="space-y-2 z-10">
                  <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                    <span className="px-2.5 py-0.5 rounded bg-accent-violet/10 text-accent-violet border border-accent-violet/20 font-semibold">
                      {goal ? TRACK_NAMES[goal.track_id] || 'Curated Track' : 'Curated Track'}
                    </span>
                    <span>•</span>
                    <span className="text-slate-300">
                      {daysRemaining !== null
                        ? `${daysRemaining} Days to Target Deadline`
                        : `Target: ${formatDate(targetDateStr)}`}
                    </span>
                  </div>

                  <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                    Welcome back,{' '}
                    <span className="bg-gradient-to-r from-white via-indigo-100 to-accent-violet bg-clip-text text-transparent">
                      Learner.
                    </span>
                  </h1>

                  <p className="text-xs sm:text-sm text-slate-400 max-w-xl leading-relaxed">
                    Today's study sprint is ready. The Fuzzy Workload Engine and A* Optimizer have aligned your
                    session for maximum retention.
                  </p>
                </div>

                {/* Quick Action & Stats Pills */}
                <div className="flex flex-wrap items-center gap-3 z-10">
                  <div className="px-3.5 py-2 rounded-xl bg-obsidian-900 border border-slate-800 flex items-center gap-2.5">
                    <Flame className="w-4 h-4 text-amber-400" />
                    <div>
                      <p className="text-[10px] text-slate-500 font-mono uppercase">Current Streak</p>
                      <p className="text-xs font-bold font-mono text-slate-200">
                        {progressData?.streak.current_streak_days ?? 0} Days
                      </p>
                    </div>
                  </div>

                  <div className="px-3.5 py-2 rounded-xl bg-obsidian-900 border border-slate-800 flex items-center gap-2.5">
                    <Award className="w-4 h-4 text-accent-emerald" />
                    <div>
                      <p className="text-[10px] text-slate-500 font-mono uppercase">Completed Tasks</p>
                      <p className="text-xs font-bold font-mono text-slate-200">
                        {progressData?.summary.completed_tasks ?? 0} Topics
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      soundClick()
                      const el = document.getElementById('today-tasks-section')
                      if (el) el.scrollIntoView({ behavior: 'smooth' })
                    }}
                    className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-accent-violet to-indigo-600 hover:from-accent-violet/90 hover:to-indigo-500 text-white text-xs font-semibold shadow-glow-violet transition flex items-center gap-1.5"
                  >
                    <Play className="w-3.5 h-3.5 fill-white" />
                    <span>Start Today's Sprint</span>
                  </button>

                  <button
                    onClick={() => {
                      soundClick()
                      if (effectiveGoalId) loadDashboardData(effectiveGoalId)
                    }}
                    className="p-2 rounded-xl bg-obsidian-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white transition"
                    title="Refresh dashboard metrics"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Quick Metrics 4-Grid */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="glass-card rounded-2xl p-5 border border-slate-800">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold font-mono uppercase tracking-wider text-slate-400">
                      Study Streak
                    </p>
                    <Flame className="w-5 h-5 text-amber-400" />
                  </div>
                  <p className="mt-3 text-2xl sm:text-3xl font-extrabold text-white">
                    {progressData?.streak.current_streak_days ?? 0}{' '}
                    <span className="text-xs font-normal text-slate-400 font-mono">days</span>
                  </p>
                  <p className="mt-1 text-[10px] text-slate-500 font-mono">
                    Consecutive daily study sessions
                  </p>
                </div>

                <div className="glass-card rounded-2xl p-5 border border-slate-800">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold font-mono uppercase tracking-wider text-slate-400">
                      Roadmap Completion
                    </p>
                    <CheckCircle2 className="w-5 h-5 text-accent-emerald" />
                  </div>
                  <p className="mt-3 text-2xl sm:text-3xl font-extrabold font-mono text-cyan-400">
                    {completionPercentage}%
                  </p>
                  <div className="mt-2 h-2 overflow-hidden rounded-full bg-obsidian-900 border border-slate-800">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-accent-violet to-cyan-400 transition-all duration-500"
                      style={{
                        width: `${Math.min(100, completionPercentage)}%`,
                      }}
                    />
                  </div>
                  <p className="mt-2 text-[10px] text-slate-500 font-mono">
                    {progressData?.summary.completed_tasks ?? 0} of{' '}
                    {progressData?.summary.total_tasks ?? 0} topics completed
                  </p>
                </div>

                <div className="glass-card rounded-2xl p-5 border border-slate-800">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold font-mono uppercase tracking-wider text-slate-400">
                      Today's Study Time
                    </p>
                    <Clock3 className="w-5 h-5 text-accent-violet" />
                  </div>
                  <p className="mt-3 text-2xl sm:text-3xl font-extrabold font-mono text-white">
                    {todayData?.summary.completed_minutes_today ?? 0}
                    <span className="text-xs font-normal text-slate-400 font-mono">
                      {' '}/ {todayData?.summary.planned_minutes_today ?? 0} min
                    </span>
                  </p>
                  <p className="mt-1 text-[10px] text-slate-500 font-mono">
                    {todayData?.summary.tasks_completed ?? 0} of{' '}
                    {todayData?.summary.tasks_total ?? 0} tasks completed today
                  </p>
                </div>

                <div className="glass-card rounded-2xl p-5 border border-slate-800">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold font-mono uppercase tracking-wider text-slate-400">
                      Target Date
                    </p>
                    <Calendar className="w-5 h-5 text-cyan-400" />
                  </div>
                  <p className="mt-3 text-lg sm:text-xl font-bold font-mono text-white">
                    {formatDate(targetDateStr)}
                  </p>
                  <p className="mt-1 text-[10px] text-slate-500 font-mono">
                    Day {todayData?.current_day ?? 1} of {todayData?.total_days ?? 1} total days
                  </p>
                </div>
              </div>

              {/* Schedule Status Notice */}
              {progressData && (
                <div
                  className={`flex items-center justify-between rounded-2xl border px-6 py-4 ${
                    progressData.progress.progress_difference >= 0
                      ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-800 dark:text-emerald-300'
                      : 'border-amber-500/20 bg-amber-500/5 text-amber-950 dark:text-amber-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {progressData.progress.progress_difference < 0 ? (
                      <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
                    ) : (
                      <CheckCircle2 className="w-5 h-5 text-accent-emerald shrink-0" />
                    )}
                    <div>
                      <p
                        className={`text-xs sm:text-sm font-semibold font-mono ${
                          progressData.progress.progress_difference >= 0
                            ? 'text-emerald-800 dark:text-emerald-200'
                            : 'text-amber-950 dark:text-amber-200'
                        }`}
                      >
                        {progressData.progress.progress_difference >= 0
                          ? 'You are currently on schedule!'
                          : 'You are slightly behind schedule.'}
                      </p>
                      <p
                        className={`mt-0.5 text-xs ${
                          progressData.progress.progress_difference >= 0
                            ? 'text-emerald-700 dark:text-emerald-300/80'
                            : 'text-amber-900 dark:text-amber-200/80'
                        }`}
                      >
                        {progressData.progress.progress_difference >= 0
                          ? 'Keep up the good consistency to hit your target date.'
                          : 'Use SkillSprint AI Adaptive Rescheduling to rebalance your study plan.'}
                      </p>
                    </div>
                  </div>

                  <Link
                    to={`/roadmap?goal_id=${effectiveGoalId}`}
                    onClick={() => soundClick()}
                    className="shrink-0 rounded-xl bg-obsidian-900 border border-slate-800 hover:border-slate-700 px-3.5 py-2 text-xs font-mono font-semibold transition"
                  >
                    View Plan &rarr;
                  </Link>
                </div>
              )}

              {/* Action Error Banner */}
              {taskActionError && (
                <div
                  role="alert"
                  className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs text-rose-800 dark:text-rose-200"
                >
                  {taskActionError}
                </div>
              )}

              {/* Computational Intelligence Status Card (Prototype) */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glass-card rounded-2xl p-5 border border-slate-800">
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 pb-2 border-b border-slate-800">
                    <span className="flex items-center gap-1.5 text-accent-violet font-semibold">
                      <Zap className="w-3.5 h-3.5" />
                      A* Search Path
                    </span>
                    <span className="text-accent-emerald font-bold">Optimal</span>
                  </div>
                  <p className="text-xs text-slate-300 mt-3">
                    Nodes explored:{' '}
                    <strong className="text-white">
                      {roadmapData?.ci.search.nodes_expanded ?? '—'}
                    </strong>
                  </p>
                  <p className="text-[10px] text-slate-500 font-mono mt-1">
                    Admissible unit-aligned heuristic
                  </p>
                </div>

                <div className="glass-card rounded-2xl p-5 border border-slate-800">
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 pb-2 border-b border-slate-800">
                    <span className="flex items-center gap-1.5 text-cyan-400 font-semibold">
                      <SlidersHorizontal className="w-3.5 h-3.5" />
                      Fuzzy Workload
                    </span>
                    <span className="text-accent-cyan font-bold">Active</span>
                  </div>
                  <p className="text-xs text-slate-300 mt-3">
                    Adaptive adjustment:{' '}
                    <strong className="text-accent-cyan">Continuous Workload Scaling</strong>
                  </p>
                  <p className="text-[10px] text-slate-500 font-mono mt-1">
                    Fatigue & capacity membership
                  </p>
                </div>

                <div className="glass-card rounded-2xl p-5 border border-slate-800">
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 pb-2 border-b border-slate-800">
                    <span className="flex items-center gap-1.5 text-accent-emerald font-semibold">
                      <Target className="w-3.5 h-3.5" />
                      Expert Rescheduler
                    </span>
                    <span className="text-slate-300 font-mono font-bold">
                      {String(
                        (roadmapData?.ci.expert as { selected_strategy?: string })?.selected_strategy ||
                          'STANDBY'
                      )}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-3">
                    Trigger:{' '}
                    <strong className="text-slate-200">
                      {todayData && todayData.summary.overdue_count > 0 ? 'Overdue Tasks Detected' : 'All Tasks On Track'}
                    </strong>
                  </p>
                  <p className="text-[10px] text-slate-500 font-mono mt-1">
                    Buffer rebalance ready
                  </p>
                </div>
              </div>

              {/* ==================== TODAY'S TASKS FOCUS ==================== */}
              <section
                id="today-tasks-section"
                className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                  <div>
                    <p className="text-xs font-semibold uppercase font-mono tracking-wider text-cyan-400">
                      Daily Focus
                    </p>
                    <h2 className="mt-1 text-xl sm:text-2xl font-bold text-white">
                      Today's Learning Tasks
                    </h2>
                    <p className="mt-0.5 text-xs text-slate-400">
                      {todayData
                        ? `Day ${todayData.current_day} of ${todayData.total_days} · ${todayData.date}`
                        : 'Loading daily tasks...'}
                    </p>
                  </div>

                  {todayData && (
                    <div className="rounded-xl border border-slate-800 bg-obsidian-900 px-3.5 py-2 text-xs font-mono text-slate-300">
                      {todayData.summary.tasks_completed} / {todayData.summary.tasks_total} completed today
                    </div>
                  )}
                </div>

                {todayData && todayData.tasks.length === 0 && (
                  <div className="rounded-2xl border border-slate-800 bg-obsidian-900 p-6 text-center text-xs font-mono text-slate-400">
                    <p>No study tasks scheduled for today.</p>
                    <p className="mt-1 text-[11px] text-slate-500">
                      Take time to review or explore upcoming topics on your roadmap.
                    </p>
                  </div>
                )}

                <div className="space-y-3">
                  {todayData?.tasks.map((task: DailyTask) => {
                    const isPending = task.status === 'pending'
                    const isBusy = taskActionId === task.id

                    return (
                      <div
                        key={task.id}
                        className="glass-card rounded-2xl p-4 sm:p-5 border border-slate-800 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4"
                      >
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-bold text-white">
                              {task.topic_name}
                            </p>
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

                          {/* Recommended Resource with Clickable Link */}
                          {task.resource && (
                            <div className="flex flex-wrap items-center gap-2 pt-0.5">
                              <a
                                href={task.resource.url}
                                target="_blank"
                                rel="noreferrer noopener"
                                className="inline-flex items-center gap-1.5 rounded-lg border border-accent-violet/30 bg-accent-violet/10 px-2.5 py-1 text-xs font-mono text-accent-violet hover:bg-accent-violet/20 hover:text-white transition"
                              >
                                <BookOpen className="w-3.5 h-3.5" />
                                <span>{task.resource.title}</span>
                                <ExternalLink className="w-3 h-3 opacity-70" />
                              </a>
                              <span className="rounded-full border border-slate-800 bg-obsidian-900 px-2.5 py-0.5 text-[10px] font-mono capitalize text-slate-400">
                                {task.resource.resource_type}
                              </span>
                            </div>
                          )}

                          {/* Resource Swapping Dropdown */}
                          {task.available_resources && task.available_resources.length > 1 && (
                            <div className="flex items-center gap-2 text-xs">
                              <span className="text-slate-500 text-[11px] font-mono">
                                Change resource:
                              </span>
                              <select
                                id={`swap-dash-${task.id}`}
                                disabled={swappingTaskId === task.id || isBusy}
                                value={task.resource?.id ?? ''}
                                onChange={(e) =>
                                  handleSwapResource(task.id, Number(e.target.value))
                                }
                                className="bg-obsidian-900 border border-slate-800 rounded-lg px-2 py-1 text-xs text-slate-300 focus:outline-none focus:border-accent-violet disabled:opacity-50"
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

                        <div className="flex items-center gap-2 shrink-0 pt-1">
                          <button
                            disabled={!isPending || isBusy}
                            onClick={() => handleTaskAction(task.id, 'complete')}
                            className="px-3.5 py-2 rounded-xl bg-accent-emerald hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-glow-emerald transition disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
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
                      Head to the Roadmap page to preview an adaptive replan!
                    </div>
                  </div>
                )}
              </section>

              {/* Simulator & Reflection Quick Navigation */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Link
                  to={`/roadmap?goal_id=${effectiveGoalId}`}
                  onClick={() => soundClick()}
                  className="glass-card rounded-2xl p-5 border border-slate-800 flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-accent-amber/10 text-accent-amber group-hover:scale-110 transition">
                      <Zap className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white group-hover:text-accent-amber transition">
                        Did you miss a study session?
                      </h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Test the Expert System's automatic re-balancing preview.
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-500 group-hover:translate-x-1 group-hover:text-white transition" />
                </Link>

                <button
                  type="button"
                  onClick={() => {
                    soundClick()
                    setReflectionModalOpen(true)
                  }}
                  className="glass-card rounded-2xl p-5 border border-slate-800 text-left flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-pink-500/10 text-pink-400 group-hover:scale-110 transition">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white group-hover:text-pink-300 transition">
                        Weekly Study Reflection
                      </h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Calibrate Fuzzy Logic with your confidence and habit ratings.
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-500 group-hover:translate-x-1 group-hover:text-white transition" />
                </button>
              </div>

              {/* Weekly Reflections History Section */}
              <section className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                  <div>
                    <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase font-mono tracking-wider text-accent-violet">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Subjective Growth Tracking</span>
                    </div>
                    <h2 className="mt-1 text-xl font-bold text-white">Weekly Reflections</h2>
                    <p className="mt-0.5 text-xs text-slate-400">
                      Personal reflections captured every 7th day of study to evaluate confidence, pacing, and study habits.
                    </p>
                  </div>

                  <button
                    onClick={() => {
                      soundClick()
                      setReflectionModalOpen(true)
                    }}
                    className="inline-flex items-center gap-1.5 self-start rounded-xl border border-slate-700 bg-obsidian-900 px-3.5 py-2 text-xs font-mono font-semibold text-slate-300 transition hover:border-accent-violet hover:text-accent-violet sm:self-auto"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>
                      {reflectionStatus?.submitted ? 'Update This Week' : 'Record Reflection'}
                    </span>
                  </button>
                </div>

                {reflections.length === 0 ? (
                  <div className="rounded-2xl border border-slate-800 bg-obsidian-900 p-6 text-center text-xs font-mono text-slate-400">
                    <p className="font-semibold text-slate-300">No reflections submitted yet</p>
                    <p className="mt-1 text-[11px] text-slate-500">
                      On every 7th day of study (e.g., Day 7, Day 14), you will be prompted to record your confidence level and study observations.
                    </p>
                  </div>
                ) : (
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {reflections.map((refl) => (
                      <div
                        key={refl.id}
                        className="glass-card flex flex-col justify-between rounded-2xl border border-slate-800 p-5 space-y-3"
                      >
                        <div>
                          <div className="flex items-center justify-between">
                            <span className="rounded-full bg-accent-violet/10 border border-accent-violet/20 px-2.5 py-0.5 text-[10px] font-mono font-bold text-accent-violet">
                              Week {refl.week_number} • Day {refl.study_day}
                            </span>
                            {refl.created_at && (
                              <span className="text-[10px] font-mono text-slate-500">
                                {formatDate(refl.created_at)}
                              </span>
                            )}
                          </div>

                          <div className="mt-3 flex items-center gap-1.5">
                            <span className="text-xs font-semibold text-slate-400">
                              Confidence:
                            </span>
                            <div className="flex items-center text-amber-400">
                              {[1, 2, 3, 4, 5].map((s) => (
                                <Star
                                  key={s}
                                  size={13}
                                  className={
                                    s <= refl.confidence_level
                                      ? 'fill-amber-400 text-amber-400'
                                      : 'text-slate-700'
                                  }
                                />
                              ))}
                            </div>
                            <span className="text-xs font-bold font-mono text-slate-300">
                              ({refl.confidence_level}/5)
                            </span>
                          </div>

                          <div className="mt-2 flex items-center gap-2 text-xs text-slate-400">
                            <span className="font-semibold">Difficulty:</span>
                            <span className="font-medium text-slate-300">
                              {refl.difficulty_rating === 1
                                ? 'Too Easy'
                                : refl.difficulty_rating === 2
                                  ? 'Comfortable'
                                  : refl.difficulty_rating === 3
                                    ? 'Balanced'
                                    : refl.difficulty_rating === 4
                                      ? 'Challenging'
                                      : 'Overwhelming'}{' '}
                              ({refl.difficulty_rating}/5)
                            </span>
                          </div>

                          {refl.notes && (
                            <p className="mt-3 rounded-xl bg-obsidian-900/80 border border-slate-800 p-3 text-xs italic leading-relaxed text-slate-300">
                              "{refl.notes}"
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </>
          )}

          {goal && todayData && (
            <WeeklyReflectionModal
              isOpen={reflectionModalOpen}
              goalId={goal.id}
              weekNumber={Math.max(1, Math.floor((todayData.current_day + 6) / 7))}
              studyDay={todayData.current_day}
              onClose={() => setReflectionModalOpen(false)}
              onSuccess={(newRefl) => {
                setReflections((prev) => [
                  newRefl,
                  ...prev.filter((r) => r.id !== newRefl.id),
                ])
                setReflectionStatus((prev) =>
                  prev
                    ? {
                        ...prev,
                        should_prompt: false,
                        submitted: true,
                        reflection: newRefl,
                      }
                    : null
                )
              }}
            />
          )}
        </div>
      </main>
    </>
  )
}

export default DashboardPage
