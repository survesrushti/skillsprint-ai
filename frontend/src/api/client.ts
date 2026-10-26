
const API_BASE_URL = 'http://127.0.0.1:5000/api/v1'

let authTokenGetter: (() => Promise<string | null>) | null = null

export function setAuthTokenGetter(getter: () => Promise<string | null>) {
  authTokenGetter = getter
}

let activeDemoDate: string | null =
  typeof window !== 'undefined'
    ? localStorage.getItem('skillsprint_demo_date') || null
    : null

export function getDemoDate(): string | null {
  return activeDemoDate
}

export function setDemoDate(date: string | null) {
  activeDemoDate = date
  if (typeof window !== 'undefined') {
    if (date) {
      localStorage.setItem('skillsprint_demo_date', date)
    } else {
      localStorage.removeItem('skillsprint_demo_date')
    }
    window.dispatchEvent(
      new CustomEvent('skillsprint_date_changed', { detail: { date } })
    )
  }
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const authHeaders: Record<string, string> = {}

  if (authTokenGetter) {
    try {
      const token = await authTokenGetter()
      if (token) {
        authHeaders['Authorization'] = `Bearer ${token}`
      }
    } catch (tokenErr) {
      console.warn('Could not retrieve Clerk auth token:', tokenErr)
    }
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders,
      ...options.headers,
    },
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.message || 'Backend request failed')
  }

  return data as T
}

export function checkBackend() {
  return apiRequest<{ status: string }>('/health')
}

export interface ResourceData {
  id?: number
  topic_id?: number
  title: string
  url: string
  resource_type: string
  estimated_minutes?: number | null
}

export interface TopicResourcesResponse {
  status: string
  topic_id: number
  topic_name: string
  count: number
  resources: ResourceData[]
}

export interface SwapResourceResponse {
  status: string
  message: string
  item_id: number
  resource: ResourceData
}

export interface DailyTask {
  id: number
  day_number: number
  topic_id: number
  topic_name: string
  planned_minutes: number
  scheduled_date: string
  status: string
  resource?: ResourceData | null
  available_resources?: ResourceData[]
}

export interface TodayTasksResponse {
  status: string
  goal_id: number
  current_day: number
  total_days: number
  date: string
  roadmap_id: number
  roadmap_version: number
  plan_status: string
  tasks: DailyTask[]
  overdue_tasks: DailyTask[]
  summary: {
    tasks_total: number
    tasks_completed: number
    planned_minutes_today: number
    completed_minutes_today: number
    overdue_count: number
    overdue_minutes: number
  }
}

export interface ProgressSummaryResponse {
  status: string
  goal_id: number
  roadmap_id: number
  roadmap_version: number
  report_date: string
  start_date: string
  current_day: number
  total_days: number
  summary: {
    total_tasks: number
    completed_tasks: number
    remaining_tasks: number
    completion_percentage: number
    total_planned_minutes: number
    actual_study_minutes: number
  }
  progress: {
    expected_tasks_by_date: number
    completed_tasks_by_date: number
    expected_percentage: number
    actual_percentage: number
    progress_difference: number
  }
  streak: {
    current_streak_days: number
    completed_study_dates: number
  }
}

export function getTodayTasks(
  goalId: number,
  date?: string
) {
  const effectiveDate = date ?? activeDemoDate ?? undefined
  const params = new URLSearchParams({
    goal_id: String(goalId),
  })

  if (effectiveDate) {
    params.set('date', effectiveDate)
  }

  return apiRequest<TodayTasksResponse>(
    `/tasks/today?${params.toString()}`
  )
}

export function getProgressSummary(
  goalId: number,
  date?: string
) {
  const effectiveDate = date ?? activeDemoDate ?? undefined
  const params = new URLSearchParams({
    goal_id: String(goalId),
  })

  if (effectiveDate) {
    params.set('date', effectiveDate)
  }

  return apiRequest<ProgressSummaryResponse>(
    `/progress/summary?${params.toString()}`
  )
}

export function completeTask(taskId: number) {
  return apiRequest<{ status: string; message?: string }>(
    `/tasks/${taskId}/complete`,
    { method: 'POST' }
  )
}

export function skipTask(taskId: number) {
  return apiRequest<{ status: string; message?: string }>(
    `/tasks/${taskId}/skip`,
    { method: 'POST' }
  )
}

export interface RescheduleResponse {
  status: string
  message?: string
  replanned?: boolean
  preview?: boolean
  saved?: boolean
  goal_id?: number
  previous_roadmap_id?: number
  previous_roadmap_version?: number
  roadmap_id?: number | null
  roadmap_version?: number
  date?: string
  current_day?: number
  first_new_day?: number
  completed_tasks_preserved?: number
  tasks_replanned?: number
  plan_end_date?: string
  target_date?: {
    old: string
    new: string
    changed: boolean
  }
  strategy?: string
  warnings?: string[]
  metrics?: {
    progress_ratio?: number
    backlog_minutes?: number
    missed_days?: number
    current_streak?: number
    required_minutes?: number
    available_minutes?: number
    days_remaining?: number
    today_closed?: boolean
  }
  ci?: {
    fuzzy?: unknown
    expert?: {
      selected_strategy?: string
      fired_rules?: unknown
      rationale?: string
      [key: string]: unknown
    }
    adaptation?: {
      daily_capacity?: number
      extend_deadline?: boolean
      [key: string]: unknown
    }
    search?: {
      success?: boolean
      sequence?: number[]
      total_minutes?: number
      daily_capacity?: number
      search_cost?: number
      nodes_expanded?: number
    }
  }
  roadmap?: RoadmapDay[]
}

