import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const chartData = [
  { date: "Jan", value: 85000 },
  { date: "Feb", value: 88200 },
  { date: "Mar", value: 84500 },
  { date: "Apr", value: 91800 },
  { date: "May", value: 89200 },
  { date: "Jun", value: 93500 },
  { date: "Jul", value: 97200 },
  { date: "Aug", value: 95800 },
  { date: "Sep", value: 102400 },
  { date: "Oct", value: 98900 },
  { date: "Nov", value: 105600 },
  { date: "Dec", value: 112300 }
];

export function PortfolioChart() {
  return (
    <Card className="col-span-full bg-gray-900/50 border-gray-700 backdrop-blur-md">
      <CardHeader>
        <CardTitle className="text-white">Portfolio Performance (12 Months)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey="date" 
              className="text-muted-foreground"
              fontSize={12}
            />
            <YAxis 
              className="text-muted-foreground"
              fontSize={12}
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip 
              formatter={(value) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
              labelStyle={{ color: 'var(--foreground)' }}
              contentStyle={{ 
                backgroundColor: 'var(--background)', 
                border: '1px solid var(--border)',
                borderRadius: '6px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="var(--foreground)" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: 'var(--foreground)' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}