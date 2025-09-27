import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { TrendingUp, BarChart3, PieChart, Target } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { PortfolioLayout } from "./portfolio-layout";

interface MainPortfolioPageProps {
  onNavigate: (page: 'stocks' | 'mutual-funds') => void;
  onLogout: () => void;
}

export function MainPortfolioPage({ onNavigate, onLogout }: MainPortfolioPageProps) {
  const handleNavigate = (page: string) => {
    if (page === 'stocks' || page === 'mutual-funds') {
      onNavigate(page);
    }
    // Handle other navigation cases as needed
  };

  return (
    <PortfolioLayout 
      currentPage="main-portfolio" 
      onNavigate={handleNavigate}
      onLogout={onLogout}
    >
      <div className="p-6">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl mb-2 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">Portfolio Dashboard</h1>
          <p className="text-gray-400">
            Choose your investment type to access detailed analytics and management tools.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Total Portfolio Value</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl text-white">$186,543</div>
              <p className="text-sm text-green-400">+2.4% today</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Total Gain/Loss</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl text-green-400">+$18,654</div>
              <p className="text-sm text-gray-400">+11.1% overall</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Active Holdings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl text-white">23</div>
              <p className="text-sm text-gray-400">9 stocks, 14 funds</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Cash Available</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl text-white">$5,420</div>
              <p className="text-sm text-gray-400">Ready to invest</p>
            </CardContent>
          </Card>
        </div>

        {/* Portfolio Options */}
        <div className="grid gap-6 md:grid-cols-2 mb-8">
          <Card className="cursor-pointer hover:shadow-xl hover:shadow-blue-500/20 transition-all duration-300 bg-gray-900/50 border-gray-700 backdrop-blur-md" onClick={() => onNavigate('stocks')}>
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-white">
                <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
                Stock Portfolio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative h-32 rounded-lg overflow-hidden">
                  <ImageWithFallback
                    src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdG9jayUyMG1hcmtldCUyMHRyYWRpbmclMjBmaW5hbmNpYWwlMjBjaGFydHN8ZW58MXx8fHwxNzU4NDU2NjM0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                    alt="Stock portfolio overview"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">Current Value:</span>
                    <span className="font-medium text-white">$120,345</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">Day Change:</span>
                    <span className="text-green-400">+$1,234 (+1.0%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">Holdings:</span>
                    <span className="font-medium text-white">9 stocks</span>
                  </div>
                </div>
                
                <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 border-0">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  View Stock Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-xl hover:shadow-green-500/20 transition-all duration-300 bg-gray-900/50 border-gray-700 backdrop-blur-md" onClick={() => onNavigate('mutual-funds')}>
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-white">
                <div className="p-3 bg-gradient-to-r from-green-500 to-green-600 rounded-lg">
                  <PieChart className="h-6 w-6 text-white" />
                </div>
                Mutual Fund Portfolio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative h-32 rounded-lg overflow-hidden">
                  <ImageWithFallback
                    src="https://images.unsplash.com/photo-1653378972336-103e1ea62721?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtdXR1YWwlMjBmdW5kcyUyMGludmVzdG1lbnQlMjBwb3J0Zm9saW98ZW58MXx8fHwxNzU4NDU2NjQxfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                    alt="Mutual fund portfolio overview"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">Current Value:</span>
                    <span className="font-medium text-white">$66,198</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">Day Change:</span>
                    <span className="text-green-400">+$456 (+0.7%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">Holdings:</span>
                    <span className="font-medium text-white">14 funds</span>
                  </div>
                </div>
                
                <Button variant="outline" className="w-full border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white">
                  <Target className="h-4 w-4 mr-2" />
                  View Fund Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
          <CardHeader>
            <CardTitle className="text-white">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 border border-gray-700 rounded-lg bg-gray-800/30">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center">
                    <TrendingUp className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-white">Bought AAPL</p>
                    <p className="text-sm text-gray-400">10 shares at $185.42</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium text-white">$1,854.20</p>
                  <p className="text-sm text-gray-400">2 hours ago</p>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 border border-gray-700 rounded-lg bg-gray-800/30">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                    <PieChart className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-white">Monthly VTIAX Investment</p>
                    <p className="text-sm text-gray-400">Automatic purchase</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium text-white">$500.00</p>
                  <p className="text-sm text-gray-400">1 day ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PortfolioLayout>
  );
}