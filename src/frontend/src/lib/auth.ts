import { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";

// NextAuth Configuration Options
export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
  ],
  callbacks: {
    // This is the Security Checkpoint!
    async signIn({ user }: { user: any }) {
      // 1. Get the list of allowed emails from our .env file
      const allowedString = process.env.ALLOWED_EMAILS || "";
      
      // 2. Split them by comma and remove spaces
      const allowedEmails = allowedString.split(",").map(email => email.trim());
      
      // 3. Check if the person trying to log in is on the list
      if (user.email && allowedEmails.includes(user.email)) {
        return true; // Access Granted!
      }
      
      console.warn(`Unauthorized login attempt from: ${user.email}`);
      return false; // Access Denied!
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
};
