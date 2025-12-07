import React, { useRef, useState } from 'react'
import axios from 'axios'

export default function UploadForm({ apiBase, onUploaded }) {
  const fileRef = useRef()
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [files, setFiles] = useState([])

  const handleFiles = (fileList) => {
    const pdfs = Array.from(fileList).filter(
      (file) => file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
    )
    if (!pdfs.length) return
    setFiles((prev) => [...prev, ...pdfs])
    setMessage('Ready to upload ' + pdfs.length + ' PDF' + (pdfs.length > 1 ? 's' : ''))
  }

  const onFileInputChange = (event) => {
    handleFiles(event.target.files)
  }

  const onDrop = (event) => {
    event.preventDefault()
    handleFiles(event.dataTransfer.files)
  }

  const clearSelection = () => {
    setFiles([])
    if (fileRef.current) {
      fileRef.current.value = ''
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    if (!files.length) {
      setMessage('Pick or drop at least one PDF to parse.')
      return
    }
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    setBusy(true)
    setMessage('')
    try {
      await axios.post(`${apiBase}/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setMessage('Uploaded and parsed!')
      setFiles([])
      if (fileRef.current) {
        fileRef.current.value = ''
      }
      onUploaded?.()
    } catch (err) {
      setMessage('Upload failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="card">
      <h2>Upload PDFs</h2>
      <form onSubmit={submit} className="upload-form">
        <div
          className="dropzone"
          onDragOver={(e) => e.preventDefault()}
          onDrop={onDrop}
          onClick={() => fileRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              fileRef.current?.click()
            }
          }}
        >
          <p className="dropzone-title">Drag and drop PDFs here</p>
          <p className="muted">…or click to choose files</p>
          <input
            type="file"
            accept="application/pdf"
            multiple
            ref={fileRef}
            onChange={onFileInputChange}
            aria-label="Choose PDF files to upload"
          />
        </div>
        <div className="upload-actions">
          <button className="secondary" type="button" onClick={clearSelection} disabled={!files.length || busy}>
            Clear
          </button>
          <button className="primary" type="submit" disabled={busy}>
            {busy ? 'Processing…' : 'Upload'}
          </button>
        </div>
      </form>
      {files.length > 0 && (
        <ul className="list small">
          {files.map((file, idx) => (
            <li key={`${file.name}-${idx}`} className="muted">
              {file.name}
            </li>
          ))}
        </ul>
      )}
      {message && <p className="muted">{message}</p>}
    </section>
  )
}
