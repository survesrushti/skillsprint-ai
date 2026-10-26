import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Code2,
  Clock3,
  Palette,
  Sparkles,
  GitBranch,
  Zap,
  SlidersHorizontal,
  type LucideIcon,
} from 'lucide-react'
import Navbar from '../components/layout/Navbar'
import { getTrackBySlug } from '../api/client'
import { soundClick } from '../utils/sound'

interface TrackInfo {
  title: string
  description: string
  level: string
  duration: string
  icon: LucideIcon
  topics: string[]
  slug: string
}

const fallbackTrackData: Record<string, TrackInfo> = {
  'full-stack': {
    title: 'Full Stack Development',
    description:
      'Build practical skills for developing modern web applications across frontend, backend, databases, APIs, and authentication.',
    level: 'Beginner to Intermediate',
    duration: '8–10 weeks',
    icon: Code2,
    slug: 'full-stack-development',
    topics: [
      'HTML Fundamentals',
      'CSS Fundamentals',
      'JavaScript Fundamentals',
      'Git and GitHub',
      'React Fundamentals',
      'Backend REST APIs with Flask',
      'Relational Databases and SQL',
      'User Authentication and Security',
      'Full Stack Deployment and Capstone',
    ],
  },
  'full-stack-development': {
    title: 'Full Stack Development',
    description:
      'Build practical skills for developing modern web applications across frontend, backend, databases, APIs, and authentication.',
    level: 'Beginner to Intermediate',
    duration: '8–10 weeks',
    icon: Code2,
    slug: 'full-stack-development',
    topics: [
      'HTML Fundamentals',
      'CSS Fundamentals',
      'JavaScript Fundamentals',
      'Git and GitHub',
      'React Fundamentals',
      'Backend REST APIs with Flask',
      'Relational Databases and SQL',
      'User Authentication and Security',
      'Full Stack Deployment and Capstone',
    ],
  },
  'data-analytics': {
    title: 'Data Analytics & Engineering',
    description:
      'Learn how to collect, clean, analyze, visualize, and interpret data to discover useful patterns and insights.',
    level: 'Beginner to Intermediate',
    duration: '6–8 weeks',
    icon: BarChart3,
    slug: 'data-analytics',
    topics: [
      'Python for Data Analysis',
      'NumPy Fundamentals',
      'Pandas Data Manipulation',
      'Data Cleaning and Preparation',
      'SQL for Data Analysis',
      'Data Visualization with Matplotlib and Seaborn',
      'Exploratory Data Analysis (EDA)',
      'Business Intelligence Dashboards',
      'Data Analytics Capstone Project',
    ],
  },
  'ui-ux': {
    title: 'UI/UX Product Design',
    description:
      'Develop practical skills for understanding users and designing intuitive, useful, and visually effective digital experiences.',
    level: 'Beginner to Intermediate',
    duration: '6–8 weeks',
    icon: Palette,
    slug: 'ui-ux-design',
    topics: [
      'UI/UX Design Fundamentals',
      'User Research and Personas',
      'Information Architecture',
      'Wireframing Fundamentals',
      'Visual Design and Hierarchy',
      'Figma and Design Systems',
      'Interactive Prototyping',
      'Usability Testing and WCAG Accessibility',
      'UI/UX Case Study Capstone',
    ],
  },
  'ui-ux-design': {
    title: 'UI/UX Product Design',
    description:
      'Develop practical skills for understanding users and designing intuitive, useful, and visually effective digital experiences.',
    level: 'Beginner to Intermediate',
    duration: '6–8 weeks',
    icon: Palette,
    slug: 'ui-ux-design',
    topics: [
      'UI/UX Design Fundamentals',
      'User Research and Personas',
      'Information Architecture',
      'Wireframing Fundamentals',
      'Visual Design and Hierarchy',
      'Figma and Design Systems',
      'Interactive Prototyping',
      'Usability Testing and WCAG Accessibility',
      'UI/UX Case Study Capstone',
    ],
  },
}

function getTrackIcon(slug: string, name: string): LucideIcon {
  const s = `${slug} ${name}`.toLowerCase()
  if (s.includes('data') || s.includes('analytic')) return BarChart3
  if (s.includes('ui') || s.includes('ux') || s.includes('design')) return Palette
  return Code2
}

