'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Compass, Cpu, HelpCircle, Network, Clock, Brain } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#090B10] text-[#F0F2F8] flex flex-col items-center justify-center p-6 text-center">
      <div className="max-w-md flex flex-col items-center">
        {/* Monospace 404 */}
        <span className="font-mono text-7xl font-extrabold tracking-widest text-[#4F7CFF] opacity-80 mb-2 select-none">
          404
        </span>
        <h1 className="text-xl font-bold mb-2">Page Not Found</h1>
        <p className="text-xs text-[#8B95B0] leading-relaxed mb-8 max-w-sm">
          The requested coordinate does not exist. It may be designated for deployment in a future release stage of the Software Intelligence Operating System.
        </p>

        {/* Buttons */}
        <div className="flex flex-wrap gap-3 mb-10 justify-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded bg-[#4F7CFF] text-white hover:bg-[#4F7CFF]/90 transition-all duration-150"
          >
            <ArrowLeft size={13} />
            Go to Dashboard
          </Link>
          <Link
            href="/capabilities"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded bg-[#111318] border border-[#222938] text-[#8B95B0] hover:text-[#F0F2F8] hover:bg-[#161A22] transition-all duration-150"
          >
            <Compass size={13} />
            Explore Capabilities
          </Link>
        </div>

        {/* Future roadmap links */}
        <div className="w-full border-t border-[#222938] pt-6 text-left">
          <h3 className="text-[10px] font-bold text-[#5A6480] uppercase tracking-widest mb-4">
            System Evolution Roadmap
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-[#111318]/50 border border-[#222938]/60 rounded-lg opacity-60">
              <div className="flex items-center gap-2 mb-1">
                <Network size={14} className="text-[#8B5CF6]" />
                <span className="text-xs font-bold text-[#F0F2F8]">Architecture</span>
              </div>
              <span className="text-[10px] text-[#8B95B0] block">Stage 2 Studio</span>
            </div>

            <div className="p-3 bg-[#111318]/50 border border-[#222938]/60 rounded-lg opacity-60">
              <div className="flex items-center gap-2 mb-1">
                <Compass size={14} className="text-[#22C55E]" />
                <span className="text-xs font-bold text-[#F0F2F8]">Decisions</span>
              </div>
              <span className="text-[10px] text-[#8B95B0] block">Stage 2 Registry</span>
            </div>

            <div className="p-3 bg-[#111318]/50 border border-[#222938]/60 rounded-lg opacity-60">
              <div className="flex items-center gap-2 mb-1">
                <Brain size={14} className="text-[#EF4444]" />
                <span className="text-xs font-bold text-[#F0F2F8]">Reasoning</span>
              </div>
              <span className="text-[10px] text-[#8B95B0] block">Stage 3 Assistant</span>
            </div>

            <div className="p-3 bg-[#111318]/50 border border-[#222938]/60 rounded-lg opacity-60">
              <div className="flex items-center gap-2 mb-1">
                <Clock size={14} className="text-[#06B6D4]" />
                <span className="text-xs font-bold text-[#F0F2F8]">Timeline</span>
              </div>
              <span className="text-[10px] text-[#8B95B0] block">Stage 3 Time Machine</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
