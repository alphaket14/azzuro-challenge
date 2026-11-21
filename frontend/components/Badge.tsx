const SENTIMENT_STYLES: Record<string, string> = {
  positive: "bg-green-100 text-green-800",
  neutral: "bg-gray-100 text-gray-700",
  negative: "bg-red-100 text-red-800",
};

export function SentimentBadge({ sentiment }: { sentiment: string }) {
  const style = SENTIMENT_STYLES[sentiment] ?? SENTIMENT_STYLES.neutral;
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${style}`}>
      {sentiment}
    </span>
  );
}

export function TopicBadge({ topic }: { topic: string }) {
  return (
    <span className="inline-block rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
      {topic.replace(/_/g, " ")}
    </span>
  );
}
