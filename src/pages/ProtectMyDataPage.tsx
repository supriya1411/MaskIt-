import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Shield,
  ShieldCheck,
  Globe,
  Plus,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';
import { useProtectionStore } from '../stores/protectionStore';
import { ErrorBanner } from '../components/common/ErrorBanner';

export const ProtectMyDataPage: React.FC = () => {
  const [domainInput, setDomainInput] = useState('youtube.com');
  const [validationError, setValidationError] = useState('');
  const {
    sites,
    isActionLoading,
    error,
    successMessage,
    protectSite,
    fetchSites,
    clearFeedback,
  } = useProtectionStore();
  const navigate = useNavigate();

  const commonDomains = ['youtube.com', 'tiktok.com', 'reddit.com', 'amazon.com', 'twitter.com', 'meta.com'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError('');
    clearFeedback();

    let cleaned = domainInput.trim().toLowerCase();
    if (cleaned.includes('://')) {
      try {
        cleaned = new URL(cleaned).hostname;
      } catch (err) {
        setValidationError('Invalid URL or domain format.');
        return;
      }
    }
    if (cleaned.includes('/')) cleaned = cleaned.split('/')[0];
    if (cleaned.includes(':')) cleaned = cleaned.split(':')[0];

    const domainRegex = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$/;
    if (!domainRegex.test(cleaned) && cleaned !== 'localhost') {
      setValidationError("Please enter a valid domain (e.g. 'youtube.com').");
      return;
    }

    const ok = await protectSite(cleaned);
    if (ok) {
      setDomainInput('');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header Card */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-blue-600" />
            <span>Configure Domain Protection</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Add target websites to intercept and virtualize hardware and browser fingerprinting probes
          </p>
        </div>

        {error && <ErrorBanner message={error} onRetry={fetchSites} />}
        {successMessage && (
          <div className="p-3.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2.5">
          <div className="relative flex-1">
            <Globe className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
            <input
              type="text"
              required
              value={domainInput}
              onChange={(e) => setDomainInput(e.target.value)}
              placeholder="Enter domain (e.g. youtube.com)"
              className="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={isActionLoading}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs rounded-lg shadow-sm transition-colors disabled:opacity-50 flex items-center justify-center space-x-1.5 shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>{isActionLoading ? 'Saving...' : 'Protect Domain'}</span>
          </button>
        </form>

        {validationError && (
          <p className="text-xs text-rose-600 flex items-center space-x-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>{validationError}</span>
          </p>
        )}

        {/* Popular chips */}
        <div className="space-y-1.5 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
          <span className="text-slate-500 font-medium block">Quick Add Popular Sites:</span>
          <div className="flex flex-wrap gap-1.5">
            {commonDomains.map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => {
                  setDomainInput(d);
                  protectSite(d);
                }}
                className="px-2.5 py-1 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-950 hover:text-blue-600 transition-colors text-xs"
              >
                + {d}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Action footer link to protected sites */}
      <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs">
        <span className="text-slate-600 dark:text-slate-400">
          Currently protecting <span className="font-semibold text-slate-900 dark:text-white">{sites.length}</span> websites.
        </span>
        <button
          onClick={() => navigate('/sites')}
          className="text-blue-600 dark:text-blue-400 font-medium hover:underline flex items-center space-x-1"
        >
          <span>View Protected Sites Table</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
