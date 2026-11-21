export interface Property {
  id: string;
  name: string;
  booking_url: string;
}

export interface Topic {
  topic: string;
  confidence: number;
}

export interface Review {
  id: number;
  property_id: string;
  property_name: string;
  reviewer_name: string | null;
  reviewer_country: string | null;
  rating_raw: number | null;
  rating_normalized: number | null;
  review_title: string | null;
  positive_text: string | null;
  negative_text: string | null;
  full_text: string;
  review_date: string | null;
  room_type: string | null;
  length_of_stay: string | null;
  sentiment: "positive" | "neutral" | "negative";
  topics: Topic[];
}

export interface ReviewListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Review[];
}

export interface WeekSummary {
  start: string;
  end: string;
  avg_rating: number | null;
  review_count: number;
}

export interface WeeklySummaryResponse {
  current_week: WeekSummary;
  previous_week: WeekSummary;
  delta: number | null;
  delta_pct: number | null;
}

export interface PropertyBreakdown {
  property_id: string;
  property_name: string;
  avg_rating: number | null;
  review_count: number;
  prev_avg_rating: number | null;
  delta: number | null;
}

export interface TopicInsight {
  topic: string;
  negative_mentions: number;
  negative_total: number;
  pct_of_negative: number;
}

export interface InsightsTopicsResponse {
  period: { start: string; end: string };
  overall: TopicInsight[];
  by_property: Record<string, TopicInsight[]>;
  headline_callouts: string[];
}

export interface TrendBucket {
  period_start: string;
  positive: number;
  neutral: number;
  negative: number;
}

export interface TrendsResponse {
  buckets: TrendBucket[];
}

export interface ReviewFilters {
  propertyIds: string[];
  dateFrom: string;
  dateTo: string;
}
