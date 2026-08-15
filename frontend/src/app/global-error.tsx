'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body className="bg-slate-950 text-slate-100 flex flex-col items-center justify-center min-h-screen p-6 text-center">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full shadow-2xl space-y-4">
          <h2 className="text-xl font-bold text-slate-100">Global System Error</h2>
          <p className="text-sm text-slate-400">
            {error?.message || 'A critical rendering error occurred.'}
          </p>
          <button
            onClick={() => reset()}
            className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-2 px-4 rounded-lg text-sm transition-colors"
          >
            Reload Application
          </button>
        </div>
      </body>
    </html>
  );
}
