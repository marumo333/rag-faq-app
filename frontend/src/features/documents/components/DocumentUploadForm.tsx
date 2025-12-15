'use client'

import { useState } from 'react'
import { useDocumentUpload } from '@/features/documents/hooks/useDocumentUpload'
import { Button } from '@/shared/components/Button'

interface DocumentUploadFormProps {
  onUploaded?: (message: string) => void
}

export function DocumentUploadForm({ onUploaded }: DocumentUploadFormProps) {
  const [file, setFile] = useState<File | null>(null)
  const { uploading, error, result, handleUpload } = useDocumentUpload()

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!file) return
    try {
      const res = await handleUpload(file)
      onUploaded?.(res.message)
    } catch (err) {
      console.error('upload failed', err)
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          disabled={uploading}
        />
      </div>
      {error && (
        <p className="text-sm text-red-600">{error.message}</p>
      )}
      {result && (
        <p className="text-sm text-green-700">{result.message}</p>
      )}
      <Button type="submit" disabled={uploading || !file}>
        {uploading ? 'アップロード中...' : 'PDFをアップロード'}
      </Button>
    </form>
  )
}
