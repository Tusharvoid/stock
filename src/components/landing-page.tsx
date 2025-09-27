import { useState, useEffect, useRef } from "react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import {
  Cloud,
  Shield,
  TrendingUp,
  BarChart3,
  Brain,
  ShoppingCart,
} from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { StockMarketBackground } from "./stock-market-background";
import { RealTimeStockCharts } from "./real-time-stock-charts";

interface LandingPageProps {
  onNavigate: (page: "stocks" | "mutual-funds") => void;
  onSignIn: () => void;
  onSignUp: () => void;
}

const portfolioFeatures = [
  {
    title: "REAL-TIME DATA",
    description:
      "Live market updates and instant portfolio synchronization",
    icon: Cloud,
    image:
      "https://images.unsplash.com/photo-1612178991541-b48cc8e92a4d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdG9jayUyMG1hcmtldCUyMHRyYWRpbmclMjBmaW5hbmNpYWwlMjBjaGFydHN8ZW58MXx8fHwxNzU4NDU2NjM0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  },
  {
    title: "SECURE ACCESS",
    description:
      "Bank-level security with encrypted data protection",
    icon: Shield,
    image:
      "https://images.unsplash.com/photo-1551288049-bebda4e38f71?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmaW5hbmNpYWwlMjBkYXNoYm9hcmQlMjBhbmFseXRpY3N8ZW58MXx8fHwxNzU4Mzk0NjQ5fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  },
  {
    title: "AI PREDICTIONS",
    description:
      "Machine learning powered investment insights and forecasts",
    icon: Brain,
    image:
      "https://images.unsplash.com/photo-1709120395858-92f1c7c577f5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhcnRpZmljaWFsJTIwaW50ZWxsaWdlbmNlJTIwZmluYW5jZSUyMHRlY2hub2xvZ3l8ZW58MXx8fHwxNzU4NDU2NjQ0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  },
  {
    title: "BUY OR SELL",
    description:
      "Execute trades with one-click order management system",
    icon: ShoppingCart,
    image:
      "https://images.unsplash.com/photo-1653378972336-103e1ea62721?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtdXR1YWwlMjBmdW5kcyUyMGludmVzdG1lbnQlMjBwb3J0Zm9saW98ZW58MXx8fHwxNzU4NDU2NjQxfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  },
];

export function LandingPage({
  onNavigate,
  onSignIn,
  onSignUp,
}: LandingPageProps) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [dragOffset, setDragOffset] = useState(0);
  const [autoPlayEnabled, setAutoPlayEnabled] = useState(true);
  const sliderRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!autoPlayEnabled) return;

    const timer = setInterval(() => {
      setCurrentSlide(
        (prev) => (prev + 1) % portfolioFeatures.length,
      );
    }, 5000);
    return () => clearInterval(timer);
  }, [autoPlayEnabled]);

  const nextSlide = () => {
    setCurrentSlide(
      (prev) => (prev + 1) % portfolioFeatures.length,
    );
  };

  const prevSlide = () => {
    setCurrentSlide(
      (prev) =>
        (prev - 1 + portfolioFeatures.length) %
        portfolioFeatures.length,
    );
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setStartX(e.clientX);
    setDragOffset(0);
    setAutoPlayEnabled(false);
    if (sliderRef.current) {
      sliderRef.current.style.cursor = "grabbing";
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;

    const currentX = e.clientX;
    const offset = currentX - startX;
    setDragOffset(offset);
  };

  const handleMouseUp = () => {
    if (!isDragging) return;

    setIsDragging(false);
    if (sliderRef.current) {
      sliderRef.current.style.cursor = "grab";
    }

    const threshold = 100;

    if (Math.abs(dragOffset) > threshold) {
      if (dragOffset > 0) {
        prevSlide();
      } else {
        nextSlide();
      }
    }

    setDragOffset(0);

    // Re-enable autoplay after 3 seconds of no interaction
    setTimeout(() => {
      setAutoPlayEnabled(true);
    }, 3000);
  };

  const handleMouseLeave = () => {
    if (isDragging) {
      handleMouseUp();
    }
  };

  return (
    <div className="min-h-screen bg-background relative">
      {/* Full Screen Stock Market Background */}
      <div className="fixed inset-0 z-0">
        <StockMarketBackground />
        <div className="absolute inset-0 bg-background/80" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-border bg-card/80 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-gradient-to-r from-chart-1 to-chart-2 rounded-full"></div>
              <div className="h-6 w-6 bg-gradient-to-r from-chart-2 to-chart-3 rounded-sm"></div>
              <div className="h-4 w-4 bg-gradient-to-r from-chart-3 to-chart-4"></div>
              <span className="ml-2 text-xl bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                Portfolio Hub
              </span>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                onClick={onSignIn}
                className="border-border hover:bg-accent"
              >
                Sign In
              </Button>
              <Button
                onClick={onSignUp}
                className="bg-gradient-to-r from-chart-1 to-chart-2 text-white hover:from-chart-1/90 hover:to-chart-2/90"
              >
                Sign Up
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section with Slider */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <div className="text-foreground relative">
            {/* Content */}
            <div className="relative z-10">
              <div className="text-center mb-12">
                <h1 className="text-4xl md:text-6xl mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                  Smarter Portfolio.
                </h1>
                <p className="text-xl text-muted-foreground mb-8">
                  Cloud-powered dashboard for stocks & mutual
                  funds.
                </p>
              </div>

              {/* Draggable Feature Slider */}
              <div className="relative">
                <div
                  ref={sliderRef}
                  className="flex items-center justify-center min-h-[240px] cursor-grab select-none overflow-hidden"
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseLeave}
                >
                  <div
                    className="text-center max-w-md transition-transform duration-300 ease-out"
                    style={{
                      transform: `translateX(${dragOffset}px)`,
                    }}
                  >
                    <div className="mb-6 flex justify-center">
                      {(() => {
                        const IconComponent =
                          portfolioFeatures[currentSlide].icon;
                        return (
                          <div className="p-6 bg-card rounded-full backdrop-blur-sm border border-border shadow-lg hover:shadow-xl transition-shadow">
                            <IconComponent className="h-16 w-16 text-chart-1" />
                          </div>
                        );
                      })()}
                    </div>
                    <h3 className="text-3xl mb-4 text-foreground">
                      {portfolioFeatures[currentSlide].title}
                    </h3>
                    <p className="text-muted-foreground text-lg leading-relaxed">
                      {
                        portfolioFeatures[currentSlide]
                          .description
                      }
                    </p>

                    {/* Drag hint */}
                    <div className="mt-6">
                      <p className="text-muted-foreground/60 text-sm"></p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Call to Action */}
              <div className="text-center mt-12">
                <div className="mb-6">
                  <p className="text-muted-foreground text-lg mb-6">
                    Join thousands of investors who trust our
                    platform for their portfolio management.
                  </p>
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button
                    size="lg"
                    className="px-12 py-6 text-lg bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white border-0 shadow-lg"
                    onClick={onSignUp}
                  >
                    Create Account
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    className="px-8 py-6 text-lg border-border hover:bg-accent"
                    onClick={onSignIn}
                  >
                    Sign In
                  </Button>
                </div>
              </div>

              {/* Real-time Stock Charts Section */}
              <div className="mt-20">
                <div className="max-w-5xl mx-auto">
                  <div className="text-center mb-12">
                    <h2 className="text-3xl mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                      Live Market Data
                    </h2>
                    <p className="text-muted-foreground text-lg">
                      Real-time stock prices and trends from
                      major markets
                    </p>
                  </div>
                  <RealTimeStockCharts />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}