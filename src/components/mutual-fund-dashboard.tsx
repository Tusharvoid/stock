import { Button } from "./ui/button";
import { TrendingUp, TrendingDown, PieChart, Target, Brain } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { PortfolioChart } from "./portfolio-chart";
import { HoldingsTable, type Holding } from "./holdings-table";
import { Badge } from "./ui/badge";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { PortfolioLayout } from "./portfolio-layout";

interface MutualFundDashboardProps {
  onBack: () => void;
}

const mockMutualFunds: Holding[] = [
  {
    symbol: "VTIAX",
    name: "Vanguard Total International Stock Index Fund",
    type: "mutual-fund",
    shares: 500,
    currentPrice: 32.85,
    marketValue: 16425,
    dayChange: 0.45,
    dayChangePercent: 1.39,
    totalGainLoss: 1425,
    totalGainLossPercent: 9.51
  },
  {
    symbol: "VTSAX",
    name: "Vanguard Total Stock Market Index Fund",
    type: "mutual-fund",
    shares: 300,
    currentPrice: 118.75,
    marketValue: 35625,
    dayChange: 1.25,
    dayChangePercent: 1.06,
    totalGainLoss: 3625,
    totalGainLossPercent: 11.32
  },
  {
    symbol: "VBTLX",
    name: "Vanguard Total Bond Market Index Fund",
    type: "mutual-fund",
    shares: 400,
    currentPrice: 10.85,
    marketValue: 4340,
    dayChange: -0.15,
    dayChangePercent: -1.36,
    totalGainLoss: -160,
    totalGainLossPercent: -3.56
  },
  {
    symbol: "VTSMX",
    name: "Vanguard Total Stock Market Index Fund Investor",
    type: "mutual-fund",
    shares: 200,
    currentPrice: 89.42,
    marketValue: 17884,
    dayChange: 0.89,
    dayChangePercent: 1.01,
    totalGainLoss: 1884,
    totalGainLossPercent: 11.77
  }
];

const fundCategories = [
  { name: "Large Cap Growth", allocation: 35, color: "bg-blue-500" },
  { name: "International", allocation: 25, color: "bg-green-500" },
  { name: "Bonds", allocation: 20, color: "bg-yellow-500" },
  { name: "Small Cap Value", allocation: 20, color: "bg-purple-500" }
];

const topPerformers = [
  { symbol: "VTSAX", return: "11.32%", period: "YTD" },
  { symbol: "VTSMX", return: "11.77%", period: "YTD" },
  { symbol: "VTIAX", return: "9.51%", period: "YTD" }
];

