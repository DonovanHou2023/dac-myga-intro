import React, { useState } from 'react'
import { marked } from 'marked'

export default function App() {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function loadObjectives() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/lessons/01-foundations-review/objectives.md')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const text = await res.text()
      setContent(marked.parse(text || '*No content found in objectives.md*'))
    } catch (err) {
      setError(String(err))
      setContent('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header>
        <h1>DAC MYGA — Lesson 1 Objectives</h1>
      </header>

      <main>
        <div className="controls">
          <button onClick={loadObjectives} className="primary">
            {loading ? 'Loading…' : 'Show Objectives'}
          </button>
        </div>

        {error && <div className="error">Error: {error}</div>}

        <section className="card">
          <div
            className="card-content"
            dangerouslySetInnerHTML={{ __html: content }}
          />
        </section>
      </main>

      <footer>
        <small>Content loaded from `lessons/01-foundations-review/objectives.md`</small>
      </footer>
    </div>
  )
}
