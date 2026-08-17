import { NextRequest, NextResponse } from "next/server";

import { mergeInventoryAndIndexedSearch, searchStoredCorpus } from "@/data/search";

const API_BASE_URL = process.env.SPACEBIO_API_URL ?? "http://localhost:8000";

export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.get("q") ?? "";
  const limitParam = request.nextUrl.searchParams.get("limit");
  const parsedLimit = limitParam ? Number.parseInt(limitParam, 10) : 20;
  const limit = Number.isFinite(parsedLimit) ? Math.min(Math.max(parsedLimit, 1), 50) : 20;
  const inventory = searchStoredCorpus(query, limit);

  try {
    const upstream = await fetch(
      `${API_BASE_URL}/search?q=${encodeURIComponent(query)}&limit=${limit}`,
      { headers: { Accept: "application/json" } },
    );
    if (!upstream.ok) {
      return NextResponse.json(inventory);
    }
    const indexed = (await upstream.json()) as { source?: unknown; passages?: unknown };
    return NextResponse.json(mergeInventoryAndIndexedSearch(inventory, indexed));
  } catch {
    return NextResponse.json(inventory);
  }
}
