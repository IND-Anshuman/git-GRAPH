'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { ShieldAlert, RefreshCw, LayoutDashboard } from 'lucide-react';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error('Next.js Global Boundary Caught Error:', error);
  }, [error]);

  const isDev = process.env.NODE_ENV === 'development';

  return (
    <div className="min-h-screen bg-[#090B10] text-[#F0F2F8] flex flex-col items-center justify-center p-6 text-center">
      <div className="max-w-md flex flex-col items-center">
        {/* Warning Icon */}
        <div className="p-3 bg-[#EF4444]/10 text-[#EF4444] rounded-full mb-4 border border-[#EF4444]/20 animate-pulse">
          <ShieldAlert className="w-8 h-8" />
        </div>

        <h1 className="text-xl font-bold mb-2">Application Error</h1>
        <p className="text-xs text-[#8B95B0] leading-relaxed mb-6 max-w-sm">
          A runtime execution error occurred inside the system view. The transaction has been rolled back safely.
        </p>

        {/* Dev details */}
        {isDev && (
          <div className="w-full text-left bg-[#111318] border border-[#222938] rounded-lg p-4 mb-6 max-h-[160px] overflow-auto">
            <span className="text-[10px] font-bold text-[#5A6480] uppercase tracking-widest block mb-2">
              Diagnostics (Development Mode Only)
            </span>
            <pre className="text-[10px] font-mono text-[#EF4444] whitespace-pre-wrap break-all leading-normal">
              {error.message || error.toString()}
            </pre>
            {error.stack && (
              <pre className="text-[9px] font-mono text-[#8B95B0] whitespace-pre-wrap break-all mt-2 leading-tight">
                {error.stack}
              </pre>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-3 justify-center">
          <button
            onClick={() => reset()}
            type="button"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded bg-[#4F7CFF] text-white hover:bg-[#4F7CFF]/90 transition-all duration-150"
          >
            <RefreshCw size={13} />
            Try Again
          </button>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded bg-[#111318] border border-[#222938] text-[#8B95B0] hover:text-[#F0F2F8] hover:bg-[#161A22] transition-all duration-150"
          >
            <LayoutDashboard size={13} />
            Go to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
