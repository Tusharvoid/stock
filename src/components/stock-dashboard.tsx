import { Button } from "./ui/button";
import { TrendingUp, TrendingDown, Brain, ShoppingCart } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { PortfolioChart } from "./portfolio-chart";
import { HoldingsTable, type Holding } from "./holdings-table";
import { Badge } from "./ui/badge";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { PortfolioLayout } from "./portfolio-layout";

interface StockDashboardProps {
  onBack: () => void;
}

const mockStocks: Holding[] = [
  {
    symbol: "AAPL",
    name: "Apple Inc.",
    type: "stock",
    shares: 50,
    currentPrice: 185.42,
    marketValue: 9271,
    dayChange: 2.35,
    dayChangePercent: 1.28,
    totalGainLoss: 1271,
    totalGainLossPercent: 15.9
  },
  {
    symbol: "MSFT",
    name: "Microsoft Corporation",
    type: "stock",
    shares: 25,
    currentPrice: 378.91,
    marketValue: 9472.75,
    dayChange: -5.23,
    dayChangePercent: -1.36,
    totalGainLoss: 972.75,
    totalGainLossPercent: 11.4
  },
  {
    symbol: "GOOGL",
    name: "Alphabet Inc.",
    type: "stock",
    shares: 15,
    currentPrice: 142.87,
    marketValue: 2143.05,
    dayChange: 3.42,
    dayChangePercent: 2.45,
    totalGainLoss: 143.05,
    totalGainLossPercent: 7.15
  },
  {
    symbol: "TSLA",
    name: "Tesla, Inc.",
    type: "stock",
    shares: 20,
    currentPrice: 248.50,
    marketValue: 4970,
    dayChange: -8.75,
    dayChangePercent: -3.40,
    totalGainLoss: -1030,
    totalGainLossPercent: -17.17
  },
  {
    symbol: "NVDA",
    name: "NVIDIA Corporation",
    type: "stock",
    shares: 10,
    currentPrice: 455.32,
    marketValue: 4553.20,
    dayChange: 12.87,
    dayChangePercent: 2.91,
    totalGainLoss: 553.20,
    totalGainLossPercent: 13.83
  }
];

const aiPredictions = [
  { symbol: "AAPL", prediction: "BUY", confidence: 85, target: 195.00, reason: "Strong quarterly earnings expected" },
  { symbol: "TSLA", prediction: "HOLD", confidence: 72, target: 260.00, reason: "Mixed market sentiment" },
  { symbol: "NVDA", prediction: "STRONG BUY", confidence: 91, target: 480.00, reason: "AI boom continues" }
];

export function StockDashboard({ onBack }: StockDashboardProps) {
  const totalValue = mockStocks.reduce((sum, stock) => sum + stock.marketValue, 0);
  const totalDayChange = mockStocks.reduce((sum, stock) => sum + stock.dayChange * stock.shares, 0);
  const dayChangePercent = (totalDayChange / totalValue) * 100;

  const handleNavigate = (page: string) => {
    if (page === 'main-portfolio') {
      onBack();
    }
    // Handle other navigation cases as needed
  };

  return (
    <PortfolioLayout 
      currentPage="stocks" 
      onNavigate={handleNavigate}
      onLogout={onBack}
    >
      <div className="p-6 space-y-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl mb-2 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">Stock Portfolio</h1>
              <p className="text-gray-400">
                Real-time stock market dashboard
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 border-0">
                <ShoppingCart className="h-4 w-4 mr-2" />
                Quick Trade
              </Button>
              <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white">
                <Brain className="h-4 w-4 mr-2" />
                AI Insights
              </Button>
            </div>
          </div>
        </div>
        {/* Portfolio Overview */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Total Stock Value</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl text-white">${totalValue.toLocaleString()}</div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Day Change</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl flex items-center gap-2 ${totalDayChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {totalDayChange >= 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
                {totalDayChange >= 0 ? '+' : ''}${totalDayChange.toFixed(2)}
              </div>
              <p className={`text-sm ${totalDayChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {totalDayChange >= 0 ? '+' : ''}{dayChangePercent.toFixed(2)}%
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Active Positions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl text-white">{mockStocks.length}</div>
              <p className="text-sm text-gray-400">Holdings</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Best Performer</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg text-white">NVDA</div>
              <p className="text-sm text-green-400">+13.83%</p>
            </CardContent>
          </Card>
        </div>

        {/* AI Predictions */}
        <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Brain className="h-5 w-5" />
              AI Stock Predictions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              {aiPredictions.map((prediction) => (
                <div key={prediction.symbol} className="border border-border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{prediction.symbol}</span>
                    <Badge variant={
                      prediction.prediction === 'STRONG BUY' ? 'default' :
                      prediction.prediction === 'BUY' ? 'secondary' : 
                      'outline'
                    }>
                      {prediction.prediction}
                    </Badge>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Target:</span>
                      <span>${prediction.target}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Confidence:</span>
                      <span>{prediction.confidence}%</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      {prediction.reason}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Performance Chart */}
        <PortfolioChart />

        {/* Stock Holdings */}
        <HoldingsTable holdings={mockStocks} title="Stock Holdings" />

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1612178991541-b48cc8e92a4d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdG9jayUyMG1hcmtldCUyMHRyYWRpbmclMjBmaW5hbmNpYWwlMjBjaGFydHN8ZW58MXx8fHwxNzU4NDU2NjM0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Buy stocks"
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <span>Buy Stocks</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmaW5hbmNpYWwlMjBkYXNoYm9hcmQlMjBhbmFseXRpY3N8ZW58MXx8fHwxNzU4Mzk0NjQ5fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Sell stocks"
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <span>Sell Stocks</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1709120395858-92f1c7c577f5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhcnRpZmljaWFsJTIwaW50ZWxsaWdlbmNlJTIwZmluYW5jZSUyMHRlY2hub2xvZ3l8ZW58MXx8fHwxNzU4NDU2NjQ0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Market analysis"
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <span>Market Analysis</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1653378972336-103e1ea62721?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtdXR1YWwlMjBmdW5kcyUyMGludmVzdG1lbnQlMjBwb3J0Zm9saW98ZW58MXx8fHwxNzU4NDU2NjQxfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Portfolio rebalance"
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <span>Rebalance</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </PortfolioLayout>
  );
}