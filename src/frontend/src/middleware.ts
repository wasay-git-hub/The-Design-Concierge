import { withAuth } from "next-auth/middleware";

// This file acts as the Bouncer for our Next.js application!
export default withAuth({
  pages: {
    // We now route unauthenticated users to our custom, beautiful login screen!
    signIn: "/login",
  },
});

// This is the Bouncer's rule list. 
// It tells the server exactly which rooms to lock the door on.
export const config = {
  // The matcher below says: "Only require authentication if the URL starts with /designer"
  // This means the homepage (/) remains completely public so clients can submit onboarding forms!
  matcher: ["/designer/:path*"],
};
