import { useState, useEffect } from 'react'
import { Calendar, ChevronDown, ChevronUp, FastForward, RotateCcw, Wrench } from 'lucide-react'
import { getDemoDate, setDemoDate } from '../../api/client'

function getTodayString() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function addDaysToDateString(baseDate: string, days: number): string {
  const d = new Date(`${baseDate}T12:00:00`)
  d.setDate(d.getDate() + days)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export default function DemoToolbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [simulatedDate, setSimulatedDateState] = useState<string>(
    getDemoDate() || getTodayString()
  )
  const [hasOverride, setHasOverride] = useState<boolean>(Boolean(getDemoDate()))

  useEffect(() => {
    function handleDateChange(e: Event) {
      const customEvent = e as CustomEvent<{ date: string | null }>
      const newDate = customEvent.detail?.date
      if (newDate) {
        setSimulatedDateState(newDate)
        setHasOverride(true)
      } else {
        setSimulatedDateState(getTodayString())
        setHasOverride(false)
      }
    }

    window.addEventListener('skillsprint_date_changed', handleDateChange)
    return () => {
      window.removeEventListener('skillsprint_date_changed', handleDateChange)
    }
  }, [])

  function applyDate(newDate: string | null) {
    if (newDate) {
      setSimulatedDateState(newDate)
      setHasOverride(true)
      setDemoDate(newDate)
    } else {
      const today = getTodayString()
      setSimulatedDateState(today)
      setHasOverride(false)
      setDemoDate(null)
    }
  }

  function handleFastForward(days: number) {
    const next = addDaysToDateString(simulatedDate, days)
    applyDate(next)
  }

  return (
    <div className="fixed bottom-4 right-4 z-40 max-w-sm font-sans">
      {!isOpen ? (
        <button
          onClick={() => setIsOpen(true)}
          className={`flex items-center gap-2 rounded-full border px-4 py-2 text-xs font-semibold shadow-2xl transition ${
            hasOverride
              ? 'border-amber-400 bg-amber-400 text-slate-950 hover:bg-amber-300'
              : 'border-slate-700 bg-slate-900/95 text-slate-300 backdrop-blur-md hover:border-cyan-400 hover:text-white'
          }`}
          title="Open Demo Date Override Toolbar"
        >
          <Wrench size={14} className={hasOverride ? 'animate-bounce' : 'text-cyan-400'} />
          <span>
            {hasOverride ? `🧪 Simulating: ${simulatedDate}` : '🧪 Demo Date Toolbar'}
          </span>
          <ChevronUp size={14} />
        </button>
      ) : (
        <div className="rounded-2xl border border-slate-700 bg-slate-900/95 p-4 shadow-2xl backdrop-blur-md">
          {/* Header */}
          <div className="flex items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2 text-cyan-400">
              <Calendar size={16} />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Demo Date Simulator
              </span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
              title="Minimize Toolbar"
            >
              <ChevronDown size={16} />
            </button>
          </div>

          <p className="mt-2 text-[11px] leading-relaxed text-slate-400">
            Fast-forward simulated time to demonstrate multi-day task flow, overdue detection,
            adaptive replanning, and weekly reflections.
          </p>

          {/* Date Picker Input */}
          <div className="mt-3">
            <label htmlFor="demo-date-input" className="block text-[11px] font-semibold text-slate-300">
              Simulated Date (?date=YYYY-MM-DD):
            </label>
            <input
              id="demo-date-input"
              type="date"
              value={simulatedDate}
              onChange={(e) => applyDate(e.target.value)}
              className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-white outline-none focus:border-cyan-400"
            />
          </div>

          {/* Quick Increment Buttons */}
          <div className="mt-3 flex flex-wrap gap-1.5">
            <button
              type="button"
              onClick={() => handleFastForward(1)}
              className="flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 text-[11px] font-semibold text-slate-200 hover:border-cyan-400 hover:text-cyan-300"
            >
              <FastForward size={11} /> +1 Day
            </button>
            <button
              type="button"
              onClick={() => handleFastForward(3)}
              className="flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 text-[11px] font-semibold text-slate-200 hover:border-cyan-400 hover:text-cyan-300"
            >
              <FastForward size={11} /> +3 Days
            </button>
            <button
              type="button"
              onClick={() => handleFastForward(7)}
              className="flex items-center gap-1 rounded-lg border border-cyan-400/30 bg-cyan-400/10 px-2.5 py-1 text-[11px] font-semibold text-cyan-300 hover:bg-cyan-400/20"
              title="Fast forward one full week (triggers Weekly Reflection if due)"
            >
              <FastForward size={11} /> +7 Days (Week)
            </button>
          </div>

          {/* Reset / Live Date Button */}
          {hasOverride && (
            <div className="mt-3 border-t border-slate-800 pt-2.5">
              <button
                type="button"
                onClick={() => applyDate(null)}
                className="flex w-full items-center justify-center gap-1.5 rounded-lg border border-amber-400/30 bg-amber-400/10 py-1.5 text-[11px] font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-400/20"
              >
                <RotateCcw size={12} /> Reset to Real-World Today
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

