"use client";

import { useState, type FormEvent } from "react";

import { useRouter } from "next/navigation";

import { useAuth } from "./useAuth";

interface UseLoginFormParams {
  email: string;
  password: string;
}

export function useLoginForm({ email, password }: UseLoginFormParams) {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const { signIn } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage("");

    try {
      await signIn(email, password);
      router.push("/faq"); // FAQ画面に遷移
    } catch (error) {
      setErrorMessage(
        "ログインに失敗しました。メールアドレスとパスワードを確認してください。",
      );
      console.error("Login error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    errorMessage,
    handleSubmit,
  };
}
