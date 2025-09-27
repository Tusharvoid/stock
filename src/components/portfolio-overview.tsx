import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { TrendingUp, TrendingDown, DollarSign, Percent } from "lucide-react";

interface PortfolioOverviewProps {
  totalValue: number;
  dayChange: number;
  dayChangePercent: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
}

export function PortfolioOverview({
  totalValue,
  dayChange,
  dayChangePercent,
  totalGainLoss,
  totalGainLossPercent
}: PortfolioOverviewProps) {
  const isPositiveDay = dayChange >= 0;
  const isPositiveTotal = totalGainLoss >= 0;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm">Total Portfolio Value</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl">${totalValue.toLocaleString()}</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm">Day Change</CardTitle>
          {isPositiveDay ? (
            <TrendingUp className="h-4 w-4 text-green-600" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-600" />
          )}
        </CardHeader>
        <CardContent>
          <div className={`text-2xl ${isPositiveDay ? 'text-green-600' : 'text-red-600'}`}>
            {isPositiveDay ? '+' : ''}${dayChange.toLocaleString()}
          </div>
          <p className={`text-sm ${isPositiveDay ? 'text-green-600' : 'text-red-600'}`}>
            {isPositiveDay ? '+' : ''}{dayChangePercent.toFixed(2)}%
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm">Total Gain/Loss</CardTitle>
          {isPositiveTotal ? (
            <TrendingUp className="h-4 w-4 text-green-600" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-600" />
          )}
        </CardHeader>
        <CardContent>
          <div className={`text-2xl ${isPositiveTotal ? 'text-green-600' : 'text-red-600'}`}>
            {isPositiveTotal ? '+' : ''}${totalGainLoss.toLocaleString()}
          </div>
          <p className={`text-sm ${isPositiveTotal ? 'text-green-600' : 'text-red-600'}`}>
            {isPositiveTotal ? '+' : ''}{totalGainLossPercent.toFixed(2)}%
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm">Asset Allocation</CardTitle>
          <Percent className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Stocks</span>
              <span className="text-sm">75%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Mutual Funds</span>
              <span className="text-sm">25%</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}