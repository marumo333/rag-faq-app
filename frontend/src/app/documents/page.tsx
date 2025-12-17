"use client";

import { useEffect } from "react";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAuth } from "@/features/auth/hooks/useAuth";
import { DocumentUploadForm } from "@/features/documents/components/DocumentUploadForm";

export default function DocumentsPage() {
  const { user, loading, signOut } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <p>読み込み中...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-semibold text-black bg-white rounded-md px-2 py-1">
              RAG FAQ
            </span>
          </div>
          <nav className="flex items-center gap-4 text-sm">
            <Link href="/faq" className="text-gray-300 hover:text-white">
              FAQ
            </Link>
            <span className="text-white font-semibold">Documents</span>
            <span className="ml-4 text-gray-400 hidden sm:inline">
              {user.email}
            </span>
            <button
              onClick={() => signOut()}
              className="ml-2 px-3 py-1.5 rounded-md border border-gray-700 text-xs sm:text-sm text-gray-200 hover:bg-gray-800"
            >
              ログアウト
            </button>
          </nav>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center">
        <div className="w-full max-w-3xl px-4 py-10">
          <h1 className="text-2xl font-semibold mb-4">
            ドキュメントアップロード
          </h1>
          <p className="text-sm text-gray-400 mb-6">
            FAQ 検索に利用する PDF ドキュメントをアップロードします。
          </p>
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 shadow">
            <DocumentUploadForm />
          </div>
        </div>
      </main>
    </div>
  );
}