export function MutualFundDashboard({ onBack }: MutualFundDashboardProps) {
  const totalValue = mockMutualFunds.reduce((sum, fund) => sum + fund.marketValue, 0);
  const totalDayChange = mockMutualFunds.reduce((sum, fund) => sum + fund.dayChange * fund.shares, 0);
  const dayChangePercent = (totalDayChange / totalValue) * 100;

  const handleNavigate = (page: string) => {
    if (page === 'main-portfolio') {
      onBack();
    }
    // Handle other navigation cases as needed
  };

  return (
    <PortfolioLayout 
      currentPage="mutual-funds" 
      onNavigate={handleNavigate}
      onLogout={onBack}
    >
      <div className="p-6 space-y-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl mb-2 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">Mutual Fund Portfolio</h1>
              <p className="text-gray-400">
                Diversified fund investment dashboard
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 border-0">
                <Target className="h-4 w-4 mr-2" />
                Rebalance
              </Button>
              <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white">
                <Brain className="h-4 w-4 mr-2" />
                AI Analysis
              </Button>
            </div>
          </div>
        </div>
        {/* Portfolio Overview */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Total Fund Value</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl text-white">${totalValue.toLocaleString()}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Day Change</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl flex items-center gap-2 ${totalDayChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalDayChange >= 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
                {totalDayChange >= 0 ? '+' : ''}${totalDayChange.toFixed(2)}
              </div>
              <p className={`text-sm ${totalDayChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalDayChange >= 0 ? '+' : ''}{dayChangePercent.toFixed(2)}%
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Active Funds</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl text-white">{mockMutualFunds.length}</div>
              <p className="text-sm text-gray-400">Holdings</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Avg Expense Ratio</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl text-white">0.04%</div>
              <p className="text-sm text-gray-400">Low cost</p>
            </CardContent>
          </Card>
        </div>

        {/* Asset Allocation */}
        <div className="grid gap-8 md:grid-cols-2">
          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <PieChart className="h-5 w-5" />
                Asset Allocation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {fundCategories.map((category) => (
                  <div key={category.name} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>{category.name}</span>
                      <span>{category.allocation}%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${category.color}`}
                        style={{ width: `${category.allocation}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader>
              <CardTitle className="text-white">Top Performers</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topPerformers.map((performer, index) => (
                  <div key={performer.symbol} className="flex items-center justify-between p-3 border border-border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center text-sm">
                        #{index + 1}
                      </div>
                      <span className="font-medium">{performer.symbol}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-green-600 font-medium">{performer.return}</div>
                      <div className="text-xs text-muted-foreground">{performer.period}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Performance Chart */}
        <PortfolioChart />

        {/* Mutual Fund Holdings */}
        <HoldingsTable holdings={mockMutualFunds} title="Mutual Fund Holdings" />

        {/* Investment Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Investment Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1653378972336-103e1ea62721?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtdXR1YWwlMjBmdW5kcyUyMGludmVzdG1lbnQlMjBwb3J0Zm9saW98ZW58MXx8fHwxNzU4NDU2NjQxfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Buy funds"
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <span>Buy Funds</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmaW5hbmNpYWwlMjBkYXNoYm9hcmQlMjBhbmFseXRpY3N8ZW58MXx8fHwxNzU4Mzk0NjQ5fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Sell funds"
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <span>Sell Funds</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1709120395858-92f1c7c577f5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhcnRpZmljaWFsJTIwaW50ZWxsaWdlbmNlJTIwZmluYW5jZSUyMHRlY2hub2xvZ3l8ZW58MXx8fHwxNzU4NDU2NjQ0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Fund analysis"
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <span>Fund Analysis</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1612178991541-b48cc8e92a4d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdG9jayUyMG1hcmtldCUyMHRyYWRpbmclMjBmaW5hbmNpYWwlMjBjaGFydHN8ZW58MXx8fHwxNzU4NDU2NjM0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Auto invest"
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <span>Auto Invest</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Fund Recommendations */}
        <Card>
          <CardHeader>
            <CardTitle>Recommended Funds</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="border border-border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">VXUS</span>
                  <Badge variant="secondary">International</Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  Vanguard Total International Stock ETF
                </p>
                <div className="text-sm">
                  <div className="flex justify-between mb-1">
                    <span>Expense Ratio:</span>
                    <span>0.08%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>1Y Return:</span>
                    <span className="text-green-600">+8.2%</span>
                  </div>
                </div>
              </div>

              <div className="border border-border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">VTI</span>
                  <Badge variant="default">US Total Market</Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  Vanguard Total Stock Market ETF
                </p>
                <div className="text-sm">
                  <div className="flex justify-between mb-1">
                    <span>Expense Ratio:</span>
                    <span>0.03%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>1Y Return:</span>
                    <span className="text-green-600">+12.1%</span>
                  </div>
                </div>
              </div>

              <div className="border border-border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">BND</span>
                  <Badge variant="outline">Bonds</Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  Vanguard Total Bond Market ETF
                </p>
                <div className="text-sm">
                  <div className="flex justify-between mb-1">
                    <span>Expense Ratio:</span>
                    <span>0.03%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>1Y Return:</span>
                    <span className="text-red-600">-2.1%</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PortfolioLayout>
  );
}