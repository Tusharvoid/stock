import { useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { ArrowLeft, Eye, EyeOff, Mail, Lock } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { StockMarketBackground } from "./stock-market-background";
import { signIn } from "../utils/auth";

interface SignInPageProps {
  onBack: () => void;
  onSignIn: () => void;
  onNavigateToSignUp: () => void;
}

export function SignInPage({ onBack, onSignIn, onNavigateToSignUp }: SignInPageProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    
    try {
      const result = await signIn(email, password);
      
      if (result.error) {
        setError(result.error);
        setIsLoading(false);
        return;
      }

      // Success - redirect to main app
      onSignIn();
      
    } catch (error) {
      setError("An unexpected error occurred. Please try again.");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex">
      {/* Full Screen Stock Market Background */}
      <div className="fixed inset-0 z-0">
        <StockMarketBackground />
        <div className="absolute inset-0 bg-black/60" />
      </div>

      {/* Left side - Form */}
      <div className="relative z-10 flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md space-y-8">
          <div className="flex items-center gap-4 mb-8">
            <Button variant="ghost" onClick={onBack} className="text-white hover:bg-white/10">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </div>

          <div className="text-center space-y-2">
            <h1 className="text-3xl bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">Welcome back</h1>
            <p className="text-gray-400">
              Sign in to your portfolio dashboard
            </p>
          </div>

          <Card className="bg-black/40 border-white/20 backdrop-blur-md">
            <CardHeader>
              <CardTitle className="text-white">Sign In</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <div className="p-3 bg-red-500/20 border border-red-500/30 rounded text-red-400 text-sm">
                    {error}
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        setError(""); // Clear error when user types
                      }}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        setError(""); // Clear error when user types
                      }}
                      className="pl-10 pr-10"
                      required
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <input
                      id="remember"
                      type="checkbox"
                      className="rounded border-border"
                    />
                    <Label htmlFor="remember" className="text-sm">
                      Remember me
                    </Label>
                  </div>
                  <Button variant="link" className="px-0 text-sm text-white/70 hover:text-white">
                    Forgot password?
                  </Button>
                </div>

                <Button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 border-0" disabled={isLoading}>
                  {isLoading ? "Signing in..." : "Sign In"}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-white/70">
                  Don't have an account?{" "}
                  <Button variant="link" className="px-0 text-white hover:text-white/80" onClick={onNavigateToSignUp}>
                    Sign up
                  </Button>
                </p>
              </div>


            </CardContent>
          </Card>
        </div>
      </div>

      {/* Right side - Content */}
      <div className="hidden lg:flex flex-1 relative z-10 items-center justify-center p-8">
        <div className="text-center text-white max-w-md">
          <div className="mb-8 p-6 bg-white/5 rounded-full backdrop-blur-sm border border-white/10 inline-block">
            <svg className="h-16 w-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
          </div>
          <h2 className="text-3xl mb-4">Manage your investments with confidence</h2>
          <p className="text-white/80 text-lg">
            Access real-time market data, AI-powered insights, and secure trading all in one place.
          </p>
        </div>
      </div>
    </div>
  );
}