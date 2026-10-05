import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Menu, X, ArrowRight } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { ThemeToggle } from '../common/ThemeToggle';

export const Navbar: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 backdrop-blur-sm transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <Shield className="w-5 h-5" />
          </div>
          <span className="font-bold text-xl tracking-tight text-slate-900 dark:text-white">
            MaskIt
          </span>
        </Link>

        {/* Desktop Links */}
        <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-600 dark:text-slate-300">
          <Link to="/" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            Home
          </Link>
          <a href="#how-it-works" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            How It Works
          </a>
          <Link to="/scan" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            Scanner
          </Link>
          <Link to="/dashboard" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            Dashboard
          </Link>
        </nav>

        {/* Desktop Actions */}
        <div className="hidden md:flex items-center space-x-3">
          <ThemeToggle />

          {isAuthenticated ? (
            <>
              <Link
                to="/dashboard"
                className="px-4 py-2 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Dashboard
              </Link>
              <button
                onClick={() => {
                  logout();
                  navigate('/');
                }}
                className="text-sm font-medium text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 px-2 py-1"
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="px-4 py-2 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Log in
              </Link>
              <Link
                to="/scan"
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium shadow-sm transition-colors flex items-center space-x-1.5"
              >
                <span>Scan Browser</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </>
          )}
        </div>

        {/* Mobile controls */}
        <div className="flex items-center space-x-2 md:hidden">
          <ThemeToggle />
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 pt-2 pb-6 space-y-3 text-sm">
          <Link
            to="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-slate-700 dark:text-slate-200"
          >
            Home
          </Link>
          <a
            href="#how-it-works"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-slate-700 dark:text-slate-200"
          >
            How It Works
          </a>
          <Link
            to="/scan"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-blue-600 dark:text-blue-400 font-medium"
          >
            Scanner
          </Link>
          <Link
            to="/dashboard"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-slate-700 dark:text-slate-200"
          >
            Dashboard
          </Link>

          <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex flex-col gap-2">
            {isAuthenticated ? (
              <button
                onClick={() => {
                  logout();
                  setMobileMenuOpen(false);
                  navigate('/');
                }}
                className="w-full text-left py-2 text-rose-600"
              >
                Sign out
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2 text-center rounded-lg border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 font-medium"
                >
                  Log in
                </Link>
                <Link
                  to="/scan"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2 text-center rounded-lg bg-blue-600 text-white font-medium shadow-sm"
                >
                  Scan Browser
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
