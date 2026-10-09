import { Link } from 'react-router-dom'
import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Code2,
  Palette,
} from 'lucide-react'

const tracks = [
  {
    id: 'full-stack',
    title: 'Full Stack Development',
    description:
      'Learn how modern web applications are designed and built from frontend to backend.',
    icon: Code2,
    level: 'Beginner to Intermediate',
    topics: [
      'HTML, CSS & JavaScript',
      'React & TypeScript',
      'Backend Development',
      'APIs & Authentication',
      'Databases',
    ],
  },
  {
    id: 'data-analytics',
    title: 'Data Analytics',
    description:
      'Develop practical skills to collect, clean, analyze, visualize, and interpret data.',
    icon: BarChart3,
    level: 'Beginner to Intermediate',
    topics: [
      'Python for Data Analysis',
      'Pandas & NumPy',
      'Data Cleaning',
      'Data Visualization',
      'Statistics & Insights',
    ],
  },
  {
    id: 'ui-ux',
    title: 'UI/UX Design',
    description:
      'Learn how to design useful, intuitive, and user-centered digital experiences.',
    icon: Palette,
    level: 'Beginner to Intermediate',
    topics: [
      'User Research',
      'Information Architecture',
      'Wireframing',
      'Visual Design',
      'Prototyping',
    ],
  },
]

function TracksPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-12">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-400">
            Learning Tracks
          </p>

          <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
            Choose your learning path
          </h1>

          <p className="mt-5 text-lg leading-8 text-slate-400">
            SkillSprint AI currently provides three curated learning tracks.
            Choose a goal and the system will later create a personalized
            roadmap around your background, available study time, and target
            date.
          </p>
        </div>

        <div className="mt-12 grid gap-7 lg:grid-cols-3">
          {tracks.map((track) => {
            const Icon = track.icon

            return (
              <article
                key={track.id}
                className="flex flex-col rounded-2xl border border-slate-800 bg-slate-900 p-7 transition hover:-translate-y-1 hover:border-cyan-400"
              >
                <div className="flex items-center justify-between">
                  <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                    <Icon size={28} />
                  </div>

                  <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400">
                    {track.level}
                  </span>
                </div>

                <h2 className="mt-7 text-2xl font-semibold">
                  {track.title}
                </h2>

                <p className="mt-3 min-h-20 text-sm leading-6 text-slate-400">
                  {track.description}
                </p>

                <div className="mt-6 border-t border-slate-800 pt-6">
                  <p className="text-sm font-semibold text-white">
                    Core topics
                  </p>

                  <ul className="mt-4 space-y-3">
                    {track.topics.map((topic) => (
                      <li
                        key={topic}
                        className="flex items-center gap-3 text-sm text-slate-400"
                      >
                        <CheckCircle2
                          size={17}
                          className="shrink-0 text-cyan-400"
                        />
                        {topic}
                      </li>
                    ))}
                  </ul>
                </div>

                <Link
                  to={`/tracks/${track.id}`}
                  className="mt-8 flex items-center justify-center gap-2 rounded-xl border border-slate-700 px-5 py-3 text-sm font-semibold transition hover:border-cyan-400 hover:text-cyan-400"
                >
                  View Track
                  <ArrowRight size={17} />
                </Link>
              </article>
            )
          })}
        </div>
      </section>
    </main>
  )
}

export default TracksPage