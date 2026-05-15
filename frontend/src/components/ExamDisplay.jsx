import ReactMarkdown from 'react-markdown'
import AnswerKey from './AnswerKey'

export default function ExamDisplay({ examen, corrige, meta, onReset }) {
  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--gray-200)' }}>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span className="badge badge-blue">{meta.niveau}</span>
            <span className="badge badge-blue">{meta.type_examen.replace('-', ' — ')}</span>
            <span className="badge badge-blue">Difficulté {meta.difficulte}/10</span>
          </div>
          <div className="btn-row no-print" style={{ margin: 0 }}>
            <button className="btn btn-outline btn-sm" onClick={() => window.print()}>
              🖨️ Imprimer
            </button>
            <button className="btn btn-outline btn-sm" onClick={onReset}>
              ← Nouvel examen
            </button>
          </div>
        </div>

        <div className="exam-content">
          <ReactMarkdown>{examen}</ReactMarkdown>
        </div>
      </div>

      <AnswerKey corrige={corrige} />
    </div>
  )
}