function TrackDetailPage() {
  const { slug } = useParams<{ slug: string }>()

  const initialTrack = slug ? fallbackTrackData[slug] : null
  const [track, setTrack] = useState<TrackInfo | null>(initialTrack || null)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    if (!slug) return
    const currentSlug = slug
    const fallback = fallbackTrackData[currentSlug]
    let isMounted = true

    async function fetchTrack() {
      try {
        const res = await getTrackBySlug(currentSlug)
        if (isMounted && res.track) {
          const t = res.track
          setTrack({
            title: t.name,
            description: t.description,
            level: 'Beginner to Intermediate',
            duration: t.estimated_duration || '8–10 weeks',
            icon: getTrackIcon(t.slug, t.name),
            slug: t.slug,
            topics:
              t.topics && t.topics.length > 0
                ? t.topics.map((topic) => topic.name)
                : fallback?.topics || [],
          })
          setNotFound(false)
        }
      } catch (err) {
        console.warn('Could not fetch dynamic track detail from API:', err)
        if (!fallback) {
          if (isMounted) setNotFound(true)
        }
      }
    }

    fetchTrack()
    return () => {
      isMounted = false
    }
  }, [slug])

  if (notFound || (!track && !initialTrack)) {
    return (
      <>
        <Navbar />
        <main className="flex min-h-screen items-center justify-center px-6 text-white">
          <div className="glass-panel rounded-3xl p-8 border border-rose-500/30 text-center space-y-4">
            <h1 className="text-2xl font-bold">Track Not Found</h1>
            <p className="text-xs text-slate-400">
              The learning track you are looking for does not exist.
            </p>
            <div className="pt-2">
              <Link
                to="/tracks"
                onClick={() => soundClick()}
                className="inline-flex items-center gap-2 rounded-xl bg-accent-violet hover:bg-accent-violet/90 px-5 py-2.5 text-xs font-semibold text-white shadow-glow-violet transition"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Tracks</span>
              </Link>
            </div>
          </div>
        </main>
      </>
    )
  }

  const activeTrack = track || initialTrack!
  const Icon = activeTrack.icon

  return (
    <>
      <Navbar />

      <main className="min-h-screen text-slate-100">
        <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 space-y-10">
          <Link
            to="/tracks"
            onClick={() => soundClick()}
            className="inline-flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-accent-violet transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to All Learning Tracks</span>
          </Link>

          <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
            {/* Left Column: Track Details & CTA */}
            <div className="space-y-6">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent-violet/10 text-accent-violet border border-accent-violet/20 shadow-glow-violet">
                <Icon className="w-8 h-8" />
              </div>

              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-violet/10 text-accent-violet text-xs font-mono mb-2">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Curated Learning Track</span>
                </div>
                <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
                  {activeTrack.title}
                </h1>
                <p className="mt-4 max-w-2xl text-sm sm:text-base leading-relaxed text-slate-400">
                  {activeTrack.description}
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-obsidian-900 px-3.5 py-2 text-xs font-mono text-slate-300">
                  <Clock3 className="w-4 h-4 text-cyan-400" />
                  <span>{activeTrack.duration}</span>
                </div>

                <div className="rounded-xl border border-slate-800 bg-obsidian-900 px-3.5 py-2 text-xs font-mono text-slate-300">
                  {activeTrack.level}
                </div>

                <div className="rounded-xl border border-slate-800 bg-obsidian-900 px-3.5 py-2 text-xs font-mono text-slate-300">
                  {activeTrack.topics.length} Milestone Topics
                </div>
              </div>

              <div className="pt-2">
                <Link
                  to={`/onboarding?track=${activeTrack.slug || slug}`}
                  onClick={() => soundClick()}
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-accent-violet to-indigo-600 hover:from-accent-violet/90 hover:to-indigo-500 px-6 py-3 font-semibold text-white text-xs shadow-glow-violet transition"
                >
                  <span>Configure Roadmap for this Track</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>

            {/* Right Column: Topics List */}
            <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-4">
              <div className="pb-3 border-b border-slate-800">
                <p className="text-xs font-semibold uppercase font-mono tracking-wider text-cyan-400">
                  Syllabus Structure
                </p>
                <h2 className="mt-1 text-xl font-bold text-white">
                  Curriculum Milestones ({activeTrack.topics.length} Topics)
                </h2>
              </div>

              <div className="space-y-2.5">
                {activeTrack.topics.map((topic, index) => (
                  <div
                    key={topic}
                    className="flex items-center gap-3.5 rounded-xl border border-slate-800/80 bg-obsidian-900/60 p-3 hover:border-accent-violet/40 transition"
                  >
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-accent-violet/10 text-xs font-mono font-bold text-accent-violet">
                      {index + 1}
                    </div>

                    <span className="flex-1 text-xs font-semibold text-slate-200">
                      {topic}
                    </span>

                    <CheckCircle2 className="w-4 h-4 text-slate-600 shrink-0" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Computational Architecture Promise Box */}
          <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-4">
            <h2 className="text-xl font-bold text-white">
              Adaptive Synthesis Guaranteed
            </h2>

            <p className="max-w-3xl text-xs sm:text-sm leading-relaxed text-slate-400">
              When you begin this track, SkillSprint AI does not hand you a static calendar. Our A* Search
              engine models prerequisite relationships, your daily capacity, and dynamically adapts with Fuzzy Logic
              whenever schedule disruptions occur.
            </p>

            <div className="grid gap-4 sm:grid-cols-3 pt-2">
              <div className="glass-card rounded-2xl p-4 border border-slate-800">
                <div className="flex items-center gap-2 text-accent-violet text-xs font-mono font-bold mb-1">
                  <GitBranch className="w-3.5 h-3.5" />
                  <span>1. A* Pathfinding</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Sequences topics to minimize total learning time while respecting prerequisites.
                </p>
              </div>

              <div className="glass-card rounded-2xl p-4 border border-slate-800">
                <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-bold mb-1">
                  <Zap className="w-3.5 h-3.5" />
                  <span>2. Expert Adaptation</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Rebalances remaining workload when study sessions are skipped or delayed.
                </p>
              </div>

              <div className="glass-card rounded-2xl p-4 border border-slate-800">
                <div className="flex items-center gap-2 text-accent-emerald text-xs font-mono font-bold mb-1">
                  <SlidersHorizontal className="w-3.5 h-3.5" />
                  <span>3. Fuzzy Calibration</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Dynamically scales daily pace based on fatigue and weekly reflection inputs.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  )
}

export default TrackDetailPage