import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";

// NextAuth Configuration
export const authOptions = {
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
      
      // 2. Split them by comma and remove spaces (e.g. "boss@agency.com, dev@agency.com")
      const allowedEmails = allowedString.split(",").map(email => email.trim());
      
      // 3. Check if the person trying to log in is on the list
      if (user.email && allowedEmails.includes(user.email)) {
        return true; // Access Granted!
      }
      
      console.warn(`Unauthorized login attempt from: ${user.email}`);
      return false; // Access Denied! Kicks them to a default Error screen.
    },
  },
  // We define a secret to encrypt the session cookies
  secret: process.env.NEXTAUTH_SECRET,
};

// Next.js App Router requires us to export the handler as both GET and POST
const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
