"use client";

import { useState } from "react";

import { authService } from "../services/authService";

interface SignUpInput {
  email: string;
  password: string;
  companyName: string;
  fullName?: string;
}

interface UseTenantRegisterOptions {
  onSuccess?: () => void;
}

export function useTenantRegister(options: UseTenantRegisterOptions = {}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  async function signUpTenant(input: SignUpInput) {
    setLoading(true);
    setError(null);

    try {
      await authService.signUp(input.email, input.password, {
        companyName: input.companyName,
        fullName: input.fullName,
      });
      options.onSuccess?.();
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return {
    signUpTenant,
    loading,
    error,
  };
}
