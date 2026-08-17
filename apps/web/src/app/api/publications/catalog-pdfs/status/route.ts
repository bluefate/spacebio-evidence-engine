import { NextResponse } from "next/server";

const API_BASE_URL = process.env.SPACEBIO_API_URL ?? "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/publications/catalog-pdfs/status`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    const payload = await response.json().catch(() => ({ detail: "Malformed upstream response." }));
    return NextResponse.json(payload, { status: response.status });
  } catch {
    return NextResponse.json(
      { detail: "Unable to reach the API. Start it with `make api`." },
      { status: 503 },
    );
  }
}
