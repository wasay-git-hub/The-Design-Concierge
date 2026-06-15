"use client";

import { signIn } from "next-auth/react";
import { Sparkles, ArrowRight, Lock } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-luxury-charcoal bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-luxury-lightGray/10 via-luxury-charcoal to-black p-4">
      <div className="max-w-md w-full bg-white/5 backdrop-blur-xl border border-white/10 p-10 rounded-2xl shadow-2xl relative overflow-hidden group">
        
        {/* Subtle hover glow effect */}
        <div className="absolute -inset-1 bg-gradient-to-r from-luxury-brass to-luxury-cream opacity-0 group-hover:opacity-10 blur transition duration-1000"></div>
        
        <div className="relative text-center space-y-8 z-10">
          <div className="flex justify-center">
            <div className="p-4 bg-luxury-brass/10 rounded-full border border-luxury-brass/20 shadow-[0_0_30px_rgba(197,160,89,0.15)]">
              <Sparkles className="w-8 h-8 text-luxury-brass" />
            </div>
          </div>
          
          <div className="space-y-3">
            <h1 className="font-serif text-3xl font-bold tracking-wider text-white">Designer Portal</h1>
            <p className="text-luxury-cream/60 text-sm leading-relaxed max-w-sm mx-auto">
              Secure access is restricted to authorized interior design personnel and administration.
            </p>
          </div>

          <div className="pt-4">
            <button
              onClick={() => signIn("google", { callbackUrl: "/designer" })}
              className="w-full flex items-center justify-center gap-3 bg-white hover:bg-luxury-lightGray text-luxury-charcoal font-bold uppercase tracking-widest text-sm py-4 px-6 rounded-lg transition-all duration-300 transform hover:-translate-y-0.5 shadow-lg shadow-white/5"
            >
              <img src="https://www.svgrepo.com/show/475656/google-color.svg" className="w-5 h-5" alt="Google" />
              Sign in with Google
              <ArrowRight className="w-4 h-4 ml-2 opacity-50" />
            </button>
          </div>
          
          <div className="flex items-center justify-center gap-1.5 pt-4 text-[10px] text-white/30 uppercase tracking-widest">
            <Lock className="w-3 h-3" />
            <span>Protected by NextAuth Enterprise Security</span>
          </div>
        </div>
      </div>
    </div>
  );
}
