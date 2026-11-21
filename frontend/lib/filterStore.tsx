"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import type { ReviewFilters } from "./types";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function daysAgoIso(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

interface FilterContextValue {
  filters: ReviewFilters;
  setPropertyIds: (ids: string[]) => void;
  setDateFrom: (date: string) => void;
  setDateTo: (date: string) => void;
  reset: () => void;
}

const defaultFilters: ReviewFilters = {
  propertyIds: [],
  dateFrom: daysAgoIso(35),
  dateTo: todayIso(),
};

const FilterContext = createContext<FilterContextValue | null>(null);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [filters, setFilters] = useState<ReviewFilters>(defaultFilters);

  const value = useMemo<FilterContextValue>(
    () => ({
      filters,
      setPropertyIds: (ids) => setFilters((f) => ({ ...f, propertyIds: ids })),
      setDateFrom: (date) => setFilters((f) => ({ ...f, dateFrom: date })),
      setDateTo: (date) => setFilters((f) => ({ ...f, dateTo: date })),
      reset: () => setFilters(defaultFilters),
    }),
    [filters]
  );

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}

export function useFilters(): FilterContextValue {
  const ctx = useContext(FilterContext);
  if (!ctx) throw new Error("useFilters must be used within a FilterProvider");
  return ctx;
}
