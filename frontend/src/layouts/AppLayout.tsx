import { Outlet } from "react-router-dom";
import { AppHeader } from "./AppHeader";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-[var(--color-ink)]">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[100] focus:rounded-full focus:bg-[var(--color-marquee)] focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-[var(--color-ink)]"
      >
        Skip to content
      </a>
      <AppHeader />
      <main id="main-content">
        <Outlet />
      </main>
    </div>
  );
}
