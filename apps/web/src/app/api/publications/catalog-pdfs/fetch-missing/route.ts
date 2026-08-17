import { NextResponse } from "next/server";

const API_BASE_URL = process.env.SPACEBIO_API_URL ?? "http://localhost:8000";

export const maxDuration = 300;

export async function POST() {
  try {
    const response = await fetch(`${API_BASE_URL}/publications/catalog-pdfs/fetch-missing`, {
      method: "POST",
      headers: { Accept: "application/json" },
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
