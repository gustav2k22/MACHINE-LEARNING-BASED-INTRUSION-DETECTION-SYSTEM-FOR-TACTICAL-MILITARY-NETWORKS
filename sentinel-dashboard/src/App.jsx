/**
 * @fileoverview Root application component for the SENTINEL-IDS dashboard.
 *
 * Architecture:
 *  - context/ThemeContext  — dark/light mode with OS preference detection
 *  - hooks/useSimulation   — real-time packet, timeline, and threat level state
 *  - components/           — reusable UI primitives (Panel, KPICard, Sidebar, TopBar, etc.)
 *  - pages/                — one component per dashboard page
 *  - data/                 — constants, metrics, and mock data generators
 *
 * The App component manages page routing via simple useState and delegates
 * all simulation logic to the useSimulation hook.
 */

import { useState } from 'react';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { useSimulation } from './hooks/useSimulation';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { DashboardPage } from './pages/DashboardPage';
import { ScenarioTestPage } from './pages/ScenarioTestPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { ArchitecturePage } from './pages/ArchitecturePage';
import { AlertsPage } from './pages/AlertsPage';
import './App.css';

/**
 * Inner app shell — uses hooks that require ThemeProvider to be mounted above.
 * Manages page routing and passes simulation state to child pages.
 */
function AppShell() {
  const { colors } = useTheme();
  const { packets, timeline, attackCount, totalPackets, clock, threatLevel } = useSimulation();
  const [page, setPage] = useState('dashboard');

  return (
    <div
      className="flex h-screen overflow-hidden transition-colors duration-200"
      style={{ background: colors.navy, color: colors.white }}
    >
      {/* Scanline overlay (dark mode only) */}
      <div className="scanline-overlay" />

      {/* Sidebar Navigation */}
      <Sidebar activePage={page} onNavigate={setPage} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Status Bar */}
        <TopBar clock={clock} threatLevel={threatLevel} />

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-4">
          {page === 'dashboard' && (
            <DashboardPage
              packets={packets}
              timeline={timeline}
              attackCount={attackCount}
              totalPackets={totalPackets}
            />
          )}
          {page === 'test' && <ScenarioTestPage />}
          {page === 'model' && <ModelPerformancePage />}
          {page === 'arch' && <ArchitecturePage />}
          {page === 'alerts' && <AlertsPage />}
        </main>
      </div>
    </div>
  );
}

/**
 * Root App component — wraps the shell in the ThemeProvider
 * so all children have access to theme context.
 */
export default function App() {
  return (
    <ThemeProvider>
      <AppShell />
    </ThemeProvider>
  );
}
