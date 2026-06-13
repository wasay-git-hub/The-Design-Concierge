"use client";

import React, { useState, useRef, useEffect } from "react";
import { 
  Sparkles, ArrowRight, Upload, Loader2, MessageSquare, 
  MapPin, CheckCircle2, FileDown, DollarSign, Maximize2, RefreshCw
} from "lucide-react";

const API_BASE = "http://localhost:8000";

interface Message {
  role: "user" | "assistant";
  content: string;
  visual_options?: { id: string; label: string; url: string }[];
}

interface VisionAnalysis {
  architectural_bones?: string;
  lighting_profile?: string;
  current_style?: string;
  estimated_dimensions?: string;
  potential_pain_points?: string;
}

export default function Home() {
  // Navigation & Flow state: onboarding -> upload -> chat -> complete
  const [step, setStep] = useState<"onboard" | "upload" | "chat" | "complete">("onboard");
  const [leadId, setLeadId] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>("");

  // Step 1 Form state
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    location: "Austin",
    room_type: "Living Room",
  });

  // Step 2 Upload state
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>("");
  const [visionAnalysis, setVisionAnalysis] = useState<VisionAnalysis | null>(null);

  // Step 3 Chat state
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<string>("");
  const [userInput, setUserInput] = useState<string>("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Step 4 Completion state
  const [summary, setSummary] = useState({
    design_dna: "",
    budget_min: 0,
    budget_max: 0,
    readiness_score: 0,
  });
  const [pdfUrl, setPdfUrl] = useState<string>("");

  // Auto-scroll on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory.length]);

  // 1. Submit basic onboarding form
  const handleOnboardSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    const formData = new FormData();
    Object.entries(form).forEach(([key, val]) => formData.append(key, val as string));

    try {
      const res = await fetch(`${API_BASE}/api/onboard`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to start session. Verify server is running.");
      const data = await res.json();

      setLeadId(data.lead_id);
      setChatHistory(data.chat_history);
      setCurrentQuestion(data.current_question);
      setStep("upload");
    } catch (err: any) {
      setErrorMsg(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  // File selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPhoto(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  // 2. Upload room photo for GPT-4o Vision API
  const handlePhotoUpload = async () => {
    if (!photo) return;
    setLoading(true);
    setErrorMsg("");

    const formData = new FormData();
    formData.append("lead_id", leadId);
    formData.append("file", photo);

    try {
      const res = await fetch(`${API_BASE}/api/upload-photo`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to upload image.");
      const data = await res.json();

      setChatHistory(data.chat_history);
      setVisionAnalysis(data.vision_analysis);
      setCurrentQuestion(data.current_question);
      setStep("chat");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to analyze image.");
    } finally {
      setLoading(false);
    }
  };

  // 3. Send chat response to Digital Assistant
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || loading) return;
    
    const messageToSubmit = userInput.trim();
    setUserInput("");
    await submitChatMessage(messageToSubmit);
  };

  const submitChatMessage = async (userMessage: string) => {
    setLoading(true);
    setErrorMsg("");

    // Optimistically update frontend UI
    const updatedHistory = [...chatHistory, { role: "user" as const, content: userMessage }];
    setChatHistory(updatedHistory);

    const formData = new FormData();
    formData.append("lead_id", leadId);
    formData.append("message", userMessage);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Connection failed.");
      const data = await res.json();

      setChatHistory(data.chat_history);
      setCurrentQuestion(data.current_question);

      if (data.is_complete) {
        setSummary({
          design_dna: data.lead_summary.design_dna || "",
          budget_min: data.lead_summary.budget_min ?? 0,
          budget_max: data.lead_summary.budget_max ?? 0,
          readiness_score: data.lead_summary.readiness_score ?? 0,
        });
        setStep("complete");
        // Trigger PDF generation in the background automatically
        triggerPdfGeneration();
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to deliver message.");
    } finally {
      setLoading(false);
    }
  };

  // 4. PDF Compilation trigger
  const triggerPdfGeneration = async () => {
    const formData = new FormData();
    formData.append("lead_id", leadId);

    try {
      const res = await fetch(`${API_BASE}/api/generate-report`, {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setPdfUrl(`${API_BASE}${data.pdf_url}`);
      }
    } catch (err) {
      console.error("Error generating PDF:", err);
    }
  };

  const handleReset = () => {
    setStep("onboard");
    setChatHistory([]);
    setPhoto(null);
    setPhotoPreview("");
    setLeadId("");
    setErrorMsg("");
    setLoading(false);
    setForm({ name: "", email: "", phone: "", location: "Austin", room_type: "Living Room" });
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Premium Navbar */}
      <header className="border-b border-luxury-border bg-white py-4 px-6 md:px-12 flex justify-between items-center sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-luxury-brass" />
          <span className="font-serif text-lg md:text-xl font-bold tracking-widest text-luxury-charcoal">
            THE DESIGN CONCIERGE
          </span>
        </div>
        <div className="flex items-center gap-6">
          {step !== "onboard" && (
            <button 
              onClick={handleReset}
              className="text-xs uppercase tracking-widest text-luxury-charcoal hover:text-luxury-brass font-semibold transition flex items-center gap-1"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Start Over
            </button>
          )}
          <a 
            href="/designer" 
            className="text-xs uppercase tracking-widest text-luxury-brass hover:text-luxury-charcoal font-semibold transition"
          >
            Designer Portal
          </a>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 flex justify-center items-center p-4 md:p-12">
        <div className="w-full max-w-4xl bg-white border border-luxury-border rounded-xl shadow-sm p-6 md:p-10 flex flex-col md:flex-row gap-8 min-h-[500px]">
          
          {/* STEP 1: INITIAL ONBOARDING FORM */}
          {step === "onboard" && (
            <div className="w-full flex flex-col justify-center animate-fade-in-up">
              <div className="max-w-xl mx-auto w-full">
                <span className="text-xs uppercase tracking-widest text-luxury-brass font-bold mb-2 block">
                  Phase 01 — Executive Welcome
                </span>
                <h1 className="font-serif text-3xl md:text-4xl text-luxury-charcoal font-semibold mb-4">
                  Welcome to The Design Concierge
                </h1>
                <p className="text-sm text-luxury-charcoal/70 mb-8 leading-relaxed">
                  We represent a Digital Junior Designer program designed
                  to assess your architectural layouts and establish your client briefing profile 
                  prior to your structural interior designer consultation.
                </p>

                {errorMsg && (
                  <div className="bg-red-50 text-red-700 text-xs p-3 rounded border border-red-100 mb-6">
                    {errorMsg}
                  </div>
                )}

                <form onSubmit={handleOnboardSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-semibold text-luxury-charcoal/80 mb-1 block">Your Name</label>
                      <input 
                        type="text" 
                        required
                        className="w-full px-4 py-2 border border-luxury-border rounded text-sm focus:outline-none focus:border-luxury-brass" 
                        placeholder="Elizabeth Vance"
                        value={form.name}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm({...form, name: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-luxury-charcoal/80 mb-1 block">Email Address</label>
                      <input 
                        type="email" 
                        required
                        className="w-full px-4 py-2 border border-luxury-border rounded text-sm focus:outline-none focus:border-luxury-brass" 
                        placeholder="elizabeth@vance.com"
                        value={form.email}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm({...form, email: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="text-xs font-semibold text-luxury-charcoal/80 mb-1 block">Phone Number</label>
                      <input 
                        type="tel" 
                        required
                        className="w-full px-4 py-2 border border-luxury-border rounded text-sm focus:outline-none focus:border-luxury-brass" 
                        placeholder="(305) 555-0199"
                        value={form.phone}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm({...form, phone: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-luxury-charcoal/80 mb-1 block">Project Location</label>
                      <select 
                        className="w-full px-4 py-2 border border-luxury-border rounded text-sm bg-white focus:outline-none focus:border-luxury-brass"
                        value={form.location}
                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setForm({...form, location: e.target.value})}
                      >
                        <option value="Miami">Miami, FL</option>
                        <option value="Austin">Austin, TX</option>
                        <option value="Scottsdale">Scottsdale, AZ</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-luxury-charcoal/80 mb-1 block">Target Room</label>
                      <select 
                        className="w-full px-4 py-2 border border-luxury-border rounded text-sm bg-white focus:outline-none focus:border-luxury-brass"
                        value={form.room_type}
                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setForm({...form, room_type: e.target.value})}
                      >
                        <option value="Living Room">Living Room</option>
                        <option value="Kitchen">Kitchen</option>
                        <option value="Bedroom">Bedroom</option>
                        <option value="Bathroom">Bathroom</option>
                      </select>
                    </div>
                  </div>

                  <button 
                    type="submit" 
                    disabled={loading}
                    className="w-full md:w-auto px-6 py-3 bg-luxury-charcoal hover:bg-luxury-brass text-white text-xs font-bold uppercase tracking-widest rounded transition flex items-center justify-center gap-2 mt-6"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Initiate Consultation"}
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* STEP 2: PHOTO UPLOAD AND VISION ANALYSIS */}
          {step === "upload" && (
            <div className="w-full flex flex-col justify-center animate-fade-in-up max-w-xl mx-auto">
              <span className="text-xs uppercase tracking-widest text-luxury-brass font-bold mb-2 block">
                Phase 02 — Space Structural Analysis
              </span>
              <h2 className="font-serif text-2xl md:text-3xl text-luxury-charcoal font-semibold mb-4">
                Share a Snapshot of Your Room
              </h2>
              <p className="text-sm text-luxury-charcoal/70 mb-8 leading-relaxed">
                Rather than asking a checklist of questions, our AI model reads your room's structural
                bones, natural lighting orientation, and current styling constraints from a photo.
              </p>

              {errorMsg && (
                <div className="bg-red-50 text-red-700 text-xs p-3 rounded border border-red-100 mb-6">
                  {errorMsg}
                </div>
              )}

              <div className={`border-2 border-dashed rounded-lg p-8 text-center transition relative ${loading ? 'border-luxury-border/50 bg-luxury-lightGray opacity-75' : 'border-luxury-border hover:border-luxury-brass bg-luxury-cream/30 cursor-pointer'}`}>
                <input 
                  type="file" 
                  accept="image/*"
                  onChange={handleFileChange}
                  disabled={loading}
                  className={`absolute inset-0 opacity-0 ${loading ? 'cursor-not-allowed' : 'cursor-pointer'}`}
                />
                
                {photoPreview ? (
                  <div className="space-y-4">
                    <img 
                      src={photoPreview} 
                      alt="Room Preview" 
                      className="max-h-48 mx-auto rounded object-cover border border-luxury-border"
                    />
                    <p className="text-xs text-luxury-charcoal/60 font-semibold">{photo?.name}</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2">
                    <Upload className="w-10 h-10 text-luxury-brass mb-2" />
                    <p className="text-sm font-semibold">Select your room photo</p>
                    <p className="text-xs text-luxury-charcoal/50">Supports JPEG, PNG, WEBP, GIF (Max 10MB)</p>
                  </div>
                )}
              </div>

              <div className="mt-8 flex gap-4">
                <button 
                  onClick={handlePhotoUpload}
                  disabled={!photo || loading}
                  className="px-6 py-3 bg-luxury-charcoal hover:bg-luxury-brass text-white text-xs font-bold uppercase tracking-widest rounded transition flex items-center gap-2 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Analyzing structural bones...
                    </>
                  ) : (
                    <>
                      Analyze Layout
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: REFINEMENT CHAT */}
          {step === "chat" && (
            <>
              {/* Left Column: Room Analysis Recap */}
              <div className="w-full md:w-1/3 border-b md:border-b-0 md:border-r border-luxury-border pb-6 md:pb-0 md:pr-6 flex flex-col justify-between">
                <div>
                  <h3 className="font-serif text-xl font-semibold text-luxury-charcoal mb-4">Detected Bones</h3>
                  {photoPreview && (
                    <img 
                      src={photoPreview} 
                      alt="Room" 
                      className="w-full h-32 object-cover rounded border border-luxury-border mb-4"
                    />
                  )}
                  {visionAnalysis && (
                    <div className="space-y-4 text-xs">
                      <div>
                        <span className="font-semibold text-luxury-brass block uppercase tracking-wider">Structure & Molding</span>
                        <p className="text-luxury-charcoal/70 mt-1">{visionAnalysis.architectural_bones}</p>
                      </div>
                      <div>
                        <span className="font-semibold text-luxury-brass block uppercase tracking-wider">Natural Light Exposure</span>
                        <p className="text-luxury-charcoal/70 mt-1">{visionAnalysis.lighting_profile}</p>
                      </div>
                      <div>
                        <span className="font-semibold text-luxury-brass block uppercase tracking-wider">Current Layout Theme</span>
                        <p className="text-luxury-charcoal/70 mt-1">{visionAnalysis.current_style}</p>
                      </div>
                    </div>
                  )}
                </div>
                <div className="bg-luxury-cream p-3 rounded border border-luxury-border mt-4 text-[10px] text-luxury-charcoal/70 flex gap-2">
                  <MapPin className="w-4 h-4 text-luxury-brass shrink-0" />
                  <div>
                    Project: <span className="font-bold">{form.room_type}</span><br/>
                    Location: <span className="font-bold">{form.location}</span>
                  </div>
                </div>
              </div>

              {/* Right Column: Dynamic Interactive Onboarding Chat */}
              <div className="flex-1 flex flex-col min-h-[400px]">
                <div className="border-b border-luxury-border pb-3 mb-4 flex justify-between items-center">
                  <span className="text-xs uppercase tracking-widest text-luxury-brass font-bold flex items-center gap-1">
                    <MessageSquare className="w-4 h-4" />
                    Senior Design Assistant Refinement
                  </span>
                  {loading && <span className="text-[10px] text-luxury-brass animate-pulse">Assistant is thinking...</span>}
                </div>

                {/* Chat Message Thread */}
                <div className="flex-1 overflow-y-auto space-y-4 pr-2 max-h-[300px] mb-4 text-sm scroll-smooth">
                  {chatHistory.map((msg: Message, index: number) => (
                    <div 
                      key={index}
                      className={`p-3 rounded-lg max-w-[85%] ${
                        msg.role === "assistant" 
                          ? "bg-luxury-lightGray text-luxury-charcoal mr-auto" 
                          : "bg-luxury-charcoal text-white ml-auto"
                      }`}
                    >
                      <p className="leading-relaxed whitespace-pre-line text-xs">{msg.content}</p>
                      
                      {msg.visual_options && msg.visual_options.length > 0 && (
                        <div className="grid grid-cols-2 gap-3 mt-4">
                          {msg.visual_options.map((opt: { id: string; label: string; url: string }) => (
                            <div 
                              key={opt.id}
                              onClick={() => submitChatMessage(`I select the ${opt.label} style.`)}
                              className="group cursor-pointer rounded overflow-hidden border-2 border-transparent hover:border-luxury-brass transition relative"
                            >
                              <img src={`${API_BASE}${opt.url}`} alt={opt.label} className="w-full h-24 object-cover" />
                              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent group-hover:from-black/50 transition flex items-end p-2">
                                <span className="text-white text-[10px] font-bold uppercase tracking-wider drop-shadow-md">{opt.label}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {loading && (
                    <div className="p-3 rounded-lg max-w-[85%] bg-luxury-lightGray text-luxury-charcoal mr-auto flex gap-2 items-center">
                      <div className="w-2 h-2 rounded-full bg-luxury-brass/60 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 rounded-full bg-luxury-brass/60 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 rounded-full bg-luxury-brass/60 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  )}

                  <div ref={chatEndRef} />
                </div>

                {errorMsg && (
                  <div className="bg-red-50 text-red-700 text-xs p-2 rounded border border-red-100 mb-2 flex justify-between items-center">
                    <span>{errorMsg}</span>
                    <button onClick={() => setErrorMsg("")} className="px-2 py-1 bg-red-100 text-red-800 rounded hover:bg-red-200 ml-2">Dismiss</button>
                  </div>
                )}

                {/* Input Area */}
                <form onSubmit={handleSendMessage} className="flex gap-2">
                  <input 
                    type="text"
                    disabled={loading}
                    className="flex-1 px-4 py-2 border border-luxury-border rounded text-sm focus:outline-none focus:border-luxury-brass"
                    placeholder="Enter your design details..."
                    value={userInput}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUserInput(e.target.value)}
                  />
                  <button 
                    type="submit"
                    disabled={loading || !userInput.trim()}
                    className="px-4 py-2 bg-luxury-charcoal hover:bg-luxury-brass text-white text-xs font-bold uppercase tracking-widest rounded transition disabled:bg-gray-300"
                  >
                    Send
                  </button>
                </form>
              </div>
            </>
          )}

          {/* STEP 4: COMPLETION VIEW */}
          {step === "complete" && (
            <div className="w-full text-center py-10 animate-fade-in-up max-w-xl mx-auto flex flex-col items-center">
              <CheckCircle2 className="w-16 h-16 text-luxury-brass mb-4" />
              <span className="text-xs uppercase tracking-widest text-luxury-brass font-bold mb-2">
                Phase 04 — Onboarding Complete
              </span>
              <h2 className="font-serif text-3xl font-semibold text-luxury-charcoal mb-4">
                Your Project Brief is Ready
              </h2>
              <p className="text-sm text-luxury-charcoal/70 mb-8 max-w-md">
                We've combined your spatial data and vision preferences to compile your personalized project brief.
              </p>

              {/* Estimate Summary card */}
              <div className="w-full bg-luxury-cream border border-luxury-border rounded-lg p-6 flex flex-col items-center justify-center mb-8">
                <span className="text-[10px] uppercase tracking-wider text-luxury-brass block mb-1">Your Unique Design DNA</span>
                <span className="text-xl font-bold text-luxury-charcoal">{summary.design_dna}</span>
              </div>

              <p className="text-xs text-luxury-charcoal/60 max-w-sm text-center mx-auto">
                Your dedicated designer has received your full intelligence report and will be in touch shortly to schedule your consultation!
              </p>
            </div>
          )}

        </div>
      </main>

      {/* Luxury Footer */}
      <footer className="border-t border-luxury-border py-4 text-center text-[10px] tracking-wider text-luxury-charcoal/50 uppercase">
        © 2026 The Design Concierge. All rights reserved.
      </footer>
    </div>
  );
}
