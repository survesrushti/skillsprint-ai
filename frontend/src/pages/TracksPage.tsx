import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Code2,
  Palette,
  Sparkles,
  type LucideIcon,
} from 'lucide-react'
import Navbar from '../components/layout/Navbar'
import { getTracks, type TrackData } from '../api/client'
import { soundClick } from '../utils/sound'

interface DisplayTrack {
  id: string
  title: string
  description: string
  icon: LucideIcon
  level: string
  color: string
  topics: string[]
}

const fallbackTracks: DisplayTrack[] = [
  {
    id: 'full-stack-development',
    title: 'Full Stack Development',
    description:
      'Master modern web applications from frontend interfaces to backend APIs, databases, and deployments.',
    icon: Code2,
    level: 'Beginner to Intermediate',
    color: 'accent-violet',
    topics: [
      'HTML & CSS Fundamentals',
      'JavaScript ES6+ & Async Systems',
      'React Components & Hooks',
      'Backend REST APIs with Flask',
      'Relational Databases & SQL',
    ],
  },
  {
    id: 'data-analytics',
    title: 'Data Analytics & Engineering',
    description:
      'Collect, clean, explore, visualize, and model data with Python, Pandas, SQL joins, and dashboards.',
    icon: BarChart3,
    level: 'Beginner to Intermediate',
    color: 'accent-cyan',
    topics: [
      'Python for Data Analysis',
      'Pandas & NumPy Arrays',
      'SQL Queries & Aggregations',
      'Data Visualization & Dashboards',
      'Statistical Reasoning',
    ],
  },
  {
    id: 'ui-ux-design',
    title: 'UI/UX Product Design',
    description:
      'Design useful, intuitive, and accessible user experiences with wireframes, Figma, and design systems.',
    icon: Palette,
    level: 'Beginner to Intermediate',
    color: 'accent-rose',
    topics: [
      'User Research & Personas',
      'Information Architecture',
      'Wireframing & Prototyping',
      'Figma Design Systems',
      'Usability & WCAG Accessibility',
    ],
  },
]

function getTrackIcon(slug: string, name: string): LucideIcon {
  const s = `${slug} ${name}`.toLowerCase()
  if (s.includes('data') || s.includes('analytic')) return BarChart3
  if (s.includes('ui') || s.includes('ux') || s.includes('design')) return Palette
  return Code2
}

function getTrackColor(slug: string, name: string): string {
  const s = `${slug} ${name}`.toLowerCase()
  if (s.includes('data') || s.includes('analytic')) return 'accent-cyan'
  if (s.includes('ui') || s.includes('ux') || s.includes('design')) return 'accent-rose'
  return 'accent-violet'
}

function TracksPage() {
  const [tracks, setTracks] = useState<DisplayTrack[]>(fallbackTracks)

  useEffect(() => {
    let isMounted = true

    async function loadTracks() {
      try {
        const res = await getTracks()
        if (isMounted && res.tracks && res.tracks.length > 0) {
          const mapped: DisplayTrack[] = res.tracks.map((t: TrackData) => {
            const topicNames =
              t.topics && t.topics.length > 0
                ? t.topics.slice(0, 5).map((top) => top.name)
                : [
                    'Fundamental concepts',
                    'Core tools & workflow',
                    'Intermediate techniques',
                    'Best practices & architecture',
                    'Capstone project',
                  ]

            return {
              id: t.slug,
              title: t.name,
              description:
                t.description ||
                'Curated learning track with adaptive roadmap pacing.',
              icon: getTrackIcon(t.slug, t.name),
              level: 'Beginner to Intermediate',
              color: getTrackColor(t.slug, t.name),
              topics: topicNames,
            }
          })
          setTracks(mapped)
        }
      } catch (err) {
        console.warn('Could not fetch dynamic tracks, using fallback tracks:', err)
      }
    }

    loadTracks()
    return () => {
      isMounted = false
    }
  }, [])

  return (
    <>
      <Navbar />

      <main className="min-h-screen text-slate-100">
        <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 space-y-10">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-violet/10 text-accent-violet text-xs font-mono">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Curated Learning Tracks</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              Choose Your Learning Track
            </h1>

            <p className="text-sm sm:text-base text-slate-400 leading-relaxed">
              SkillSprint AI provides structured curricula with open resources. Choose a track, and our
              A* search engine will synthesize a personalized roadmap tailored to your target completion date
              and available study time.
            </p>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            {tracks.map((track) => {
              const Icon = track.icon

              return (
                <article
                  key={track.id}
                  className="glass-card rounded-3xl p-7 border border-slate-800 flex flex-col justify-between hover:border-accent-violet/50 transition group"
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent-violet/10 text-accent-violet border border-accent-violet/20 group-hover:scale-105 transition">
                        <Icon className="w-6 h-6" />
                      </div>

                      <span className="rounded-full border border-slate-800 bg-obsidian-900 px-3 py-1 text-[11px] font-mono text-slate-400">
                        {track.level}
                      </span>
                    </div>

                    <h2 className="mt-6 text-xl font-bold text-white group-hover:text-accent-violet transition">
                      {track.title}
                    </h2>

                    <p className="mt-2 text-xs sm:text-sm leading-relaxed text-slate-400">
                      {track.description}
                    </p>

                    <div className="mt-6 border-t border-slate-800/80 pt-5 space-y-3">
                      <p className="text-xs font-bold font-mono uppercase tracking-wider text-slate-300">
                        Featured Topics (9 Total)
                      </p>

                      <ul className="space-y-2">
                        {track.topics.map((topic) => (
                          <li
                            key={topic}
                            className="flex items-center gap-2.5 text-xs text-slate-300"
                          >
                            <CheckCircle2 className="w-4 h-4 text-accent-emerald shrink-0" />
                            <span>{topic}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="mt-8 pt-5 border-t border-slate-800/80 flex items-center gap-3">
                    <Link
                      to={`/onboarding?track=${track.id}`}
                      onClick={() => soundClick()}
                      className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-accent-violet to-indigo-600 hover:from-accent-violet/90 hover:to-indigo-500 text-white text-xs font-semibold shadow-glow-violet transition text-center flex items-center justify-center gap-1.5"
                    >
                      <span>Start Roadmap</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>

                    <Link
                      to={`/tracks/${track.id}`}
                      onClick={() => soundClick()}
                      className="px-3.5 py-2.5 rounded-xl bg-obsidian-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white text-xs font-mono transition"
                    >
                      Details
                    </Link>
                  </div>
                </article>
              )
            })}
          </div>
        </section>
      </main>
    </>
  )
}

export default TracksPage