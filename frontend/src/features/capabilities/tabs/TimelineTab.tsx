'use client';

import React from 'react';
import { GitCommit, Clock, AlertCircle } from 'lucide-react';
import { useCapabilityTimeline } from '@/hooks/useCapabilities';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { formatDate } from '@/lib/utils';

interface TimelineTabProps {
  capabilityId: string;
}

export default function TimelineTab({ capabilityId }: TimelineTabProps) {
  const { data, isLoading, isError } = useCapabilityTimeline(capabilityId);

  const timelineEntries = data?.timeline ?? [];

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 gap-3 min-h-[300px]">
        <LoadingSpinner size="md" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Retrieving Ingest Logs...
        </span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <span className="text-xl mb-2">⚠️</span>
        <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
          History Unavailable
        </h4>
        <p className="text-xs text-sip-text-secondary max-w-sm">
          Failed to fetch evolution timeline for this capability.
        </p>
      </div>
    );
  }

  if (timelineEntries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-[var(--color-border)] bg-sip-surface/10 rounded-lg">
        <AlertCircle className="w-8 h-8 text-sip-text-tertiary mb-2" />
        <h4 className="text-xs font-semibold text-sip-text-primary">No History Found</h4>
        <p className="text-[11px] text-sip-text-secondary mt-1 max-w-[240px]">
          This capability has not recorded any version changes or is in initial stage.
        </p>
      </div>
    );
  }

  // Sort timeline entries desc by timestamp
  const sortedTimeline = [...timelineEntries].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <div className="flex flex-col p-2 animate-fade-in max-h-[500px] overflow-y-auto">
      <div className="relative border-l-2 border-[var(--color-border)] ml-3 pl-6 flex flex-col gap-6">
        {sortedTimeline.map((entry, idx) => {
          const formattedDate = formatDate(entry.timestamp);
          const shortHash = entry.commit_hash ? entry.commit_hash.slice(0, 7) : 'Initial';

          return (
            <div key={idx} className="relative">
              {/* Timeline marker */}
              <div className="absolute -left-[31px] top-1 flex items-center justify-center w-5 h-5 rounded-full bg-[#111318] border-2 border-[var(--color-primary)] text-[var(--color-primary)] shadow-sm">
                <GitCommit className="w-3.5 h-3.5" />
              </div>

              {/* Box */}
              <div className="bg-sip-surface/40 border border-[var(--color-border)] rounded-lg p-4 flex flex-col gap-3">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--color-border)]/40 pb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-sip-text-primary font-mono bg-sip-surface border border-[var(--color-border)] px-2 py-0.5 rounded uppercase tracking-wider">
                      commit: {shortHash}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[11px] text-sip-text-secondary">
                    <Clock className="w-3.5 h-3.5 text-sip-text-tertiary" />
                    <span>{formattedDate}</span>
                  </div>
                </div>

                {/* Features detail */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-[10px] text-sip-text-tertiary font-bold uppercase tracking-wider">
                    Extracted Attributes
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {entry.features && Object.keys(entry.features).length > 0 ? (
                      Object.entries(entry.features).map(([key, val]) => (
                        <div
                          key={key}
                          className="flex items-center text-[10px] bg-sip-surface border border-[var(--color-border)]/50 rounded font-mono px-2 py-0.5"
                        >
                          <span className="text-sip-text-tertiary mr-1">{key}:</span>
                          <span className="text-sip-text-primary font-semibold truncate max-w-[150px]">
                            {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                          </span>
                        </div>
                      ))
                    ) : (
                      <span className="text-xs text-sip-text-muted italic">No attribute changes detected.</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