export function rescheduleRoadmap(
  goalId: number,
  options: {
    date?: string
    preview?: boolean
    force?: boolean
  } = {}
) {
  const effectiveDate = options.date ?? activeDemoDate ?? undefined
  return apiRequest<RescheduleResponse>('/roadmap/reschedule', {
    method: 'POST',
    body: JSON.stringify({
      goal_id: goalId,
      ...options,
      ...(effectiveDate ? { date: effectiveDate } : {}),
    }),
  })
}


export interface RoadmapTask {
  id?: number
  topic_id: number
  name: string
  minutes: number
  difficulty: number
  is_optional: boolean
  status?: string
  resource?: ResourceData | null
}

export interface RoadmapDay {
  day: number
  date?: string
  total_minutes: number
  tasks: RoadmapTask[]
}

export interface RoadmapResponse {
  status: string
  message: string
  roadmap_id?: number
  roadmap_version?: number
  items_saved?: number
  goal: {
    id: number
    track_id: number
    skill_level: string
    study_hours_per_day: number
    target_date: string
    known_topics: string[]
  }
  ci: {
    fuzzy?: unknown
    expert?: {
      selected_strategy?: string
      [key: string]: unknown
    }
    search: {
      success: boolean
      sequence?: number[]
      total_minutes: number
      daily_capacity: number
      total_days: number
      search_cost?: number
      nodes_expanded?: number
    }
  }
  roadmap: RoadmapDay[]
}

export function getActiveRoadmap(goalId: number) {
  return apiRequest<RoadmapResponse>(`/roadmap/active?goal_id=${goalId}`)
}

export function generateRoadmap(goalId: number) {
  return apiRequest<RoadmapResponse>('/roadmap/generate', {
    method: 'POST',
    body: JSON.stringify({ goal_id: goalId }),
  })
}

export interface GoalData {
  id: number
  user_id?: number | null
  track_id: number
  skill_level: string
  study_hours_per_day: number
  target_date: string
  known_topics: string[]
  commitment: boolean
  status: string
}

export interface GoalResponse {
  status: string
  goal: GoalData
}

export function getActiveGoal(trackId?: number, userId?: number) {
  const params = new URLSearchParams()
  if (trackId !== undefined) params.set('track_id', String(trackId))
  if (userId !== undefined) params.set('user_id', String(userId))
  const qs = params.toString() ? `?${params.toString()}` : ''
  return apiRequest<GoalResponse>(`/goals/active${qs}`)
}

export function getGoal(goalId: number) {
  return apiRequest<GoalResponse>(`/goals/${goalId}`)
}

export interface CreateGoalPayload {
  track_id: number
  skill_level: string
  study_hours_per_day: number
  target_date: string
  known_topics?: string[]
  commitment?: boolean
}

export function createGoal(payload: CreateGoalPayload) {
  return apiRequest<GoalResponse>('/goals', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export interface TopicSummary {
  id: number
  name: string
  slug: string
  description?: string
  estimated_minutes: number
  difficulty: number
  priority: number
  is_optional: boolean
  prerequisites?: number[]
}

export interface TrackData {
  id: number
  name: string
  slug: string
  description: string
  is_active: boolean
  topic_count: number
  total_minutes: number
  estimated_duration?: string
  topics: TopicSummary[]
}

export interface TracksResponse {
  status: string
  count: number
  tracks: TrackData[]
}

export interface TrackDetailResponse {
  status: string
  track: TrackData
}

export function getTracks() {
  return apiRequest<TracksResponse>('/tracks')
}

export function getTrackBySlug(slug: string) {
  return apiRequest<TrackDetailResponse>(`/tracks/${slug}`)
}

export function getTopicResources(topicId: number) {
  return apiRequest<TopicResourcesResponse>(`/topics/${topicId}/resources`)
}

export function swapTaskResource(itemId: number, resourceId: number) {
  return apiRequest<SwapResourceResponse>(`/roadmap-items/${itemId}/resource`, {
    method: 'PUT',
    body: JSON.stringify({ resource_id: resourceId }),
  })
}

export interface WeeklyReflectionData {
  id: number
  goal_id: number
  user_id?: number | null
  week_number: number
  study_day: number
  confidence_level: number
  difficulty_rating: number
  notes: string | null
  created_at?: string | null
}

export interface ReflectionStatusResponse {
  status: string
  goal_id: number
  current_day: number
  week_number: number
  is_due: boolean
  submitted: boolean
  should_prompt: boolean
  reflection?: WeeklyReflectionData | null
}

export function submitWeeklyReflection(data: {
  goal_id: number
  week_number?: number
  study_day?: number
  confidence_level: number
  difficulty_rating: number
  notes?: string
}) {
  return apiRequest<{
    status: string
    message: string
    reflection: WeeklyReflectionData
  }>('/reflections', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function getWeeklyReflections(goalId: number) {
  return apiRequest<{
    status: string
    count: number
    reflections: WeeklyReflectionData[]
  }>(`/reflections?goal_id=${goalId}`)
}

export function getWeeklyReflectionStatus(goalId: number, day?: number) {
  const params = new URLSearchParams({
    goal_id: String(goalId),
  })
  if (day !== undefined) {
    params.set('day', String(day))
  }
  return apiRequest<ReflectionStatusResponse>(
    `/reflections/status?${params.toString()}`
  )
}

