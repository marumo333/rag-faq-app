import { useState } from 'react'
import { documentService } from '../services/documentService'
import { UploadResponse } from '../type'

export function useDocumentUpload() {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [result, setResult] = useState<UploadResponse | null>(null)

  const handleUpload = async (file: File) => {
    setUploading(true)
    setError(null)

    try {
      const res = await documentService.upload(file)
      setResult(res)
      return res
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setUploading(false)
    }
  }

  return {
    uploading,
    error,
    result,
    handleUpload,
  }
}
