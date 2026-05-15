import { useState } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'

export default function AnswerKey({ corrige }) {
  const [showModal, setShowModal] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [unlocked, setUnlocked] = useState(false)
  const [checking, setChecking] = useState(false)

  async function handleVerify() {
    setChecking(true)
    setError('')
    try {
      const res = await axios.post('/api/verify-password', { password })
      if (res.data.valid) {
        setUnlocked(true)
        setShowModal(false)
        setPassword('')
      } else {
        setError('Mot de passe incorrect.')
      }
    } catch {
      setError('Erreur de connexion.')
    } finally {
      setChecking(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleVerify()
  }

  if (unlocked) {
    return (
      <div className="card">
        <div className="corrige-banner">
          🔓 Corrigé — réservé aux parents et enseignants
        </div>
        <div className="exam-content">
          <ReactMarkdown>{corrige}</ReactMarkdown>
        </div>
        <div className="btn-row no-print">
          <button className="btn btn-outline btn-sm" onClick={() => setUnlocked(false)}>
            🔒 Masquer le corrigé
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="no-print" style={{ textAlign: 'center', marginTop: '0.5rem' }}>
        <button
          className="btn btn-success"
          onClick={() => { setShowModal(true); setError(''); setPassword('') }}
        >
          🔑 Voir le corrigé (parent / enseignant)
        </button>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>🔒 Accès protégé</h3>
            <p>Entrez le mot de passe parent pour afficher le corrigé.</p>
            <input
              type="password"
              placeholder="Mot de passe"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus
            />
            {error && <div className="error-msg">{error}</div>}
            <div className="modal-buttons">
              <button
                className="btn btn-primary"
                onClick={handleVerify}
                disabled={checking || !password}
                style={{ flex: 1 }}
              >
                {checking ? 'Vérification…' : 'Confirmer'}
              </button>
              <button
                className="btn btn-outline"
                onClick={() => setShowModal(false)}
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
