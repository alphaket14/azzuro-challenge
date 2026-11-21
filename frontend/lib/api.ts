import type {
  InsightsTopicsResponse,
  Property,
  ReviewListResponse,
  TrendsResponse,
  WeeklySummaryResponse,
  PropertyBreakdown,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string, params?: Record<string, string | string[] | undefined>): Promise<T> {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value === undefined) continue;
      if (Array.isArray(value)) {
        for (const v of value) url.searchParams.append(key, v);
      } else {
        url.searchParams.set(key, value);
      }
    }
  }

  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`Request to ${url.pathname} failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getProperties(): Promise<Property[]> {
  return getJson<Property[]>("/api/properties");
}

export function getWeeklySummary(propertyId?: string): Promise<WeeklySummaryResponse> {
  return getJson<WeeklySummaryResponse>("/api/summary/weekly", { property_id: propertyId });
}

export function getPropertyBreakdown(): Promise<PropertyBreakdown[]> {
  return getJson<PropertyBreakdown[]>("/api/summary/properties");
}

export function getTopicInsights(): Promise<InsightsTopicsResponse> {
  return getJson<InsightsTopicsResponse>("/api/insights/topics");
}

export function getTrends(
  propertyIds: string[],
  dateFrom?: string,
  dateTo?: string
): Promise<TrendsResponse> {
  return getJson<TrendsResponse>("/api/insights/trends", {
    property_id: propertyIds[0],
    date_from: dateFrom,
    date_to: dateTo,
  });
}

export interface ReviewQuery {
  propertyIds?: string[];
  dateFrom?: string;
  dateTo?: string;
  sentiment?: string;
  topic?: string;
  page?: number;
  pageSize?: number;
}

export function getReviews(query: ReviewQuery): Promise<ReviewListResponse> {
  return getJson<ReviewListResponse>("/api/reviews", {
    property_id: query.propertyIds,
    date_from: query.dateFrom,
    date_to: query.dateTo,
    sentiment: query.sentiment,
    topic: query.topic,
    page: query.page ? String(query.page) : undefined,
    page_size: query.pageSize ? String(query.pageSize) : undefined,
  });
}
