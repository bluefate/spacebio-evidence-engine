import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.SPACEBIO_API_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON body." }, { status: 400 });
  }
  try {
    const response = await fetch(`${API_BASE_URL}/publications/from-doi`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
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
