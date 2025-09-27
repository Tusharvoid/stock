import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, BarChart3 } from "lucide-react";

export function StockMarketBackground() {
  const [particles, setParticles] = useState<Array<{
    id: number;
    x: number;
    y: number;
    direction: 'up' | 'down';
    symbol: string;
    change: string;
    speed: number;
    opacity: number;
  }>>([]);

  const [marketPulse, setMarketPulse] = useState(0);

  const stockSymbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX', 'SPY', 'QQQ', 'BTC', 'ETH'];
  
  useEffect(() => {
    const generateParticle = () => ({
      id: Math.random(),
      x: Math.random() * 100,
      y: Math.random() * 100,
      direction: Math.random() > 0.65 ? 'up' : 'down',
      symbol: stockSymbols[Math.floor(Math.random() * stockSymbols.length)],
      change: `${Math.random() > 0.65 ? '+' : '-'}${(Math.random() * 8 + 0.1).toFixed(2)}%`,
      speed: Math.random() * 0.5 + 0.3,
      opacity: Math.random() * 0.6 + 0.4
    });

    // Initialize particles
    const initialParticles = Array.from({ length: 18 }, generateParticle);
    setParticles(initialParticles);

    // Market pulse animation
    const pulseInterval = setInterval(() => {
      setMarketPulse(prev => (prev + 1) % 100);
    }, 50);

    // Update particles periodically
    const interval = setInterval(() => {
      setParticles(prev => prev.map(particle => ({
        ...particle,
        y: particle.direction === 'up' ? 
          (particle.y - particle.speed + 100) % 100 : 
          (particle.y + particle.speed) % 100,
        x: (particle.x + (Math.random() - 0.5) * 0.1 + 100) % 100,
        direction: Math.random() > 0.97 ? (Math.random() > 0.65 ? 'up' : 'down') : particle.direction,
        change: Math.random() > 0.985 ? 
          `${Math.random() > 0.65 ? '+' : '-'}${(Math.random() * 8 + 0.1).toFixed(2)}%` : 
          particle.change,
        opacity: Math.random() > 0.98 ? Math.random() * 0.6 + 0.4 : particle.opacity
      })));
    }, 80);

    return () => {
      clearInterval(interval);
      clearInterval(pulseInterval);
    };
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Animated gradient background with market pulse */}
      <div 
        className="absolute inset-0 transition-all duration-300"
        style={{
          background: `
            radial-gradient(ellipse at ${30 + Math.sin(marketPulse * 0.1) * 20}% ${40 + Math.cos(marketPulse * 0.08) * 15}%, 
              rgba(34, 197, 94, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at ${70 + Math.cos(marketPulse * 0.12) * 25}% ${60 + Math.sin(marketPulse * 0.09) * 20}%, 
              rgba(239, 68, 68, 0.15) 0%, transparent 50%),
            linear-gradient(45deg, rgba(0, 0, 0, 0.8), rgba(15, 23, 42, 0.6))
          `
        }}
      />
      
      {/* Dynamic grid pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="h-full w-full" style={{
          backgroundImage: `
            linear-gradient(rgba(34, 197, 94, ${0.2 + Math.sin(marketPulse * 0.1) * 0.1}) 1px, transparent 1px),
            linear-gradient(90deg, rgba(239, 68, 68, ${0.15 + Math.cos(marketPulse * 0.08) * 0.1}) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
          transform: `translateX(${Math.sin(marketPulse * 0.02) * 2}px) translateY(${Math.cos(marketPulse * 0.015) * 2}px)`
        }} />
      </div>

      {/* Floating candlestick charts */}
      <div className="absolute inset-0">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="absolute"
            style={{
              left: `${15 + i * 15}%`,
              top: `${20 + Math.sin(marketPulse * 0.05 + i) * 10}%`,
              transform: `rotate(${Math.sin(marketPulse * 0.03 + i) * 5}deg)`
            }}
          >
            <BarChart3 
              className={`h-8 w-8 ${Math.sin(marketPulse * 0.1 + i) > 0 ? 'text-green-400' : 'text-red-400'} opacity-30`} 
            />
          </div>
        ))}
      </div>

      {/* Floating stock indicators */}
      {particles.map(particle => (
        <div
          key={particle.id}
          className={`absolute transition-all duration-200 ease-out ${
            particle.direction === 'up' ? 'text-green-400' : 'text-red-400'
          }`}
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            transform: 'translate(-50%, -50%)',
            opacity: particle.opacity
          }}
        >
          <div className={`flex items-center gap-1 text-xs font-mono backdrop-blur-sm px-2 py-1 rounded-md border transition-all duration-200 ${
            particle.direction === 'up' 
              ? 'bg-green-500/10 border-green-500/20 shadow-green-500/20' 
              : 'bg-red-500/10 border-red-500/20 shadow-red-500/20'
          } hover:scale-110`}>
            {particle.direction === 'up' ? 
              <TrendingUp className="h-3 w-3 animate-pulse" /> : 
              <TrendingDown className="h-3 w-3 animate-pulse" />
            }
            <span className="text-white/70 font-medium">{particle.symbol}</span>
            <span className={`font-bold ${particle.direction === 'up' ? 'text-green-300' : 'text-red-300'}`}>
              {particle.change}
            </span>
          </div>
        </div>
      ))}

      {/* Animated market trend lines */}
      <svg className="absolute inset-0 w-full h-full opacity-30">
        <defs>
          <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="transparent" />
            <stop offset="30%" stopColor="rgba(34, 197, 94, 0.8)" />
            <stop offset="70%" stopColor="rgba(34, 197, 94, 0.8)" />
            <stop offset="100%" stopColor="transparent" />
          </linearGradient>
          <linearGradient id="redGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="transparent" />
            <stop offset="30%" stopColor="rgba(239, 68, 68, 0.8)" />
            <stop offset="70%" stopColor="rgba(239, 68, 68, 0.8)" />
            <stop offset="100%" stopColor="transparent" />
          </linearGradient>
          <linearGradient id="pulseGreen" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="transparent" />
            <stop offset="50%" stopColor="rgba(34, 197, 94, 0.6)" />
            <stop offset="100%" stopColor="transparent" />
            <animateTransform
              attributeName="gradientTransform"
              type="translate"
              values="-100 0;200 0;-100 0"
              dur="3s"
              repeatCount="indefinite"
            />
          </linearGradient>
          <linearGradient id="pulseRed" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="transparent" />
            <stop offset="50%" stopColor="rgba(239, 68, 68, 0.6)" />
            <stop offset="100%" stopColor="transparent" />
            <animateTransform
              attributeName="gradientTransform"
              type="translate"
              values="200 0;-100 0;200 0"
              dur="4s"
              repeatCount="indefinite"
            />
          </linearGradient>
        </defs>
        
        {/* Dynamic market trend lines with animation */}
        <path
          d="M0,60 Q25,40 50,45 T100,30"
          stroke="url(#pulseGreen)"
          strokeWidth="3"
          fill="none"
          opacity="0.8"
        />
        <path
          d="M0,80 Q25,85 50,75 T100,70"
          stroke="url(#pulseRed)"
          strokeWidth="3"
          fill="none"
          opacity="0.8"
        />
        <path
          d="M0,40 Q25,35 50,50 T100,20"
          stroke="url(#greenGradient)"
          strokeWidth="2"
          fill="none"
          className="animate-pulse"
          style={{ animationDelay: '0.5s' }}
        />
        <path
          d="M0,90 Q25,75 50,85 T100,65"
          stroke="url(#redGradient)"
          strokeWidth="2"
          fill="none"
          className="animate-pulse"
          style={{ animationDelay: '1.5s' }}
        />
        
        {/* Additional flowing lines */}
        <path
          d="M0,25 Q25,20 50,30 T100,15"
          stroke="rgba(34, 197, 94, 0.4)"
          strokeWidth="1"
          fill="none"
          strokeDasharray="5,5"
          className="animate-pulse"
        />
        <path
          d="M0,95 Q25,90 50,95 T100,85"
          stroke="rgba(239, 68, 68, 0.4)"
          strokeWidth="1"
          fill="none"
          strokeDasharray="3,3"
          className="animate-pulse"
          style={{ animationDelay: '2s' }}
        />
      </svg>
    </div>
  );
}