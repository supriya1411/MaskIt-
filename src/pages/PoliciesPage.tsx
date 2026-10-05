import React, { useEffect, useState } from 'react';
import {
  Sliders,
  CheckCircle2,
  RefreshCw,
  Save,
  Shield,
} from 'lucide-react';
import { usePolicyStore } from '../stores/policyStore';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorBanner } from '../components/common/ErrorBanner';

export const PoliciesPage: React.FC = () => {
  const { policies, activePolicy, isLoading, isSaving, error, successMessage, fetchPolicies, updatePolicy, clearFeedback } = usePolicyStore();

  const [enabled, setEnabled] = useState(true);
  const [strength, setStrength] = useState<'LOW' | 'BALANCED' | 'AGGRESSIVE' | 'STEALTH'>('BALANCED');
  const [strategy, setStrategy] = useState<'STATIC' | 'DISTRIBUTION_SAMPLED' | 'AI_GENERATED'>('DISTRIBUTION_SAMPLED');
  const [rules, setRules] = useState({
    mask_canvas: true,
    mask_webgl: true,
    mask_navigator: true,
    mask_screen: true,
    mask_timezone: true,
    mask_audio: true,
  });

  useEffect(() => {
    fetchPolicies();
  }, []);

  useEffect(() => {
    if (activePolicy) {
      setEnabled(activePolicy.enabled);
      setStrength(activePolicy.masking_strength as any);
      setStrategy(activePolicy.strategy as any);
      if (activePolicy.rules_json) {
        setRules({
          mask_canvas: !!activePolicy.rules_json.mask_canvas,
          mask_webgl: !!activePolicy.rules_json.mask_webgl,
          mask_navigator: !!activePolicy.rules_json.mask_navigator,
          mask_screen: !!activePolicy.rules_json.mask_screen,
          mask_timezone: !!activePolicy.rules_json.mask_timezone,
          mask_audio: !!activePolicy.rules_json.mask_audio,
        });
      }
    }
  }, [activePolicy]);

  const handleSave = async () => {
    if (!activePolicy) return;
    clearFeedback();

    await updatePolicy(activePolicy.id, {
      enabled,
      masking_strength: strength,
      strategy,
      rules_json: rules,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-blue-600" />
            <span>Fingerprint Masking Policies</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure virtualization strategies applied across protected websites
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving || !activePolicy}
          className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs rounded-lg shadow-sm transition-colors disabled:opacity-50 flex items-center space-x-1.5"
        >
          {isSaving ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Saving...</span>
            </>
          ) : (
            <>
              <Save className="w-3.5 h-3.5" />
              <span>Save Changes</span>
            </>
          )}
        </button>
      </div>

      {error && <ErrorBanner message={error} onRetry={fetchPolicies} />}
      {successMessage && (
        <div className="p-3.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {isLoading ? (
        <LoadingSkeleton rows={3} height="h-28" />
      ) : (
        <div className="space-y-6">
          {/* Master Protection Toggle */}
          <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
                Global Masking Status
              </h3>
              <p className="text-xs text-slate-500">
                Turn on or pause client-side fingerprint virtualization across all sites
              </p>
            </div>

            <button
              onClick={() => setEnabled(!enabled)}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${
                enabled
                  ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
              }`}
            >
              {enabled ? 'Enabled' : 'Paused'}
            </button>
          </div>

          {/* Strategy Selection */}
          <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
              Virtualization Strategy
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {[
                { id: 'STATIC', title: 'Static Profile', desc: 'Aligns hardware parameters to a standard high-population profile.' },
                { id: 'DISTRIBUTION_SAMPLED', title: 'Sampled Cohort', desc: 'Deterministically samples from authentic browser distribution sets.' },
                { id: 'AI_GENERATED', title: 'Adaptive Noise', desc: 'Injects micro-noise into Canvas and Audio oscillator nodes.' },
              ].map((s) => (
                <div
                  key={s.id}
                  onClick={() => setStrategy(s.id as any)}
                  className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                    strategy === s.id
                      ? 'bg-blue-50/60 dark:bg-blue-950/40 border-blue-500 text-slate-900 dark:text-white shadow-2xs'
                      : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300'
                  }`}
                >
                  <span className="font-semibold text-xs block mb-1">{s.title}</span>
                  <p className="text-xs text-slate-500 leading-relaxed">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Strength Level */}
          <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
              Masking Strength Level
            </h3>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'LOW', label: 'Standard', desc: 'Zero site friction' },
                { id: 'BALANCED', label: 'Balanced', desc: 'Recommended default' },
                { id: 'AGGRESSIVE', label: 'Aggressive', desc: 'Maximum anonymity' },
              ].map((lvl) => (
                <button
                  key={lvl.id}
                  type="button"
                  onClick={() => setStrength(lvl.id as any)}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    strength === lvl.id
                      ? 'bg-blue-50/60 dark:bg-blue-950/40 border-blue-500 text-slate-900 dark:text-white'
                      : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300'
                  }`}
                >
                  <span className="font-semibold text-xs block">{lvl.label}</span>
                  <span className="text-[11px] text-slate-500">{lvl.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Granular Vector Switches */}
          <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
              Granular Signal Interceptors
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                { key: 'mask_canvas', label: 'Canvas Subpixel Jitter', desc: 'Randomize offscreen 2D render hash' },
                { key: 'mask_webgl', label: 'WebGL Normalization', desc: 'Mask unmasked renderer vendor strings' },
                { key: 'mask_navigator', label: 'Navigator Metadata', desc: 'Sync platform and browser user-agent' },
                { key: 'mask_screen', label: 'Screen Dimension Snapping', desc: 'Normalize viewport and DPI ratios' },
                { key: 'mask_timezone', label: 'Timezone Locale Alignment', desc: 'Align Intl date format to standard zone' },
                { key: 'mask_audio', label: 'AudioContext Fuzzing', desc: 'Fuzz frequency node processing buffers' },
              ].map((flag) => (
                <label
                  key={flag.key}
                  className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
                >
                  <div>
                    <span className="text-xs font-semibold text-slate-900 dark:text-white block">{flag.label}</span>
                    <span className="text-[11px] text-slate-500">{flag.desc}</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={(rules as any)[flag.key]}
                    onChange={(e) => setRules({ ...rules, [flag.key]: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
                  />
                </label>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
