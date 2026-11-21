import { SentimentBadge, TopicBadge } from "./Badge";
import type { Review } from "@/lib/types";

export function ReviewCard({ review }: { review: Review }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <span className="font-medium text-gray-900">{review.reviewer_name ?? "Anonymous guest"}</span>
          {review.reviewer_country && <span className="ml-2 text-sm text-gray-400">{review.reviewer_country}</span>}
        </div>
        <div className="flex items-center gap-2">
          {review.rating_raw !== null && (
            <span className="rounded bg-gray-900 px-2 py-0.5 text-xs font-semibold text-white">
              {review.rating_raw.toFixed(1)}/10
            </span>
          )}
          <SentimentBadge sentiment={review.sentiment} />
        </div>
      </div>

      <div className="mt-2 text-sm text-gray-500">
        {review.property_name}
        {review.review_date && <> · {review.review_date}</>}
        {review.room_type && <> · {review.room_type}</>}
        {review.length_of_stay && <> · {review.length_of_stay}</>}
      </div>

      {review.review_title && <div className="mt-2 font-medium text-gray-800">{review.review_title}</div>}

      {review.positive_text && (
        <p className="mt-1 text-sm text-gray-700">
          <span className="font-medium text-green-700">Liked: </span>
          {review.positive_text}
        </p>
      )}
      {review.negative_text && (
        <p className="mt-1 text-sm text-gray-700">
          <span className="font-medium text-red-700">Disliked: </span>
          {review.negative_text}
        </p>
      )}

      {review.topics.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {review.topics.map((t) => (
            <TopicBadge key={t.topic} topic={t.topic} />
          ))}
        </div>
      )}
    </div>
  );
}
