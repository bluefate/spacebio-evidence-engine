import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.SPACEBIO_API_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const form = await request.formData();
    const response = await fetch(`${API_BASE_URL}/publications/from-pdf`, {
      method: "POST",
      body: form,
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
