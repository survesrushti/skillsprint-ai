import { Link } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import {
  Code2,
  BarChart3,
  Palette,
  ArrowRight,
  Search,
  Brain,
  SlidersHorizontal,
} from 'lucide-react'

function LandingPage() {
  return (
    <>
      <Navbar />

      <main className="min-h-screen bg-slate-950 text-white">
        {/* Hero Section */}
        <section className="mx-auto flex min-h-[calc(100vh-81px)] max-w-7xl flex-col justify-center px-6 py-20 lg:px-12">
          <div className="max-w-4xl">
            <p className="mb-5 text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
              Adaptive Learning Coach
            </p>

            <h1 className="text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
              Learn smarter.
              <span className="block text-cyan-400">
                Stay on track.
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
              SkillSprint AI creates a personalized learning roadmap and
              intelligently adapts it when your schedule changes, so you can
              keep moving toward your learning goal.
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                to="/tracks"
                className="rounded-xl bg-cyan-400 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300"
              >
                Start Learning
              </Link>

              <a
                href="#tracks"
                className="rounded-xl border border-slate-700 px-6 py-3 font-semibold text-white transition hover:border-cyan-400"
              >
                Explore Tracks
              </a>
            </div>
          </div>

          {/* Feature Cards */}
          <section
            id="features"
            className="mt-16 grid gap-5 md:grid-cols-3"
          >
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">
                Personalized Roadmap
              </h2>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                Get a learning sequence based on your background, available
                study time, and target completion date.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">
                Adaptive Planning
              </h2>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                Missed a study session? SkillSprint AI can intelligently
                reschedule your remaining learning plan.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">
                Intelligent Guidance
              </h2>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                Search, Expert System, and Fuzzy Logic work together to adjust
                your learning journey.
              </p>
            </div>
          </section>
        </section>

        {/* Learning Tracks */}
        <section
          id="tracks"
          className="border-t border-slate-800 bg-slate-900/50 px-6 py-24 lg:px-12"
        >
          <div className="mx-auto max-w-7xl">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-400">
                Learning Tracks
              </p>

              <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
                Choose your learning path
              </h2>

              <p className="mt-4 leading-7 text-slate-400">
                Start with a curated learning track and let SkillSprint AI
                personalize the journey around your goals, schedule, and
                progress.
              </p>
            </div>

            <div className="mt-12 grid gap-6 md:grid-cols-3">
              {/* Full Stack */}
              <div className="group rounded-2xl border border-slate-800 bg-slate-950 p-7 transition hover:-translate-y-1 hover:border-cyan-400">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                  <Code2 size={26} />
                </div>

                <h3 className="mt-6 text-2xl font-semibold">
                  Full Stack Development
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Build skills across frontend, backend, databases, APIs,
                  authentication, and modern web development.
                </p>

                <Link
                  to="/tracks/full-stack"
                  className="mt-6 flex items-center gap-2 text-sm font-semibold text-cyan-400"
                >
                  Explore track
                  <ArrowRight
                    size={17}
                    className="transition group-hover:translate-x-1"
                  />
                </Link>
              </div>

              {/* Data Analytics */}
              <div className="group rounded-2xl border border-slate-800 bg-slate-950 p-7 transition hover:-translate-y-1 hover:border-cyan-400">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                  <BarChart3 size={26} />
                </div>

                <h3 className="mt-6 text-2xl font-semibold">
                  Data Analytics
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Learn data analysis, visualization, statistics, Python,
                  dashboards, and practical analytical thinking.
                </p>

                <Link
                  to="/tracks/data-analytics"
                  className="mt-6 flex items-center gap-2 text-sm font-semibold text-cyan-400"
                >
                  Explore track
                  <ArrowRight
                    size={17}
                    className="transition group-hover:translate-x-1"
                  />
                </Link>
              </div>

              {/* UI/UX */}
              <div className="group rounded-2xl border border-slate-800 bg-slate-950 p-7 transition hover:-translate-y-1 hover:border-cyan-400">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                  <Palette size={26} />
                </div>

                <h3 className="mt-6 text-2xl font-semibold">
                  UI/UX Design
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Develop skills in user research, wireframing, visual
                  design, prototyping, and user-centered product design.
                </p>

                <Link
                  to="/tracks/ui-ux"
                  className="mt-6 flex items-center gap-2 text-sm font-semibold text-cyan-400"
                >
                  Explore track
                  <ArrowRight
                    size={17}
                    className="transition group-hover:translate-x-1"
                  />
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* CI Section */}
        <section
          id="how-it-works"
          className="px-6 py-24 lg:px-12"
        >
          <div className="mx-auto max-w-7xl">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-400">
                Computational Intelligence
              </p>

              <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
                Intelligence behind your learning plan
              </h2>

              <p className="mt-4 leading-7 text-slate-400">
                SkillSprint AI combines three Computational Intelligence
                techniques to make learning plans adaptive instead of static.
              </p>
            </div>

            <div className="mt-12 grid gap-6 md:grid-cols-3">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-7">
                <Search className="text-cyan-400" size={28} />

                <h3 className="mt-5 text-xl font-semibold">
                  Search
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Finds an optimized learning sequence while respecting topic
                  dependencies, priorities, and available study capacity.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-7">
                <Brain className="text-cyan-400" size={28} />

                <h3 className="mt-5 text-xl font-semibold">
                  Expert System
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Uses rule-based reasoning to decide how the roadmap should
                  respond when learners fall behind or miss sessions.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-7">
                <SlidersHorizontal className="text-cyan-400" size={28} />

                <h3 className="mt-5 text-xl font-semibold">
                  Fuzzy Logic
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Determines how much the workload should change based on
                  available study time and learning progress.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="border-t border-slate-800 bg-slate-900/50 px-6 py-24 lg:px-12">
          <div className="mx-auto max-w-7xl">
            <div className="text-center">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-400">
                How It Works
              </p>

              <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
                From goal to adaptive roadmap
              </h2>
            </div>

            <div className="mt-14 grid gap-6 md:grid-cols-4">
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-cyan-400 font-bold text-slate-950">
                  1
                </div>

                <h3 className="mt-5 font-semibold">
                  Set your goal
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Choose a learning track, background level, available time,
                  and target date.
                </p>
              </div>

              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-cyan-400 font-bold text-slate-950">
                  2
                </div>

                <h3 className="mt-5 font-semibold">
                  Get your roadmap
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  SkillSprint AI generates a personalized sequence of
                  learning tasks.
                </p>
              </div>

              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-cyan-400 font-bold text-slate-950">
                  3
                </div>

                <h3 className="mt-5 font-semibold">
                  Learn and track
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Complete daily tasks and monitor your progress and
                  consistency.
                </p>
              </div>

              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-cyan-400 font-bold text-slate-950">
                  4
                </div>

                <h3 className="mt-5 font-semibold">
                  Adapt and continue
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  If your schedule changes, the system intelligently adjusts
                  the remaining roadmap.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="px-6 py-24 lg:px-12">
          <div className="mx-auto max-w-5xl rounded-3xl border border-cyan-400/20 bg-cyan-400/5 px-8 py-16 text-center">
            <h2 className="text-3xl font-bold sm:text-4xl">
              Ready to make your learning plan adaptive?
            </h2>

            <p className="mx-auto mt-4 max-w-2xl leading-7 text-slate-400">
              Build a roadmap that adjusts with you instead of forcing you to
              follow a fixed schedule.
            </p>

            <Link
              to="/tracks"
              className="mt-8 inline-flex rounded-xl bg-cyan-400 px-7 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              Start Your Learning Journey
            </Link>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-slate-800 px-6 py-8 lg:px-12">
          <div className="mx-auto flex max-w-7xl flex-col gap-3 text-center text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:text-left">
            <p>© 2026 SkillSprint AI</p>

            <p>
              Adaptive Learning Coach powered by Computational Intelligence
            </p>
          </div>
        </footer>
      </main>
    </>
  )
}

export default LandingPage