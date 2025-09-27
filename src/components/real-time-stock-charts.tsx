import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, TrendingDown } from "lucide-react";
import { Card, CardContent } from "./ui/card";
import { getQuote, getCompanyProfile, isApiConfigured } from "../utils/finnhub";

interface StockData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  data: { time: string; value: number }[];
}

const generateStockData = (
  basePrice: number,
  volatility: number = 0.02,
) => {
  const data: { time: string; value: number }[] = [];
  let currentPrice = basePrice;

  for (let i = 0; i < 24; i++) {
    const hour = i.toString().padStart(2, "0") + ":00";
    const randomChange =
      (Math.random() - 0.5) * volatility * currentPrice;
    currentPrice += randomChange;
    data.push({
      time: hour,
      value: Number(currentPrice.toFixed(2)),
    });
  }

  return data;
};

const TRACKED_SYMBOLS = ["AAPL", "META", "TSLA", "MSFT", "NVDA", "AMZN"] as const;

export function RealTimeStockCharts() {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const apiReady = isApiConfigured();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!apiReady) {
      setError("Finnhub API key is missing. Set VITE_FINNHUB_API_KEY in .env.");
      return;
    }

    // Initial load for symbols
    (async () => {
      try {
        const loaded = await Promise.all(
          TRACKED_SYMBOLS.map(async (symbol) => {
            const [quote, profile] = await Promise.all([
              getQuote(symbol),
              getCompanyProfile(symbol),
            ]);
            if (!quote || typeof quote.c !== "number") {
              throw new Error("Invalid quote data");
            }
            const name = profile?.name ?? symbol;
            const price = Number(quote.c.toFixed(2));
            const base = quote.pc ?? quote.o ?? quote.c;
            const change = Number((price - base).toFixed(2));
            const changePercent = Number(((change / base) * 100).toFixed(2));
            return {
              symbol,
              name,
              price,
              change,
              changePercent,
              data: generateStockData(price, 0.02),
            } as StockData;
          })
        );
        setStocks(loaded);
      } catch (e) {
        setError("Failed to fetch initial stock data from Finnhub.");
      }
    })();

    const interval = setInterval(async () => {
      try {
        // Fetch all quotes first
        const pairs = await Promise.all(
          TRACKED_SYMBOLS.map(async (sym) => [sym, await getQuote(sym)] as const)
        );
        const quoteMap: Record<string, { c: number } | undefined> = Object.fromEntries(pairs);

        // Update state synchronously
        setStocks((prevStocks) =>
          prevStocks.map((stock) => {
            const quote = quoteMap[stock.symbol];
            if (!quote || typeof quote.c !== "number") return stock;
            const newPrice = Number(quote.c.toFixed(2));
            const base = stock.data[0]?.value ?? newPrice;
            const change = Number((newPrice - base).toFixed(2));
            const changePercent = Number(((change / base) * 100).toFixed(2));
            const newDataPoint = {
              time: new Date().toLocaleTimeString("en-US", {
                hour12: false,
                hour: "2-digit",
                minute: "2-digit",
              }),
              value: newPrice,
            };
            const updatedData = [...stock.data.slice(1), newDataPoint];
            return { ...stock, price: newPrice, change, changePercent, data: updatedData };
          })
        );
      } catch (e) {
        setError("Failed to fetch live stock data from Finnhub.");
        clearInterval(interval);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [apiReady]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stocks.map((stock) => (
          <Card
            key={stock.symbol}
            className="bg-card border-border hover:bg-accent/50 transition-colors"
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <span className="text-foreground font-semibold">
                      {stock.symbol}
                    </span>
                    <div
                      className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                        stock.change >= 0
                          ? "bg-green-500/20 text-green-400 border border-green-500/30"
                          : "bg-red-500/20 text-red-400 border border-red-500/30"
                      }`}
                    >
                      {stock.change >= 0 ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      <span>
                        {stock.changePercent >= 0 ? "+" : ""}
                        {stock.changePercent}%
                      </span>
                    </div>
                  </div>
                  <p className="text-muted-foreground text-sm mt-1 truncate">
                    {stock.name}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-foreground font-semibold text-lg">
                    ${stock.price}
                  </div>
                  <div
                    className={`text-sm font-medium ${
                      stock.change >= 0
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >
                    {stock.change >= 0 ? "+" : ""}$
                    {stock.change}
                  </div>
                </div>
              </div>

              <div className="h-16 w-full bg-muted/20 rounded-md p-2">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={stock.data}>
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke={
                        stock.change >= 0
                          ? "#10b981"
                          : "#ef4444"
                      }
                      strokeWidth={2}
                      dot={false}
                      animationDuration={500}
                    />
                    <XAxis hide />
                    <YAxis hide />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {error ? (
        <div className="text-center">
          <p className="text-red-500 text-sm">{error}</p>
        </div>
      ) : null}
    </div>
  );
}