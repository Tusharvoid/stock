// Lightweight Finnhub REST helpers for Vite React app

const FINNHUB_BASE_URL = "https://finnhub.io/api/v1";

type HttpMethod = "GET" | "POST";

function getApiKey(): string | undefined {
  // Vite exposes env vars starting with VITE_
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const viteEnv = (import.meta as any).env;
  return viteEnv?.VITE_FINNHUB_API_KEY as string | undefined;
}

async function fetchJson<T>(path: string, params: Record<string, string | number | undefined> = {}, method: HttpMethod = "GET"): Promise<T> {
  const apiKey = getApiKey();
  const url = new URL(`${FINNHUB_BASE_URL}${path}`);
  const query: Record<string, string> = {};
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) query[key] = String(value);
  }
  if (apiKey) query["token"] = apiKey;
  Object.entries(query).forEach(([k, v]) => url.searchParams.set(k, v));

  const res = await fetch(url.toString(), { method });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Finnhub request failed ${res.status}: ${text}`);
  }
  return (await res.json()) as T;
}

export interface FinnhubQuoteResponse {
  c: number; // current price
  d: number | null; // change
  dp: number | null; // percent change
  h: number; // high
  l: number; // low
  o: number; // open
  pc: number; // previous close
  t?: number; // timestamp (sometimes provided)
}

export interface CandleResponse {
  c: number[]; // close prices
  h: number[];
  l: number[];
  o: number[];
  s: "ok" | "no_data";
  t: number[]; // unix times (seconds)
  v: number[];
}

export async function getQuote(symbol: string): Promise<FinnhubQuoteResponse | undefined> {
  const apiKey = getApiKey();
  if (!apiKey) return undefined; // allow caller to fallback to mock
  return await fetchJson<FinnhubQuoteResponse>("/quote", { symbol });
}

export async function getIntradayCandles(symbol: string, resolution: "1" | "5" | "15" | "30" | "60" = "5", rangeMinutes = 60): Promise<CandleResponse | undefined> {
  const apiKey = getApiKey();
  if (!apiKey) return undefined;
  const nowSec = Math.floor(Date.now() / 1000);
  const fromSec = nowSec - rangeMinutes * 60;
  return await fetchJson<CandleResponse>("/stock/candle", {
    symbol,
    resolution,
    from: fromSec,
    to: nowSec,
  });
}

export interface CompanyProfile2 {
  country?: string;
  currency?: string;
  exchange?: string;
  finnhubIndustry?: string;
  ipo?: string;
  logo?: string;
  marketCapitalization?: number;
  name?: string;
  phone?: string;
  shareOutstanding?: number;
  ticker?: string;
  weburl?: string;
}

export async function getCompanyProfile(symbol: string): Promise<CompanyProfile2 | undefined> {
  const apiKey = getApiKey();
  if (!apiKey) return undefined;
  return await fetchJson<CompanyProfile2>("/stock/profile2", { symbol });
}

export function isApiConfigured(): boolean {
  return Boolean(getApiKey());
}


