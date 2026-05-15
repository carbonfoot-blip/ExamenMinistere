import { useState } from 'react'
import axios from 'axios'
import ExamSelector from './components/ExamSelector'
import ExamDisplay from './components/ExamDisplay'

export default function App() {
  const [state, setState] = useState('idle') // idle | loading | done | error
  const [exam, setExam] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')

  async function handleGenerate(niveau, type_examen, difficulte) {
    setState('loading')
    setErrorMsg('')
    try {
      const res = await axios.post('/api/generate', { niveau, type_examen, difficulte })
      setExam({ ...res.data, meta: { niveau, type_examen, difficulte } })
      setState('done')
    } catch (e) {
      setErrorMsg(e?.response?.data?.detail || 'Une erreur est survenue. Réessaie.')
      setState('error')
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📝 Examens ministériels</h1>
        <p>Générateur d'examens pour élèves du primaire — propulsé par l'intelligence artificielle</p>
      </header>

      {(state === 'idle' || state === 'loading' || state === 'error') && (
        <ExamSelector onGenerate={handleGenerate} loading={state === 'loading'} />
      )}

      {state === 'loading' && (
        <div className="card">
          <div className="loading-wrapper">
            <div className="spinner" />
            <p>Génération de l'examen en cours…</p>
            <p style={{ fontSize: '0.85rem', color: 'var(--gray-400)' }}>
              Cela peut prendre 15 à 30 secondes.
            </p>
          </div>
        </div>
      )}

      {state === 'error' && (
        <div className="card" style={{ borderLeft: '4px solid var(--red)' }}>
          <p style={{ color: 'var(--red)', fontWeight: 600 }}>⚠️ {errorMsg}</p>
        </div>
      )}

      {state === 'done' && exam && (
        <ExamDisplay
          examen={exam.examen}
          corrige={exam.corrige}
          meta={exam.meta}
          onReset={() => { setState('idle'); setExam(null) }}
        />
      )}
    </div>
  )
}
