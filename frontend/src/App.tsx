import React from "react";
import { BlockExplorer } from "./components/BlockExplorer";
import "./App.css";

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 transition-colors duration-300">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-40 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            {/* Logo Icon */}
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white font-extrabold shadow-md shadow-purple-500/20">
              F
            </div>
            <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
              FabiCoin
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs font-semibold text-slate-500 dark:text-slate-400">
            <span>Red: Localhost</span>
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
          </div>
        </div>
      </header>

      {/* Main BlockExplorer View */}
      <main className="py-8">
        <BlockExplorer />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950/50 py-6 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 FabiCoin Core Developer Team. Todos los derechos reservados.</p>
          <p className="font-mono">v0.1.0-alpha</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
