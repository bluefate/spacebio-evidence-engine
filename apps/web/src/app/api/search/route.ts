import { NextRequest, NextResponse } from "next/server";

import { searchStoredCorpus } from "@/data/search";

export function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.get("q") ?? "";
  const limitParam = request.nextUrl.searchParams.get("limit");
  const parsedLimit = limitParam ? Number.parseInt(limitParam, 10) : 20;
  const limit = Number.isFinite(parsedLimit) ? Math.min(Math.max(parsedLimit, 1), 50) : 20;

  return NextResponse.json(searchStoredCorpus(query, limit));
}
