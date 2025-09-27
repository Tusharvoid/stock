import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "./ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import { Badge } from "./ui/badge";
import { TrendingUp, TrendingDown } from "lucide-react";

export interface Holding {
  symbol: string;
  name: string;
  type: "stock" | "mutual-fund";
  shares: number;
  currentPrice: number;
  marketValue: number;
  dayChange: number;
  dayChangePercent: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
}

interface HoldingsTableProps {
  holdings: Holding[];
  title: string;
}

export function HoldingsTable({
  holdings,
  title,
}: HoldingsTableProps) {
  return (
    <Card className="bg-gray-900/50 border-gray-700 backdrop-blur-md">
      <CardHeader>
        <CardTitle className="text-white">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Symbol</TableHead>
              <TableHead>Name</TableHead>
              <TableHead className="text-right">
                Shares
              </TableHead>
              <TableHead className="text-right">
                Price
              </TableHead>
              <TableHead className="text-right">
                Market Value
              </TableHead>
              <TableHead className="text-right">
                Day Change
              </TableHead>
              <TableHead className="text-right">
                Total Gain/Loss
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {holdings.map((holding) => {
              const isDayPositive = holding.dayChange >= 0;
              const isTotalPositive =
                holding.totalGainLoss >= 0;

              return (
                <TableRow key={holding.symbol}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span>{holding.symbol}</span>
                      <Badge
                        variant={
                          holding.type === "stock"
                            ? "default"
                            : "secondary"
                        }
                      >
                        {holding.type === "stock"
                          ? "Stock"
                          : "Fund"}
                      </Badge>
                    </div>
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate">
                    {holding.name}
                  </TableCell>
                  <TableCell className="text-right">
                    {holding.shares.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right">
                    ${holding.currentPrice.toFixed(2)}
                  </TableCell>
                  <TableCell className="text-right">
                    ${holding.marketValue.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div
                      className={`flex items-center justify-end gap-1 ${isDayPositive ? "text-green-600" : "text-red-600"}`}
                    >
                      {isDayPositive ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      <span>
                        {isDayPositive ? "+" : ""}$
                        {holding.dayChange.toFixed(2)}
                      </span>
                      <span className="text-xs">
                        ({isDayPositive ? "+" : ""}
                        {holding.dayChangePercent.toFixed(2)}%)
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <div
                      className={`flex items-center justify-end gap-1 ${isTotalPositive ? "text-green-600" : "text-red-600"}`}
                    >
                      {isTotalPositive ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      <span>
                        {isTotalPositive ? "+" : ""}$
                        {holding.totalGainLoss.toFixed(2)}
                      </span>
                      <span className="text-xs">
                        ({isTotalPositive ? "+" : ""}
                        {holding.totalGainLossPercent.toFixed(
                          2,
                        )}
                        %)
                      </span>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}