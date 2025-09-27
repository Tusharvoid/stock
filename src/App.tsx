import { useState } from "react";
import { LandingPage } from "./components/landing-page";
import { SignInPage } from "./components/sign-in-page";
import { SignUpPage } from "./components/sign-up-page";
import { MainPortfolioPage } from "./components/main-portfolio-page";
import { StockDashboard } from "./components/stock-dashboard";
import { MutualFundDashboard } from "./components/mutual-fund-dashboard";

type Page = 'landing' | 'sign-in' | 'sign-up' | 'main-portfolio' | 'stocks' | 'mutual-funds';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const navigateToPage = (page: Page) => {
    setCurrentPage(page);
  };

  const navigateBack = () => {
    if (isAuthenticated) {
      setCurrentPage('main-portfolio');
    } else {
      setCurrentPage('landing');
    }
  };

  const handleSignIn = () => {
    setIsAuthenticated(true);
    setCurrentPage('main-portfolio');
  };

  const handleSignUp = () => {
    setIsAuthenticated(true);
    setCurrentPage('main-portfolio');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentPage('landing');
  };

  const navigateToPortfolio = (portfolioType: 'stocks' | 'mutual-funds') => {
    setCurrentPage(portfolioType);
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'sign-in':
        return (
          <SignInPage 
            onBack={navigateBack} 
            onSignIn={handleSignIn}
            onNavigateToSignUp={() => navigateToPage('sign-up')}
          />
        );
      case 'sign-up':
        return (
          <SignUpPage 
            onBack={navigateBack} 
            onSignUp={handleSignUp}
            onNavigateToSignIn={() => navigateToPage('sign-in')}
          />
        );
      case 'main-portfolio':
        return (
          <MainPortfolioPage 
            onNavigate={navigateToPortfolio}
            onLogout={handleLogout}
          />
        );
      case 'stocks':
        return <StockDashboard onBack={navigateBack} />;
      case 'mutual-funds':
        return <MutualFundDashboard onBack={navigateBack} />;
      default:
        return (
          <LandingPage 
            onNavigate={navigateToPortfolio}
            onSignIn={() => navigateToPage('sign-in')}
            onSignUp={() => navigateToPage('sign-up')}
          />
        );
    }
  };

  return (
    <div className="dark min-h-screen">
      {renderCurrentPage()}
    </div>
  );
}