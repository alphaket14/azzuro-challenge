import { FilterBar } from "@/components/FilterBar";
import { InsightsPanel } from "@/components/InsightsPanel";
import { KpiCards } from "@/components/KpiCards";
import { PropertyBreakdownTable } from "@/components/PropertyBreakdownTable";
import { ReviewFeed } from "@/components/ReviewFeed";
import { TrendChart } from "@/components/TrendChart";
import { FilterProvider } from "@/lib/filterStore";

export default function Home() {
  return (
    <FilterProvider>
      <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
        <header>
          <h1 className="text-2xl font-semibold text-gray-900">Azzurro Hotels — Review Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Guest sentiment, property performance, and recurring operational issues from Booking.com reviews.
          </p>
        </header>

        <FilterBar />

        <KpiCards />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <PropertyBreakdownTable />
          <InsightsPanel />
        </div>

        <TrendChart />

        <ReviewFeed />
      </main>
    </FilterProvider>
  );
}
