"use client";

import { useEffect, useState } from "react";
import { getReviews } from "@/lib/api";
import { useFilters } from "@/lib/filterStore";
import type { Review } from "@/lib/types";
import { ReviewCard } from "./ReviewCard";

const PAGE_SIZE = 10;

export function ReviewFeed() {
  const { filters } = useFilters();
  const [sentiment, setSentiment] = useState<string>("");
  const [reviews, setReviews] = useState<Review[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPage(1);
    setReviews([]);
  }, [filters.propertyIds, filters.dateFrom, filters.dateTo, sentiment]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getReviews({
      propertyIds: filters.propertyIds.length ? filters.propertyIds : undefined,
      dateFrom: filters.dateFrom,
      dateTo: filters.dateTo,
      sentiment: sentiment || undefined,
      page,
      pageSize: PAGE_SIZE,
    })
      .then((res) => {
        setTotal(res.total);
        setReviews((prev) => (page === 1 ? res.items : [...prev, ...res.items]));
      })
      .catch(() => setError("Could not load reviews — check that the backend is running."))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filters.propertyIds, filters.dateFrom, filters.dateTo, sentiment]);

  const hasMore = reviews.length < total;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-sm font-semibold text-gray-700">
          Review feed {total > 0 && <span className="text-gray-400">({total})</span>}
        </h2>
        <div className="flex gap-2">
          {["", "positive", "neutral", "negative"].map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSentiment(s)}
              className={`rounded-full border px-3 py-1 text-xs capitalize transition-colors ${
                sentiment === s
                  ? "border-blue-600 bg-blue-600 text-white"
                  : "border-gray-300 bg-white text-gray-600 hover:border-blue-400"
              }`}
            >
              {s || "All"}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

      <div className="space-y-3">
        {reviews.map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </div>

      {reviews.length === 0 && !loading && !error && (
        <p className="text-sm text-gray-400">No reviews match the current filters.</p>
      )}

      {hasMore && (
        <button
          type="button"
          onClick={() => setPage((p) => p + 1)}
          disabled={loading}
          className="mt-4 w-full rounded-md border border-gray-300 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          {loading ? "Loading…" : "Load more"}
        </button>
      )}
    </div>
  );
}
