const API_BASE_URL = 'http://127.0.0.1:5000/api/v1'

export async function checkBackend() {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error('Backend request failed')
  }

  return response.json()
}