const EXAM_LABELS = {
  "MATH-QUESTIONNAIRE": "Mathématique — Questionnaire",
  "MATH-C1": "Mathématique — Compétence 1",
  "MATH-C2": "Mathématique — Compétence 2",
  "LECTURE-NARRATIF": "Lecture — Texte narratif",
  "LECTURE-INFORMATIF": "Lecture — Texte informatif",
}

export default function ExamSelector({ onGenerate, loading }) {
  const niveau = "Primaire 6e"
  const examTypes = Object.keys(EXAM_LABELS)

  return (
    <div className="card">
      <h2>Configurer l'examen</h2>

      <div className="form-grid">
        <div className="form-group">
          <label>Niveau</label>
          <select disabled value={niveau}>
            <option>Primaire 6e</option>
          </select>
        </div>

        <div className="form-group">
          <label>Type d'examen</label>
          <select id="exam-type">
            {examTypes.map(t => (
              <option key={t} value={t}>{EXAM_LABELS[t]}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="difficulty-row">
        <label htmlFor="difficulty">Difficulté</label>
        <input
          id="difficulty"
          type="range"
          min="1"
          max="10"
          defaultValue="5"
          style={{ flex: 1 }}
          onInput={e => {
            document.getElementById('diff-badge').textContent = e.target.value
          }}
        />
        <span className="difficulty-badge" id="diff-badge">5</span>
        <span style={{ fontSize: '0.82rem', color: 'var(--gray-600)' }}>/10</span>
      </div>

      <button
        className="btn btn-primary"
        disabled={loading}
        onClick={() => {
          const type = document.getElementById('exam-type').value
          const diff = parseInt(document.getElementById('difficulty').value)
          onGenerate(niveau, type, diff)
        }}
      >
        {loading ? (
          <>
            <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
            Génération en cours…
          </>
        ) : (
          <>✨ Générer l'examen</>
        )}
      </button>
    </div>
  )
}
