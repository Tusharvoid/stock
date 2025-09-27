<<<<<<< HEAD
# Stock-and-Mutual-fund-Portfolio-Dashboard
for buy/sell stocks and Investing in mutual funds 
=======

  # Stock Portfolio Dashboard

  This is a code bundle for Stock Portfolio Dashboard. The original project is available at https://www.figma.com/design/rIkJw6nMDqTfgQtRIhvkY4/Stock-Portfolio-Dashboard.

## Running the code

Run `npm i` to install the dependencies.

Run `npm run dev` to start the development server.

### Live stock data (Finnhub)

The `src/components/real-time-stock-charts.tsx` component can fetch real quotes via Finnhub.

1. Create a `.env` file in the project root with:

```
VITE_FINNHUB_API_KEY=YOUR_FINNHUB_TOKEN
```

2. Restart the dev server after adding the key.

If the key is not set, the charts will use simulated data and a hint will be displayed.
  
>>>>>>> pushing my project
