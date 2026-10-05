import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail, ArrowRight, Zap } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { ThemeToggle } from '../components/common/ThemeToggle';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('demo@maskit.dev');
  const [password, setPassword] = useState('SecurePass123!');
  const { login, loginAsDemo, isLoading, error, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    const success = await login(email, password);
    if (success) {
      navigate('/dashboard');
    }
  };

  const handleInstantDemo = () => {
    loginAsDemo();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 transition-colors relative">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-2">
        <Link to="/" className="inline-flex items-center space-x-2.5">
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <Shield className="w-5 h-5" />
          </div>
          <span className="font-bold text-2xl tracking-tight text-slate-900 dark:text-white">
            MaskIt
          </span>
        </Link>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
          Sign In to Your Account
        </h2>
        <p className="text-xs text-slate-500">
          Manage protected websites, risk thresholds, and live telemetry
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800 space-y-5">
          {error && <ErrorBanner message={error} onRetry={clearError} />}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Account Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-9 pr-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs rounded-lg shadow-sm transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              <span>{isLoading ? 'Signing In...' : 'Sign In'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={handleInstantDemo}
              className="w-full py-2 bg-slate-50 dark:bg-slate-800/70 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 font-medium text-xs rounded-lg transition-colors flex items-center justify-center space-x-1.5"
            >
              <Zap className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
              <span>Continue with Demo Session</span>
            </button>
          </form>

          {/* Quick Demo Helper */}
          <div className="pt-2 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500 flex items-center justify-between">
            <span>Demo Account:</span>
            <button
              type="button"
              onClick={() => {
                setEmail('demo@maskit.dev');
                setPassword('SecurePass123!');
              }}
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              Fill Credentials
            </button>
          </div>

          <div className="text-center pt-2">
            <p className="text-xs text-slate-500">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-600 dark:text-blue-400 hover:underline font-medium">
                Register here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
