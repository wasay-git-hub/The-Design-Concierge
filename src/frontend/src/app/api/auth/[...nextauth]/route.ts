import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth";

// Next.js App Router requires us to export the handler as both GET and POST
const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
