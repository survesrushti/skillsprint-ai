import { Link } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import {
  Code2,
  Database,
  Palette,
  ArrowRight,
  GitBranch,
  Zap,
  SlidersHorizontal,
  Sparkles,
  Play,
  Compass,
} from 'lucide-react'
import { soundClick } from '../utils/sound'

function LandingPage() {
  return (
    <>
      <Navbar />

      <main className="min-h-screen text-slate-100 flex flex-col justify-between">
        {/* ==================== HERO SECTION ==================== */}
        <section className="relative hero-glow px-4 sm:px-6 lg:px-8 pt-12 pb-20 max-w-7xl mx-auto w-full">
          <div className="text-center max-w-3xl mx-auto space-y-6 pt-4 sm:pt-8">
            {/* Live Research Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-obsidian-900/80 border border-accent-violet/30 text-[11px] font-mono text-accent-violet shadow-sm">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-violet opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-violet" />
              </span>
              <span>Computational Intelligence in Adaptive Education</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-[1.12]">
              The Learning Roadmap That{' '}
              <span className="text-accent-indigo dark:text-white">
                Adapts When Life Happens.
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-base sm:text-lg text-slate-400 font-normal leading-relaxed max-w-2xl mx-auto">
              Most learners abandon static online roadmaps when they miss a session.{' '}
              <strong className="text-slate-200">SkillSprint AI</strong> uses Search,
              Expert Systems, and Fuzzy Logic to continuously adjust your pace, manage daily workload,
              and guarantee completion.
            </p>

            {/* Hero CTAs */}
            <div className="flex flex-wrap items-center justify-center gap-3 pt-3">
              <Link
                to="/onboarding"
                onClick={() => soundClick()}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-accent-violet to-indigo-600 hover:from-accent-violet/90 hover:to-indigo-500 text-white text-sm font-semibold shadow-glow-violet transition flex items-center gap-2 group"
              >
                <span>Build Your Personalized Track</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
              </Link>

              <Link
                to="/tracks"
                onClick={() => soundClick()}
                className="px-5 py-3 rounded-xl bg-obsidian-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white text-sm font-medium transition flex items-center gap-2"
              >
                <Compass className="w-4 h-4 text-cyan-400" />
                <span>Explore Tracks</span>
              </Link>

              <Link
                to="/dashboard"
                onClick={() => soundClick()}
                className="px-4 py-3 rounded-xl bg-obsidian-900/60 border border-slate-800/80 hover:border-slate-700 text-slate-400 hover:text-slate-200 text-sm font-medium transition flex items-center gap-1.5"
              >
                <Play className="w-3.5 h-3.5 text-accent-violet" />
                <span>Dashboard</span>
              </Link>
            </div>

            {/* Verified Project Architecture Metrics */}
            <div className="pt-8 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-2xl mx-auto border-t border-slate-800/80 text-left">
              <div className="p-3">
                <p className="text-2xl font-bold font-mono text-white">3</p>
                <p className="text-xs text-slate-400 mt-0.5">CI Engines (A*, Expert, Fuzzy)</p>
              </div>

              <div className="p-3">
                <p className="text-2xl font-bold font-mono text-accent-violet">3 V1</p>
                <p className="text-xs text-slate-400 mt-0.5">Curated Learning Tracks</p>
              </div>

              <div className="p-3">
                <p className="text-2xl font-bold font-mono text-cyan-400">27</p>
                <p className="text-xs text-slate-400 mt-0.5">Structured Topics (9 / Track)</p>
              </div>

              <div className="p-3">
                <p className="text-2xl font-bold font-mono text-accent-emerald">100%</p>
                <p className="text-xs text-slate-400 mt-0.5">Free & Open Resources</p>
              </div>
            </div>
          </div>

          {/* ==================== CI PILLARS ==================== */}
          <div className="mt-20 space-y-4">
            <div className="text-center max-w-xl mx-auto">
              <p className="text-xs uppercase font-mono tracking-wider text-accent-violet font-semibold">
                Under The Hood
              </p>
              <h2 className="text-2xl sm:text-3xl font-bold text-white mt-1">
                Computational Intelligence Architecture
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-4">
              {/* Pillar 1: Search */}
              <div className="glass-card rounded-2xl p-6 relative overflow-hidden group">
                <div className="w-10 h-10 rounded-xl bg-accent-violet/10 border border-accent-violet/20 flex items-center justify-center text-accent-violet mb-4">
                  <GitBranch className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">
                  1. Heuristic Search Engine
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Generates an optimal topic dependency path graph. Evaluates prerequisite constraints,
                  your daily time capacity, and prioritizes core foundational concepts to minimize total study hours.
                </p>
                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-indigo-300">
                  <span>Goal: Min total time</span>
                  <span className="font-semibold text-accent-violet">A* Search</span>
                </div>
              </div>

              {/* Pillar 2: Expert System */}
              <div className="glass-card rounded-2xl p-6 relative overflow-hidden group">
                <div className="w-10 h-10 rounded-xl bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center text-cyan-400 mb-4">
                  <Zap className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">
                  2. Rule-Based Expert System
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Applies cognitive heuristics when you miss a study session. Automatically reorganizes buffer
                  days, redistributes micro-topics, and prevents deadline drift without causing learner burnout.
                </p>
                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-cyan-300">
                  <span>Trigger: Missed Session</span>
                  <span className="font-semibold text-cyan-400">Rule Inference</span>
                </div>
              </div>

              {/* Pillar 3: Fuzzy Logic */}
              <div className="glass-card rounded-2xl p-6 relative overflow-hidden group">
                <div className="w-10 h-10 rounded-xl bg-accent-emerald/10 border border-accent-emerald/20 flex items-center justify-center text-accent-emerald mb-4">
                  <SlidersHorizontal className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">
                  3. Fuzzy Logic Engine
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Human schedules aren't binary. Fuzzy membership functions gauge student fatigue, task complexity,
                  and subjective confidence to dynamically dial daily study quota up or down.
                </p>
                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-emerald-800 dark:text-emerald-300">
                  <span>Dynamic Workload</span>
                  <span className="font-semibold text-accent-emerald">Mamdani Model</span>
                </div>
              </div>
            </div>
          </div>

          {/* ==================== CURATED TRACKS SHOWCASE ==================== */}
          <div className="mt-16 p-6 sm:p-8 rounded-3xl glass-panel border border-slate-800/80">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-bold text-white">Supported Learning Tracks (V1)</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Curricula mapped with official documentation, community roadmaps, and high-quality open materials.
                </p>
              </div>

              <Link
                to="/tracks"
                onClick={() => soundClick()}
                className="text-xs font-semibold text-accent-violet hover:text-white flex items-center gap-1 transition"
              >
                <span>View all tracks</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6">
              {/* Track 1 */}
              <Link
                to="/tracks/full-stack"
                onClick={() => soundClick()}
                className="p-5 rounded-2xl bg-obsidian-900 border border-slate-800/80 hover:border-accent-violet/60 transition group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center gap-2 text-indigo-400 mb-2">
                    <Code2 className="w-4 h-4" />
                    <span className="text-xs font-mono font-bold">Track 01</span>
                  </div>
                  <h4 className="font-bold text-slate-100 text-sm group-hover:text-accent-violet transition">
                    Full Stack Web Development
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    TypeScript, React, Node.js/Flask, SQL databases, and modern cloud deployment pipelines.
                  </p>
                </div>
                <div className="mt-4 flex items-center justify-between text-[10px] font-mono text-slate-500 pt-3 border-t border-slate-800/60">
                  <span>9 Milestone Topics</span>
                  <span className="text-accent-violet group-hover:translate-x-0.5 transition flex items-center gap-1">
                    Explore &rarr;
                  </span>
                </div>
              </Link>

              {/* Track 2 */}
              <Link
                to="/tracks/data-analytics"
                onClick={() => soundClick()}
                className="p-5 rounded-2xl bg-obsidian-900 border border-slate-800/80 hover:border-cyan-400/60 transition group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center gap-2 text-cyan-400 mb-2">
                    <Database className="w-4 h-4" />
                    <span className="text-xs font-mono font-bold">Track 02</span>
                  </div>
                  <h4 className="font-bold text-slate-100 text-sm group-hover:text-cyan-400 transition">
                    Data Analytics & Engineering
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    Python, Pandas, SQL joins, Tableau/PowerBI visual dashboards, and analytical statistical reasoning.
                  </p>
                </div>
                <div className="mt-4 flex items-center justify-between text-[10px] font-mono text-slate-500 pt-3 border-t border-slate-800/60">
                  <span>9 Milestone Topics</span>
                  <span className="text-cyan-400 group-hover:translate-x-0.5 transition flex items-center gap-1">
                    Explore &rarr;
                  </span>
                </div>
              </Link>

              {/* Track 3 */}
              <Link
                to="/tracks/ui-ux"
                onClick={() => soundClick()}
                className="p-5 rounded-2xl bg-obsidian-900 border border-slate-800/80 hover:border-pink-400/60 transition group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center gap-2 text-pink-400 mb-2">
                    <Palette className="w-4 h-4" />
                    <span className="text-xs font-mono font-bold">Track 03</span>
                  </div>
                  <h4 className="font-bold text-slate-100 text-sm group-hover:text-pink-400 transition">
                    UI/UX Product Design
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    User research, wireframing, Figma design systems, accessibility WCAG, and interactive prototypes.
                  </p>
                </div>
                <div className="mt-4 flex items-center justify-between text-[10px] font-mono text-slate-500 pt-3 border-t border-slate-800/60">
                  <span>9 Milestone Topics</span>
                  <span className="text-pink-400 group-hover:translate-x-0.5 transition flex items-center gap-1">
                    Explore &rarr;
                  </span>
                </div>
              </Link>
            </div>
          </div>

          {/* ==================== HOW IT WORKS ==================== */}
          <div className="mt-20">
            <div className="text-center max-w-xl mx-auto">
              <p className="text-xs uppercase font-mono tracking-wider text-cyan-400 font-semibold">
                Learner Lifecycle
              </p>
              <h2 className="text-2xl sm:text-3xl font-bold text-white mt-1">
                From Goal to Adaptive Mastery
              </h2>
            </div>

            <div className="mt-10 grid gap-6 md:grid-cols-4">
              <div className="glass-card rounded-2xl p-6 text-center">
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-accent-violet/20 font-bold font-mono text-accent-violet">
                  1
                </div>
                <h3 className="mt-4 font-bold text-sm text-white">Set Your Goal</h3>
                <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                  Select your track, prior knowledge, daily available hours, and target completion date.
                </p>
              </div>

              <div className="glass-card rounded-2xl p-6 text-center">
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/20 font-bold font-mono text-cyan-400">
                  2
                </div>
                <h3 className="mt-4 font-bold text-sm text-white">Synthesize Plan</h3>
                <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                  A* search computes the optimal dependency path and packs daily study sprints.
                </p>
              </div>

              <div className="glass-card rounded-2xl p-6 text-center">
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-accent-emerald/20 font-bold font-mono text-accent-emerald">
                  3
                </div>
                <h3 className="mt-4 font-bold text-sm text-white">Learn & Track</h3>
                <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                  Execute curated learning resources, check off tasks, and build study streaks.
                </p>
              </div>

              <div className="glass-card rounded-2xl p-6 text-center">
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-amber-400/20 font-bold font-mono text-amber-800 dark:text-amber-300">
                  4
                </div>
                <h3 className="mt-4 font-bold text-sm text-white">Adapt & Finish</h3>
                <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                  If life disrupts your rhythm, the expert system rebalances your schedule gracefully.
                </p>
              </div>
            </div>
          </div>

          {/* ==================== BOTTOM CTA ==================== */}
          <div className="mt-20 glass-panel rounded-3xl p-8 sm:p-12 text-center gradient-border shadow-2xl relative overflow-hidden">
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white">
              Ready to make your learning roadmap adaptive?
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-sm text-slate-400 leading-relaxed">
              Never let missed days derail your goals again. Let Computational Intelligence keep you on track.
            </p>
            <div className="mt-8 flex justify-center">
              <Link
                to="/onboarding"
                onClick={() => soundClick()}
                className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-accent-violet via-indigo-600 to-cyan-500 hover:from-accent-violet/90 hover:to-cyan-400 text-white font-semibold text-sm shadow-glow-violet transition flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>Start Your Personalized Journey</span>
              </Link>
            </div>
          </div>
        </section>

        {/* ==================== FOOTER ==================== */}
        <footer className="border-t border-slate-800/80 bg-obsidian-950 px-6 py-8">
          <div className="mx-auto flex max-w-7xl flex-col gap-3 text-center text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:text-left">
            <div className="flex items-center justify-center sm:justify-start gap-2">
              <span className="font-bold text-slate-300">SkillSprint AI</span>
              <span>— M.Sc. Computational Intelligence Mini Project</span>
            </div>
            <p>Adaptive Learning Coach powered by A* Search, Expert System, and Fuzzy Logic.</p>
          </div>
        </footer>
      </main>
    </>
  )
}

export default LandingPage