import React from 'react';
import Link from 'next/link';
import { Brain, ArrowLeft, Terminal, Bot } from 'lucide-react';
import AppShell from '@/components/layout/AppShell';

export default function ReasoningPlaceholder() {
  return (
    <AppShell>
      <div className="p-6 max-w-[800px] mx-auto flex flex-col gap-6 my-12 animate-fade-in">
        {/* Page Header */}
        <div className="flex items-center gap-3 border-b border-[var(--color-border)] pb-4 shrink-0">
          <div className="p-2 bg-[var(--color-primary-muted)] text-[var(--color-primary)] rounded">
            <Brain className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-xl font-bold tracking-tight text-sip-text-primary">
              Reasoning Assistant
            </h1>
            <span className="text-[10px] uppercase tracking-wider font-bold text-[var(--color-primary)]">
              Reserved for Stage 3
            </span>
          </div>
        </div>

        {/* Info box */}
        <div className="bg-sip-surface border border-[var(--color-border)] rounded-lg p-6 flex flex-col gap-4">
          <h2 className="text-sm font-bold text-sip-text-primary uppercase tracking-wider">
            Agentic Code Reasoning
          </h2>
          <p className="text-xs text-sip-text-secondary leading-relaxed">
            The Reasoning Assistant introduces LLM-backed logical graph queries. Users will be able to consult an agent about complex refactoring impacts, ask for architectural risk explanations, and generate code corrections.
          </p>

          <div className="grid grid-cols-2 gap-4 my-2">
            <div className="p-4 bg-[#161A22]/50 border border-[var(--color-border)] rounded flex flex-col gap-1.5">
              <Bot className="w-4 h-4 text-sip-text-tertiary" />
              <span className="text-xs font-semibold text-sip-text-primary">Interactive Graph Agent</span>
              <span className="text-[10px] text-sip-text-muted">Chat with an agent that understands the codebase structure.</span>
            </div>
            <div className="p-4 bg-[#161A22]/50 border border-[var(--color-border)] rounded flex flex-col gap-1.5">
              <Terminal className="w-4 h-4 text-sip-text-tertiary" />
              <span className="text-xs font-semibold text-sip-text-primary">Explain Boundary Violation</span>
              <span className="text-[10px] text-sip-text-muted">Interactive explainers for boundary leakage and structural risk.</span>
            </div>
          </div>

          <Link
            href="/dashboard"
            className="self-start inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded bg-[#111318] border border-[#222938] text-[#8B95B0] hover:text-[#F0F2F8] hover:bg-[#161A22] transition-colors"
          >
            <ArrowLeft size={13} />
            Back to Dashboard
          </Link>
        </div>
      </div>
    </AppShell>
  );
}
