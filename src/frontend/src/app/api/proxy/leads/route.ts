import { NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";

export async function GET(request: Request) {
  // 1. Check the Bouncer's VIP List
  // We use getServerSession to guarantee this user successfully logged in via Google.
  const session = await getServerSession(authOptions);
  
  if (!session) {
    // If they aren't logged in, immediately block the request.
    return NextResponse.json({ error: "Unauthorized access. Google Login required." }, { status: 401 });
  }

  // 2. The Secret Handshake
  // Because the user is verified, Next.js will now securely talk to the Python Backend.
  // We secretly attach the BACKEND_API_KEY so Python knows it's an official request, 
  // not a random hacker on the internet.
  
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  try {
    const res = await fetch(`${backendUrl}/api/leads`, {
      headers: {
        "x-api-key": process.env.BACKEND_API_KEY || "super-secret-key-123",
      },
      // We disable caching so the designer always gets the freshest leads
      cache: "no-store",
    });
    
    if (!res.ok) {
      throw new Error(`Python Backend returned ${res.status}`);
    }

    const data = await res.json();
    
    // 3. Hand the data back to the browser
    return NextResponse.json(data);
  } catch (error) {
    console.error("Proxy Error:", error);
    return NextResponse.json({ error: "Failed to connect to Python backend" }, { status: 500 });
  }
}
