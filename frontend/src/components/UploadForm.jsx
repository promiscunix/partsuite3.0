import React, { useRef, useState } from 'react'
import axios from 'axios'

export default function UploadForm({ apiBase, onUploaded }) {
  const fileRef = useRef()
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    const files = fileRef.current.files
    if (!files.length) return
    const form = new FormData()
    Array.from(files).forEach((f) => form.append('files', f))
    setBusy(true)
    setMessage('')
    try {
      await axios.post(`${apiBase}/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setMessage('Uploaded and parsed!')
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
        <input type="file" accept="application/pdf" multiple ref={fileRef} />
        <button className="primary" type="submit" disabled={busy}>
          {busy ? 'Processing…' : 'Upload'}
        </button>
      </form>
      {message && <p className="muted">{message}</p>}
    </section>
  )
}
