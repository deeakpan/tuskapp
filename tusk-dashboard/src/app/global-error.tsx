"use client";

import "./globals.css";

export default function GlobalError({ error, retry }: { error: Error & { digest?: string }; retry: () => void }) {
  return (
    <html lang="en">
      <head>
        <title>Something went wrong · TuskApp</title>
        <meta name="description" content="TuskApp hit an unexpected error. Try again in a moment." />
      </head>
      <body className="flex min-h-screen items-center justify-center p-6 font-sans">
        <div className="max-w-md">
          <h1 className="text-3xl tracking-tight">Something went wrong</h1>
          <p className="mt-3 text-muted">TuskApp hit an unexpected error. Your data is safe.</p>
          {error.digest && <p className="mt-2 font-mono text-xs text-faint">Error ID {error.digest}</p>}
          <button
            type="button"
            onClick={retry}
            className="mt-6 h-9 rounded-full bg-ink px-4 text-sm text-bg"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
