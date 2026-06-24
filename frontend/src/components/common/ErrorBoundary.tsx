'use client';

import React, { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  className?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const isDev = process.env.NODE_ENV === 'development';

      return (
        <div
          className={cn(
            'flex flex-col items-center justify-center p-6 rounded-lg border border-[var(--color-danger)]/30 bg-[var(--color-danger)]/5 w-full text-center',
            this.props.className
          )}
        >
          <div className="p-2 bg-[var(--color-danger)]/10 text-[var(--color-danger)] rounded-full mb-3">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
            Component Error
          </h4>
          <p className="text-xs text-sip-text-secondary max-w-sm mb-4">
            {this.state.error?.message && this.state.error.message.length < 100
              ? this.state.error.message
              : 'An unexpected render error occurred in this workspace view.'}
          </p>

          {isDev && this.state.error && (
            <pre className="text-[10px] text-left text-sip-text-muted bg-[#0e1015] p-3 rounded border border-[var(--color-border)] max-w-full overflow-auto mb-4 font-mono max-h-[120px] w-full">
              {this.state.error.stack || this.state.error.toString()}
            </pre>
          )}

          <button
            onClick={this.handleReset}
            type="button"
            className={cn(
              'inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md text-white bg-[var(--color-danger)]',
              'hover:bg-[var(--color-danger)]/90 transition-all duration-150'
            )}
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
