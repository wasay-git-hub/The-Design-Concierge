import { NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";

export async function GET(request: Request) {
  // 1. Check the Bouncer's VIP List
  const session = await getServerSession(authOptions);
  
  if (!session) {
    return NextResponse.json({ error: "Unauthorized access. Google Login required." }, { status: 401 });
  }

  // 2. The Secret Handshake
  const backendUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  try {
    const res = await fetch(`${backendUrl}/api/feedback`, {
      headers: {
        "x-api-key": process.env.BACKEND_API_KEY || "super-secret-key-123",
      },
      cache: "no-store",
    });
    
    if (!res.ok) {
      throw new Error(`Python Backend returned ${res.status}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Proxy Error:", error);
    return NextResponse.json({ error: "Failed to connect to Python backend" }, { status: 500 });
  }
}
