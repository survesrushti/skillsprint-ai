import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import TracksPage from './pages/TracksPage'
import TrackDetailPage from './pages/TrackDetailPage'
import OnboardingPage from './pages/OnboardingPage'

type RoadmapTask = {
  topic_id: number
  name: string
  minutes: number
  difficulty: number
  is_optional: boolean
}

type RoadmapDay = {
  day: number
  total_minutes: number
  tasks: RoadmapTask[]
}

type RoadmapResponse = {
  status: string
  message: string
  goal: {
    id: number
    track_id: number
    skill_level: string
    study_hours_per_day: number
    target_date: string
    known_topics: string[]
  }
  ci: {
    fuzzy: unknown
    expert: unknown
    search: {
      success: boolean
      sequence: number[]
      total_minutes: number
      daily_capacity: number
      total_days: number
      search_cost: number
      nodes_expanded: number
    }
  }
  roadmap: RoadmapDay[]
}

function RoadmapPage() {
  const location = useLocation()
  const navigate = useNavigate()

  const [roadmapData, setRoadmapData] =
    useState<RoadmapResponse | null>(null)

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const goalId = location.state?.goalId

    if (!goalId) {
      setError('No learning goal was found. Please create your goal again.')
      setIsLoading(false)
      return
    }

    const generateRoadmap = async () => {
      try {
        const response = await fetch(
          'http://127.0.0.1:5000/api/v1/roadmap/generate',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              goal_id: goalId,
            }),
          }
        )

        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            data.message || 'Could not generate your roadmap.'
          )
        }

        setRoadmapData(data)
      } catch (roadmapError) {
        console.error('Roadmap generation error:', roadmapError)

        setError(
          roadmapError instanceof Error
            ? roadmapError.message
            : 'Could not generate your roadmap.'
        )
      } finally {
        setIsLoading(false)
      }
    }

    generateRoadmap()
  }, [location.state])

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-20 text-white">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-400">
            SkillSprint AI
          </p>

          <h1 className="mt-4 text-4xl font-bold">
            Generating your roadmap...
          </h1>

          <p className="mt-4 text-slate-400">
            SkillSprint AI is analyzing your goal and creating an
            adaptive learning plan.
          </p>

          <div className="mt-10 h-2 overflow-hidden rounded-full bg-slate-800">
            <div className="h-full w-1/2 animate-pulse rounded-full bg-cyan-400" />
          </div>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-20 text-white">
        <div className="mx-auto max-w-3xl">
          <div className="rounded-3xl border border-red-400/30 bg-red-400/10 p-8">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-red-300">
              Roadmap Error
            </p>

            <h1 className="mt-3 text-3xl font-bold">
              We could not generate your roadmap
            </h1>

            <p className="mt-4 text-red-200">
              {error}
            </p>

            <button
              onClick={() => navigate('/tracks')}
              className="mt-6 rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 hover:bg-cyan-300"
            >
              Create Goal Again
            </button>
          </div>
        </div>
      </main>
    )
  }

  if (!roadmapData) {
    return null
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-white lg:px-12">
      <div className="mx-auto max-w-6xl">

        <div className="mb-10">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-400">
            SkillSprint AI
          </p>

          <h1 className="mt-3 text-4xl font-bold sm:text-5xl">
            Your Personalized Roadmap
          </h1>

          <p className="mt-4 max-w-3xl leading-7 text-slate-400">
            Your learning plan has been generated using Search,
            Expert System, and Fuzzy Logic.
          </p>
        </div>

        <section className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-500">
              Skill Level
            </p>

            <p className="mt-2 text-xl font-semibold">
              {roadmapData.goal.skill_level}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-500">
              Study Time
            </p>

            <p className="mt-2 text-xl font-semibold">
              {roadmapData.goal.study_hours_per_day} hrs/day
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-500">
              Target Date
            </p>

            <p className="mt-2 text-xl font-semibold">
              {roadmapData.goal.target_date}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-500">
              Roadmap Days
            </p>

            <p className="mt-2 text-xl font-semibold">
              {roadmapData.ci.search.total_days}
            </p>
          </div>
        </section>

        <section className="mt-10 rounded-3xl border border-cyan-400/20 bg-slate-900 p-6 sm:p-8">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.15em] text-cyan-400">
                AI-generated plan
              </p>

              <h2 className="mt-2 text-2xl font-bold">
                Your Learning Journey
              </h2>
            </div>

            <div className="rounded-xl bg-slate-950 px-4 py-3 text-sm text-slate-300">
              {roadmapData.ci.search.total_minutes} total minutes
            </div>
          </div>

          <div className="mt-8 space-y-5">
            {roadmapData.roadmap.map((day) => (
              <div
                key={day.day}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
              >
                <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
                  <div>
                    <p className="text-lg font-bold">
                      Day {day.day}
                    </p>

                    <p className="text-sm text-slate-500">
                      {day.total_minutes} minutes planned
                    </p>
                  </div>

                  <span className="rounded-full bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-400">
                    {day.tasks.length}{' '}
                    {day.tasks.length === 1
                      ? 'task'
                      : 'tasks'}
                  </span>
                </div>

                <div className="mt-4 space-y-3">
                  {day.tasks.map((task) => (
                    <div
                      key={`${day.day}-${task.topic_id}`}
                      className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900 p-4 sm:flex-row sm:items-center sm:justify-between"
                    >
                      <div>
                        <p className="font-semibold">
                          {task.name}
                        </p>

                        <div className="mt-2 flex flex-wrap gap-2">
                          <span className="rounded-full bg-slate-800 px-2.5 py-1 text-xs text-slate-400">
                            Difficulty {task.difficulty}
                          </span>

                          {task.is_optional && (
                            <span className="rounded-full bg-amber-400/10 px-2.5 py-1 text-xs text-amber-300">
                              Optional
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="text-sm font-semibold text-cyan-400">
                        {task.minutes} min
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-8 grid gap-5 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm font-semibold text-cyan-400">
              SEARCH
            </p>

            <h3 className="mt-2 text-xl font-bold">
              A* Roadmap Search
            </h3>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Search optimized the topic sequence while respecting
              prerequisite relationships and daily study capacity.
            </p>

            <div className="mt-5 text-sm text-slate-300">
              Nodes explored:{' '}
              <span className="font-semibold text-white">
                {roadmapData.ci.search.nodes_expanded}
              </span>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm font-semibold text-cyan-400">
              EXPERT SYSTEM
            </p>

            <h3 className="mt-2 text-xl font-bold">
              Rule-Based Planning
            </h3>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              The expert system evaluates the learner situation and
              selects an appropriate planning strategy.
            </p>

            <div className="mt-5 rounded-xl bg-slate-950 px-4 py-3 text-sm text-slate-300">
              Strategy:
              <span className="ml-2 font-semibold text-cyan-400">
                {String(
                  (roadmapData.ci.expert as {
                    selected_strategy?: string
                  })?.selected_strategy ||
                    'NO_CHANGE'
                )}
              </span>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm font-semibold text-cyan-400">
              FUZZY LOGIC
            </p>

            <h3 className="mt-2 text-xl font-bold">
              Adaptive Workload
            </h3>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Fuzzy Logic evaluates time availability and learning
              progress to determine workload adjustment.
            </p>

            <div className="mt-5 rounded-xl bg-slate-950 px-4 py-3 text-sm text-slate-300">
              Adaptive adjustment calculated
            </div>
          </div>
        </section>

        <div className="mt-10 flex flex-col gap-3 sm:flex-row">
          <button
            onClick={() => navigate('/tracks')}
            className="rounded-xl border border-slate-700 px-5 py-3 font-semibold text-slate-300 hover:border-cyan-400 hover:text-cyan-400"
          >
            Create Another Goal
          </button>
        </div>

      </div>
    </main>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/tracks" element={<TracksPage />} />
        <Route path="/tracks/:slug" element={<TrackDetailPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/roadmap" element={<RoadmapPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App