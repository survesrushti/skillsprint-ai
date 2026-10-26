import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import {
  Zap,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  Flame,
  Check,
  Cpu,
  Layers,
} from 'lucide-react'
import Navbar from '../components/layout/Navbar'
import {
  getActiveGoal,
  getActiveRoadmap,
  rescheduleRoadmap,
  getProgressSummary,
  type GoalData,
  type RoadmapDay,
  type RescheduleResponse,
  type ProgressSummaryResponse,
} from '../api/client'
import { soundClick, soundSuccess, soundAlert } from '../utils/sound'

export default function ReplanningPage() {
  const [searchParams] = useSearchParams()
  const goalIdParam = searchParams.get('goal_id')

  const [goal, setGoal] = useState<GoalData | null>(null)
  const [activeDays, setActiveDays] = useState<RoadmapDay[]>([])
  const [progressSummary, setProgressSummary] = useState<ProgressSummaryResponse | null>(null)
  const [previewData, setPreviewData] = useState<RescheduleResponse | null>(null)

  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isSimulating, setIsSimulating] = useState<boolean>(false)
  const [isApplying, setIsApplying] = useState<boolean>(false)
  const [applySuccessMessage, setApplySuccessMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refreshIndex, setRefreshIndex] = useState<number>(0)

  useEffect(() => {
    let isMounted = true

    async function fetchData() {
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

        const [roadmapRes, progressRes] = await Promise.all([
          getActiveRoadmap(activeGoalId),
          getProgressSummary(activeGoalId),
        ])

        if (isMounted) {
          setActiveDays(roadmapRes.roadmap || [])
          setProgressSummary(progressRes)
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load replanning data.')
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void fetchData()

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


  // Trigger Missed Session Simulation (Preview Mode)
  async function handleSimulateMissedSession() {
    if (!goal) return
    soundClick()
    setIsSimulating(true)
    setError(null)
    setApplySuccessMessage(null)

    try {
      // Preview call invokes real Rescheduler() (Fuzzy -> Expert System -> A* search)
      const res = await rescheduleRoadmap(goal.id, { preview: true, force: true })
      setPreviewData(res)
      soundAlert()
    } catch (err) {
      soundAlert()
      setError(err instanceof Error ? err.message : 'Reschedule simulation failed.')
    } finally {
      setIsSimulating(false)
    }
  }

  // Apply Revised Schedule (Save to DB)
  async function handleApplySchedule() {
    if (!goal) return
    soundClick()
    setIsApplying(true)
    setError(null)

    try {
      const res = await rescheduleRoadmap(goal.id, { preview: false, force: true })
      soundSuccess()
      setApplySuccessMessage(
        res.message || 'Adaptive roadmap rebalanced and committed to MySQL database successfully!'
      )
      setPreviewData(null)
      // Reload active data
      setRefreshIndex((prev) => prev + 1)
    } catch (err) {
      soundAlert()
      setError(err instanceof Error ? err.message : 'Could not apply schedule.')
    } finally {
      setIsApplying(false)
    }
  }

  function handleResetSimulation() {
    soundClick()
    setPreviewData(null)
    setApplySuccessMessage(null)
    setError(null)
  }

  // Determine current effective roadmap to display (either preview or active)
  const currentDaysList: RoadmapDay[] = previewData?.roadmap && previewData.roadmap.length > 0
    ? previewData.roadmap
    : activeDays

  // 7-Day Window: Slice the first 7 days (or rolling 7 days)
  const sevenDayWindow = currentDaysList.slice(0, 7)

  // Helper to determine day status and styling
  const currentDayIndex = progressSummary?.current_day || 1

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 px-4 sm:px-6 lg:px-8 py-8 max-w-7xl mx-auto w-full space-y-6">
        {/* Top Header & Simulation Controls */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-accent-amber/10 text-accent-amber border border-accent-amber/20 text-xs font-mono font-semibold mb-2">
              <Zap className="w-3.5 h-3.5 text-accent-amber" />
              <span>Core Synopsis Demonstration • Section 6</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              Expert System Adaptive Rescheduler
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
              Simulate what happens when you miss study sessions or fall behind. Watch the rule engine rebalance the roadmap without breaking your target date.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={handleSimulateMissedSession}
              disabled={isSimulating || isLoading || !goal}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-accent-amber to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/10 transition flex items-center gap-2 disabled:opacity-50"
            >
              <AlertTriangle className="w-4 h-4 text-slate-950" />
              <span>{isSimulating ? 'Simulating Rule Engine...' : 'Simulate: "I Missed Yesterday"'}</span>
            </button>

            {previewData && (
              <button
                onClick={handleApplySchedule}
                disabled={isApplying}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-semibold text-xs shadow-glow-emerald transition flex items-center gap-1.5 disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                <span>{isApplying ? 'Applying...' : 'Apply Revised Schedule'}</span>
              </button>
            )}

            <button
              onClick={handleResetSimulation}
              disabled={isLoading}
              className="px-3.5 py-2.5 rounded-xl bg-obsidian-900 border border-white/10 hover:bg-white/5 text-slate-300 text-xs font-medium transition flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset View</span>
            </button>
          </div>
        </div>

        {/* Success Alert */}
        {applySuccessMessage && (
          <div className="p-4 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 text-xs font-mono text-emerald-800 dark:text-emerald-200 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{applySuccessMessage}</span>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-2xl border border-rose-500/30 bg-rose-500/10 text-xs font-mono text-rose-800 dark:text-rose-300 flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={() => setRefreshIndex((prev) => prev + 1)}
              className="px-3 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-800 dark:text-rose-200 font-semibold"
            >
              Retry
            </button>
          </div>
        )}

        {/* 7-Day Reschedule Calendar Visualizer */}
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-white/10">
            <div>
              <h2 className="font-bold text-white text-base">7-Day Study Matrix & Live Rebalancing</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Visualizing task sequencing, capacity allocation, and buffer days across the weekly study cycle
              </p>
            </div>

            <div className="flex items-center gap-2">
              {previewData ? (
                <span className="text-xs font-mono text-accent-amber bg-accent-amber/10 px-3 py-1 rounded-full border border-accent-amber/20 font-bold flex items-center gap-1.5 animate-pulse">
                  <Sparkles className="w-3.5 h-3.5 text-accent-amber" />
                  <span>Simulation Active: Schedule Reallocated</span>
                </span>
              ) : (
                <span className="text-xs font-mono text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded-full border border-emerald-400/20 font-bold flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>All Sessions on Track</span>
                </span>
              )}
            </div>
          </div>

          {/* 7-Day Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
            {sevenDayWindow.length > 0 ? (
              sevenDayWindow.map((dayItem, index) => {
                const dayNum = dayItem.day || index + 1
                const isPast = dayNum < currentDayIndex
                const isToday = dayNum === currentDayIndex
                const isSimulatedMissed = previewData && dayNum === currentDayIndex - 1 && isPast
                const isBufferDay = dayNum % 6 === 0 || dayNum % 7 === 0 || dayItem.tasks.length === 0

                const totalMinutes = dayItem.total_minutes || dayItem.tasks.reduce((acc, t) => acc + (t.minutes || 0), 0)
                const firstTask = dayItem.tasks[0]

                return (
                  <div
                    key={dayNum}
                    className={`p-4 rounded-2xl border transition-all duration-300 space-y-2.5 ${
                      isSimulatedMissed
                        ? 'bg-rose-500/15 border-rose-500/60 shadow-lg shadow-rose-500/10 scale-[1.02]'
                        : isToday
                        ? 'bg-accent-violet/15 border-accent-violet shadow-glow-violet'
                        : previewData && !isPast && !isBufferDay
                        ? 'bg-accent-amber/10 border-accent-amber/40'
                        : isBufferDay
                        ? 'bg-obsidian-900/40 border-dashed border-white/10'
                        : 'bg-obsidian-900/80 border-white/10'
                    }`}
                  >
                    {/* Day Header */}
                    <div className="flex justify-between items-center text-[10px] font-mono">
                      <span className={isToday ? 'text-accent-violet font-bold' : 'text-slate-400'}>
                        {isToday ? `DAY ${dayNum} (TODAY)` : `DAY ${dayNum}`}
                      </span>

                      {isSimulatedMissed ? (
                        <span className="text-rose-400 font-bold px-1.5 py-0.5 rounded bg-rose-500/20 border border-rose-500/30">
                          MISSED
                        </span>
                      ) : isPast ? (
                        <span className="text-emerald-400 font-bold">DONE</span>
                      ) : isToday ? (
                        <span className="text-cyan-400 font-bold">ACTIVE</span>
                      ) : isBufferDay ? (
                        <span className="text-slate-500">BUFFER</span>
                      ) : (
                        <span className="text-slate-400">QUEUED</span>
                      )}
                    </div>

                    {/* Topic Title */}
                    <div className="min-h-[44px]">
                      {firstTask ? (
                        <p className="text-xs font-bold text-slate-200 line-clamp-2 leading-tight">
                          {firstTask.name}
                        </p>
                      ) : (
                        <p className="text-xs font-medium text-slate-500 italic mt-1">
                          Buffer / Catchup Slot
                        </p>
                      )}
                    </div>

                    {/* Load & Status Meta */}
                    <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[10px] font-mono">
                      <span className="text-slate-400">
                        {totalMinutes > 0 ? `${(totalMinutes / 60).toFixed(1)} hrs` : '0 hrs'}
                      </span>
                      <span
                        className={
                          isSimulatedMissed
                            ? 'text-rose-400'
                            : isToday
                            ? 'text-indigo-300'
                            : 'text-slate-500'
                        }
                      >
                        {isSimulatedMissed
                          ? 'Zero Logged'
                          : isBufferDay
                          ? 'Flexible'
                          : 'Standard'}
                      </span>
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="col-span-7 py-8 text-center text-xs font-mono text-slate-500">
                No roadmap items found to construct the 7-day visualizer.
              </div>
            )}
          </div>

          {/* Simulation Feedback Explanation Box */}
          {previewData && (
            <div className="p-5 rounded-2xl bg-accent-amber/10 border border-accent-amber/30 text-xs text-slate-200 space-y-3 animate-fade-in">
              <div className="flex items-center gap-2 text-accent-amber font-bold text-sm">
                <Sparkles className="w-4 h-4 text-accent-amber" />
                <span>
                  Expert System Strategy Fired: [{previewData.strategy || 'COLLISION RESOLUTION COMPLETE'}]
                </span>
              </div>

              <div className="font-mono text-slate-300 text-xs leading-relaxed space-y-2">
                <p>
                  <strong>Rule Engine Rationale:</strong> Learner simulated missing Day {currentDayIndex - 1}. Rather than doubling study capacity on subsequent days (which is prohibited by the <strong>Fuzzy Fatigue Guardrail</strong> to avoid cognitive burnout), the Expert System reallocated pending tasks across designated buffer slots.
                </p>

                {previewData.target_date && (
                  <div className="flex flex-wrap items-center gap-4 pt-2 text-[11px] border-t border-accent-amber/20">
                    <span>
                      Original Target Date: <strong className="text-white">{previewData.target_date.old}</strong>
                    </span>
                    <span>
                      Revised Target Date:{' '}
                      <strong className={previewData.target_date.changed ? 'text-accent-amber' : 'text-emerald-400'}>
                        {previewData.target_date.new}
                      </strong>
                    </span>
                    <span className="text-emerald-400 font-bold">
                      {previewData.target_date.changed
                        ? 'Target date extended to preserve manageable daily load'
                        : 'Target completion date preserved without deadline drift!'}
                    </span>
                  </div>
                )}

                {previewData.warnings && previewData.warnings.length > 0 && (
                  <div className="text-amber-800 dark:text-amber-200 pt-1">
                    {previewData.warnings.map((w, idx) => (
                      <p key={idx}>• {w}</p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* 2-Column Section: Telemetry Diagnostics & Rete Rule Pattern Matcher */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Computational Intelligence Telemetry (1 Col) */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>Live Rescheduler Telemetry</span>
              </h3>
              <span className="text-[10px] font-mono text-slate-500">Real Backend Output</span>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div className="flex items-center justify-between p-3 rounded-xl bg-obsidian-950/70 border border-white/5">
                <span className="text-slate-400">Selected Strategy:</span>
                <span className="text-accent-amber font-bold">
                  {previewData?.strategy || 'STANDARD_PACING'}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-obsidian-950/70 border border-white/5">
                <span className="text-slate-400">Progress Ratio:</span>
                <span className="text-emerald-400 font-bold">
                  {previewData?.metrics?.progress_ratio ?? progressSummary?.progress.progress_difference ?? '1.0'}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-obsidian-950/70 border border-white/5">
                <span className="text-slate-400">Study Consistency Streak:</span>
                <span className="text-accent-amber font-bold flex items-center gap-1">
                  <Flame className="w-3.5 h-3.5 fill-current" />
                  {progressSummary?.streak.current_streak_days ?? 1} Days
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-obsidian-950/70 border border-white/5">
                <span className="text-slate-400">Daily Quota Guardrail:</span>
                <span className="text-cyan-400 font-bold">
                  {goal ? `${goal.study_hours_per_day}h / day` : '2.0h / day'}
                </span>
              </div>
            </div>
          </div>

          {/* Right: Expert System Rationale Stream (Rete Pattern Matcher) (2 Cols) */}
          <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div>
                <h3 className="font-bold text-white text-sm flex items-center gap-2">
                  <Layers className="w-4 h-4 text-accent-violet" />
                  <span>Expert System Rule Base (Condition-Action Pairs)</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Formal computational logic governing the adaptive schedule rebalancing
                </p>
              </div>
              <span className="text-[10px] font-mono text-slate-500">MSc CI Architecture</span>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3.5 rounded-xl bg-obsidian-950/70 border border-white/5 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-accent-amber font-bold">RULE #01 (Fatigue Guardrail):</span>
                </div>
                <p className="text-slate-300">
                  <span className="text-slate-500">IF</span> (MissedSession == TRUE) AND (DailyCapacity == 2.0h) <br />
                  <span className="text-slate-500">THEN</span> Prohibit doubling next day quota. Forward-chaining inference prevents cognitive fatigue.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-obsidian-950/70 border border-white/5 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-cyan-400 font-bold">RULE #02 (Buffer Slot Absorption):</span>
                </div>
                <p className="text-slate-300">
                  <span className="text-slate-500">IF</span> (BufferDaysAvailable &gt; 0) <br />
                  <span className="text-slate-500">THEN</span> Shift pending leaf milestones to weekend buffer slot without shifting target completion date.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-obsidian-950/70 border border-white/5 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-emerald-400 font-bold">RULE #03 (Admissible Target Preservation):</span>
                </div>
                <p className="text-slate-300">
                  <span className="text-slate-500">IF</span> (TargetDate - CurrentDate &gt; RemainingHours / Capacity) <br />
                  <span className="text-slate-500">THEN</span> Preserve final milestone and maintain topological prerequisite order ($h(n) \le h^*(n)$).
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Back Link to Roadmap */}
        <div className="pt-2 flex items-center justify-between text-xs text-slate-400">
          <Link
            to="/roadmap"
            onClick={() => soundClick()}
            className="hover:text-white transition flex items-center gap-1.5"
          >
            <span>← Back to Visual Roadmap Timeline</span>
          </Link>

          <Link
            to="/workspace"
            onClick={() => soundClick()}
            className="hover:text-white transition flex items-center gap-1.5 text-accent-violet font-semibold"
          >
            <span>Proceed to Focus Workspace</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </main>
    </div>
  )
}
