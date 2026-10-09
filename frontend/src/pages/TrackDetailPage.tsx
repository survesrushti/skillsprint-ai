import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Code2,
  Clock3,
  Palette,
} from 'lucide-react'

const trackData = {
  'full-stack': {
    title: 'Full Stack Development',
    description:
      'Build practical skills for developing modern web applications across frontend, backend, databases, APIs, and authentication.',
    level: 'Beginner to Intermediate',
    duration: '10–12 weeks',
    icon: Code2,
    topics: [
      'HTML, CSS & JavaScript',
      'Git & GitHub',
      'React & TypeScript',
      'Backend Development',
      'REST APIs',
      'Databases & SQL',
      'Authentication',
      'Full Stack Project',
    ],
  },

  'data-analytics': {
    title: 'Data Analytics',
    description:
      'Learn how to collect, clean, analyze, visualize, and interpret data to discover useful patterns and insights.',
    level: 'Beginner to Intermediate',
    duration: '8–10 weeks',
    icon: BarChart3,
    topics: [
      'Python Fundamentals',
      'NumPy',
      'Pandas',
      'Data Cleaning',
      'Exploratory Data Analysis',
      'Statistics',
      'Data Visualization',
      'Analytics Project',
    ],
  },

  'ui-ux': {
    title: 'UI/UX Design',
    description:
      'Develop practical skills for understanding users and designing intuitive, useful, and visually effective digital experiences.',
    level: 'Beginner to Intermediate',
    duration: '6–8 weeks',
    icon: Palette,
    topics: [
      'Design Fundamentals',
      'User Research',
      'Information Architecture',
      'Wireframing',
      'Visual Design',
      'Design Systems',
      'Prototyping',
      'UX Case Study',
    ],
  },
}

function TrackDetailPage() {
  const { slug } = useParams()

  const track = trackData[slug as keyof typeof trackData]

  if (!track) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Track not found</h1>

          <p className="mt-3 text-slate-400">
            The learning track you are looking for does not exist.
          </p>

          <Link
            to="/tracks"
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950"
          >
            <ArrowLeft size={17} />
            Back to Tracks
          </Link>
        </div>
      </main>
    )
  }

  const Icon = track.icon

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto max-w-7xl px-6 py-12 lg:px-12">
        <Link
          to="/tracks"
          className="inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-cyan-400"
        >
          <ArrowLeft size={17} />
          Back to Learning Tracks
        </Link>

        <div className="mt-10 grid gap-12 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-400">
              <Icon size={32} />
            </div>

            <p className="mt-7 text-sm font-semibold uppercase tracking-[0.2em] text-cyan-400">
              Learning Track
            </p>

            <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
              {track.title}
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">
              {track.description}
            </p>

            <div className="mt-7 flex flex-wrap gap-4">
              <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-300">
                <Clock3 size={18} className="text-cyan-400" />
                {track.duration}
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-300">
                {track.level}
              </div>
            </div>

            <Link
              to={`/onboarding?track=${slug}`}
              className="mt-8 inline-flex items-center gap-2 rounded-xl bg-cyan-400 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              Start This Track
              <ArrowRight size={18} />
            </Link>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-7">
            <p className="text-sm font-semibold uppercase tracking-[0.15em] text-cyan-400">
              Learning Path
            </p>

            <h2 className="mt-3 text-2xl font-bold">
              What you will learn
            </h2>

            <div className="mt-7 space-y-4">
              {track.topics.map((topic, index) => (
                <div
                  key={topic}
                  className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-950 p-4"
                >
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-cyan-400/10 text-sm font-semibold text-cyan-400">
                    {index + 1}
                  </div>

                  <span className="flex-1 text-sm text-slate-300">
                    {topic}
                  </span>

                  <CheckCircle2
                    size={18}
                    className="text-slate-600"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-16 rounded-3xl border border-cyan-400/20 bg-cyan-400/5 p-8">
          <h2 className="text-2xl font-bold">
            Your roadmap will be personalized
          </h2>

          <p className="mt-3 max-w-3xl leading-7 text-slate-400">
            SkillSprint AI will use your background, available study time,
            learning progress, and target completion date to create an
            adaptive roadmap instead of giving you the same fixed schedule
            as every other learner.
          </p>

          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <p className="text-sm font-semibold text-white">
                Personalized
              </p>
              <p className="mt-2 text-sm text-slate-500">
                Based on your current level and learning goal.
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <p className="text-sm font-semibold text-white">
                Adaptive
              </p>
              <p className="mt-2 text-sm text-slate-500">
                Adjusts when your schedule or progress changes.
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <p className="text-sm font-semibold text-white">
                Intelligent
              </p>
              <p className="mt-2 text-sm text-slate-500">
                Uses Computational Intelligence to guide the roadmap.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default TrackDetailPage