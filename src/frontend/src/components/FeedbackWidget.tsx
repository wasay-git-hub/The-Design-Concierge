"use client";

import React, { useState, useEffect } from "react";
import { MessageSquarePlus, X, Send, Loader2, CheckCircle2 } from "lucide-react";
import { usePathname } from "next/navigation";

export default function FeedbackWidget() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    category: "Feedback",
    message: ""
  });

  // Do not show widget on designer portal or login page
  if (pathname?.startsWith("/designer") || pathname?.startsWith("/login")) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      const data = new FormData();
      if (formData.name) data.append("name", formData.name);
      if (formData.email) data.append("email", formData.email);
      data.append("category", formData.category);
      data.append("message", formData.message);

      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      const res = await fetch(`${API_BASE}/api/feedback`, {
        method: "POST",
        body: data,
      });

      if (!res.ok) throw new Error("Failed to submit feedback.");
      
      setSuccess(true);
      setTimeout(() => {
        setIsOpen(false);
        setSuccess(false);
        setFormData({ name: "", email: "", category: "Feedback", message: "" });
      }, 3000);
      
    } catch (err: any) {
      setErrorMsg(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 z-50 p-4 bg-luxury-charcoal text-luxury-cream rounded-full shadow-2xl hover:bg-black transition-transform hover:-translate-y-1 ${isOpen ? 'scale-0' : 'scale-100'}`}
        title="Send Feedback"
      >
        <MessageSquarePlus className="w-6 h-6" />
      </button>

      {/* Modal Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-luxury-charcoal/40 backdrop-blur-sm p-4 sm:p-0">
          <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
            
            <div className="flex justify-between items-center p-5 border-b border-luxury-border bg-luxury-cream/30">
              <h2 className="font-serif text-lg font-bold text-luxury-charcoal flex items-center gap-2">
                <MessageSquarePlus className="w-5 h-5 text-luxury-brass" />
                Feedback & Support
              </h2>
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-md text-luxury-charcoal/50 hover:bg-luxury-lightGray transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6">
              {success ? (
                <div className="flex flex-col items-center justify-center py-8 text-center space-y-3">
                  <CheckCircle2 className="w-12 h-12 text-emerald-500 animate-bounce" />
                  <p className="font-semibold text-luxury-charcoal">Thank you!</p>
                  <p className="text-xs text-luxury-charcoal/60">Your message has been securely sent to our lead designers.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <p className="text-xs text-luxury-charcoal/70 leading-relaxed pb-2">
                    How is your experience with the digital assistant? Let us know if you encountered any issues or have suggestions.
                  </p>

                  {errorMsg && (
                    <div className="p-3 text-xs text-rose-600 bg-rose-50 border border-rose-200 rounded">
                      {errorMsg}
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-luxury-charcoal/60 mb-1">Name (Optional)</label>
                      <input 
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({...formData, name: e.target.value})}
                        className="w-full p-2.5 text-sm bg-luxury-lightGray/30 border border-luxury-border rounded focus:outline-none focus:border-luxury-brass transition"
                        placeholder="Jane Doe"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-luxury-charcoal/60 mb-1">Email (Optional)</label>
                      <input 
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                        className="w-full p-2.5 text-sm bg-luxury-lightGray/30 border border-luxury-border rounded focus:outline-none focus:border-luxury-brass transition"
                        placeholder="jane@example.com"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-luxury-charcoal/60 mb-1">Category</label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({...formData, category: e.target.value})}
                      className="w-full p-2.5 text-sm bg-luxury-lightGray/30 border border-luxury-border rounded focus:outline-none focus:border-luxury-brass transition"
                    >
                      <option value="Feedback">General Feedback</option>
                      <option value="Complaint">Report an Issue / Complaint</option>
                      <option value="Suggestion">Feature Suggestion</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-luxury-charcoal/60 mb-1">Message *</label>
                    <textarea 
                      required
                      rows={4}
                      value={formData.message}
                      onChange={(e) => setFormData({...formData, message: e.target.value})}
                      className="w-full p-2.5 text-sm bg-luxury-lightGray/30 border border-luxury-border rounded focus:outline-none focus:border-luxury-brass transition resize-none"
                      placeholder="Tell us what happened..."
                    ></textarea>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full mt-2 py-3 bg-luxury-charcoal hover:bg-black text-luxury-cream text-xs font-bold uppercase tracking-widest rounded transition flex justify-center items-center gap-2"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /> Send Message</>}
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
