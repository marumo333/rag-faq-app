"use client";

import { useState, useEffect } from "react";

import { authService, supabase } from "../services/authService";
import { User } from "../type";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // 初期セッション確認
    void checkUser();

    // 認証状態の変更を監視
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        const roleValue =
          typeof session.user.user_metadata?.role === "string"
            ? session.user.user_metadata.role
            : undefined;

        setUser({
          id: session.user.id,
          email: session.user.email || "",
          role: roleValue,
        });
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  async function checkUser() {
    try {
      const currentUser = await authService.getUser();
      if (currentUser) {
        const roleValue =
          typeof currentUser.user_metadata?.role === "string"
            ? currentUser.user_metadata.role
            : undefined;
        setUser({
          id: currentUser.id,
          email: currentUser.email || "",
          role: roleValue,
        });
      }
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }

  async function signIn(email: string, password: string) {
    setLoading(true);
    setError(null);
    try {
      await authService.signIn(email, password);
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function signOut() {
    setLoading(true);
    try {
      await authService.signOut();
      setUser(null);
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return {
    user,
    loading,
    error,
    signIn,
    signOut,
    isAuthenticated: !!user,
  };
}
