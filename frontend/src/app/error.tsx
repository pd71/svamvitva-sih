'use client';

import { useEffect } from 'react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Unhandled Application Error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 text-center">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full shadow-2xl space-y-4">
        <div className="w-16 h-16 bg-rose-500/10 text-rose-400 rounded-full flex items-center justify-center mx-auto border border-rose-500/20 text-2xl font-bold">
          !
        </div>
        <h2 className="text-xl font-bold text-slate-100">Application Error</h2>
        <p className="text-sm text-slate-400">
          {error?.message || 'An unexpected rendering error occurred in the dashboard interface.'}
        </p>
        <div className="flex gap-3 pt-2">
          <button
            onClick={() => reset()}
            className="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-2 px-4 rounded-lg text-sm transition-colors"
          >
            Try Again
          </button>
          <Link
            href="/"
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium py-2 px-4 rounded-lg text-sm transition-colors block text-center"
          >
            Home
          </Link>
        </div>
      </div>
    </div>
  );
}
