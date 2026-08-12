import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.SPACEBIO_API_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON body." }, { status: 400 });
  }

  if (!isAskRequest(body)) {
    return NextResponse.json(
      { detail: "Request body must include a non-empty question." },
      { status: 422 },
    );
  }

  try {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        question: body.question.trim(),
        top_k: typeof body.top_k === "number" ? Math.min(Math.max(body.top_k, 1), 50) : 8,
      }),
    });

    const responseBody = await response.json().catch(() => ({ detail: "Malformed upstream response." }));
    return NextResponse.json(responseBody, { status: response.status });
  } catch {
    return NextResponse.json(
      {
        detail:
          "Unable to reach the grounded answer API. Start it with `make api` and ensure SPACEBIO_API_URL is correct.",
      },
      { status: 503 },
    );
  }
}

function isAskRequest(value: unknown): value is { question: string; top_k?: number } {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const obj = value as Record<string, unknown>;
  return typeof obj.question === "string" && obj.question.trim().length > 0;
}
