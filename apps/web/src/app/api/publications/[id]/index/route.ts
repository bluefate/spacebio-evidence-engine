import { NextResponse } from "next/server";

const API_BASE_URL = process.env.SPACEBIO_API_URL ?? "http://localhost:8000";

export async function POST(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  try {
    const response = await fetch(
      `${API_BASE_URL}/publications/${encodeURIComponent(id)}/index`,
      { method: "POST", headers: { Accept: "application/json" } },
    );
    const payload = await response.json().catch(() => ({ detail: "Malformed upstream response." }));
    return NextResponse.json(payload, { status: response.status });
  } catch {
    return NextResponse.json(
      { detail: "Unable to reach the API. Start it with `make api`." },
      { status: 503 },
    );
  }
}
