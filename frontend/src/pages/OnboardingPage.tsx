import { useState } from 'react'
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom'

function OnboardingPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()

  const selectedTrack =
    searchParams.get('track') ||
    location.state?.track ||
    'full-stack'

  const [level, setLevel] = useState('Beginner')
  const [studyHours, setStudyHours] = useState('2')
  const [targetDate, setTargetDate] = useState('')
  const [knownTopics, setKnownTopics] = useState('')
  const [commitment, setCommitment] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const trackIds: Record<string, number> = {
    'full-stack': 1,
    'data-analytics': 2,
    'ui-ux': 3,
  }

  const trackNames: Record<string, string> = {
    'full-stack': 'Full Stack Development',
    'data-analytics': 'Data Analytics',
    'ui-ux': 'UI/UX Design',
  }

  const selectedTrackId = trackIds[selectedTrack]

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault()

    if (!targetDate || !commitment) {
      return
    }

    if (!selectedTrackId) {
      setError('Invalid learning track selected.')
      return
    }

    setIsSubmitting(true)
    setError('')

    const [year, month, day] = targetDate.split('-')

    const formattedTargetDate = `${day}/${month}/${year}`

    const knownTopicsList = knownTopics
      .split(',')
      .map((topic) => topic.trim())
      .filter((topic) => topic.length > 0)

    const onboardingData = {
      track: selectedTrack,
      track_id: selectedTrackId,
      level,
      studyHours: Number(studyHours),
      targetDate: formattedTargetDate,
      knownTopics: knownTopicsList,
      commitment,
    }

    try {
      const response = await fetch(
        'http://127.0.0.1:5000/api/v1/goals',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            track_id: selectedTrackId,
            skill_level: level,
            study_hours_per_day: Number(studyHours),
            target_date: formattedTargetDate,
            known_topics: knownTopicsList,
            commitment,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.message || 'Could not create your learning goal.'
        )
      }

      console.log('Goal created:', data)

      navigate('/roadmap', {
        state: {
          ...onboardingData,
          goalId: data.goal.id,
        },
      })
    } catch (submitError) {
      console.error('Goal creation error:', submitError)

      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Could not connect to the backend.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-white lg:px-12">
      <div className="mx-auto max-w-3xl">
        <div className="mb-10">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-400">
            Step 1 of 2
          </p>

          <h1 className="mt-3 text-4xl font-bold sm:text-5xl">
            Set up your learning goal
          </h1>

          <p className="mt-4 leading-7 text-slate-400">
            Tell SkillSprint AI about your learning situation so it can
            prepare a personalized roadmap.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-8 rounded-3xl border border-slate-800 bg-slate-900 p-7 sm:p-10"
        >
          <div>
            <label className="text-sm font-semibold text-slate-200">
              Selected Learning Track
            </label>

            <div className="mt-3 rounded-xl border border-cyan-400/30 bg-cyan-400/5 px-4 py-3 text-cyan-400">
              {trackNames[selectedTrack] || 'Unknown Track'}
            </div>
          </div>

          <div>
            <label
              htmlFor="level"
              className="text-sm font-semibold text-slate-200"
            >
              Current Skill Level
            </label>

            <select
              id="level"
              value={level}
              onChange={(event) => setLevel(event.target.value)}
              className="mt-3 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400"
            >
              <option>Beginner</option>
              <option>Intermediate</option>
              <option>Advanced</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="studyHours"
              className="text-sm font-semibold text-slate-200"
            >
              Available Study Hours Per Day
            </label>

            <select
              id="studyHours"
              value={studyHours}
              onChange={(event) => setStudyHours(event.target.value)}
              className="mt-3 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400"
            >
              <option value="1">1 hour</option>
              <option value="2">2 hours</option>
              <option value="3">3 hours</option>
              <option value="4">4 hours</option>
              <option value="5">5 hours</option>
              <option value="6">6+ hours</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="targetDate"
              className="text-sm font-semibold text-slate-200"
            >
              Target Completion Date
            </label>

            <input
              id="targetDate"
              type="date"
              value={targetDate}
              onChange={(event) => setTargetDate(event.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="mt-3 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400"
              required
            />
          </div>

          <div>
            <label
              htmlFor="knownTopics"
              className="text-sm font-semibold text-slate-200"
            >
              Topics You Already Know
            </label>

            <textarea
              id="knownTopics"
              value={knownTopics}
              onChange={(event) => setKnownTopics(event.target.value)}
              placeholder="Example: HTML, CSS, basic JavaScript"
              rows={4}
              className="mt-3 w-full resize-none rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder:text-slate-600 outline-none focus:border-cyan-400"
            />

            <p className="mt-2 text-xs text-slate-500">
              Separate multiple topics with commas.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
            <label className="flex cursor-pointer gap-3">
              <input
                type="checkbox"
                checked={commitment}
                onChange={(event) =>
                  setCommitment(event.target.checked)
                }
                className="mt-1 h-4 w-4 accent-cyan-400"
                required
              />

              <span className="text-sm leading-6 text-slate-300">
                I commit to following my learning plan and completing my
                scheduled study sessions as consistently as possible.
              </span>
            </label>
          </div>

          {error && (
            <div className="rounded-xl border border-red-400/30 bg-red-400/10 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl bg-cyan-400 px-6 py-3.5 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting
              ? 'Saving Your Goal...'
              : 'Generate My Roadmap'}
          </button>
        </form>
      </div>
    </main>
  )
}

export default OnboardingPage