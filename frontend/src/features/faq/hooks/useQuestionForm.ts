import { useState, type FormEvent } from 'react'

interface UseQuestionFormParams {
  onSubmit: (question: string) => void
}

export function useQuestionForm({ onSubmit }: UseQuestionFormParams) {
  const [question, setQuestion] = useState('')

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (question.trim()) {
      onSubmit(question)
    }
  }

  return {
    question,
    setQuestion,
    handleSubmit,
  }
}
