import { ReactNode } from "react";
import { PortfolioSidebar } from "./portfolio-sidebar";

interface PortfolioLayoutProps {
  children: ReactNode;
  currentPage: string;
  onNavigate: (page: string) => void;
  onLogout: () => void;
}

export function PortfolioLayout({ children, currentPage, onNavigate, onLogout }: PortfolioLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex">
      <PortfolioSidebar 
        currentPage={currentPage}
        onNavigate={onNavigate}
        onLogout={onLogout}
      />
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
}