"use client";

import React, { useState, useEffect } from "react";
import { 
  Sparkles, FileText, ArrowLeft, RefreshCw, Calendar, 
  User, Mail, Phone, MapPin, Gauge, Download, Home, Maximize2, Loader2 
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  room_type: string;
  area_sqft: number;
  scope_level: number;
  material_tier: number;
  budget_min: number;
  budget_max: number;
  readiness_score: number;
  timeline: string;
  decision_maker: string;
  vision_analysis: any;
  design_dna: string;
  status: string;
  pdf_path: string;
  created_at: string;
}

export default function DesignerDashboard() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>("");

  const fetchLeads = async (showRefreshIndicator = false) => {
    if (showRefreshIndicator) setRefreshing(true);
    setErrorMsg("");
    try {
      // PROXY PATTERN: Instead of hitting Python directly, we hit our own Next.js server!
      const res = await fetch(`/api/proxy/leads`);
      if (!res.ok) throw new Error("Could not retrieve leads from the database.");
      const data = await res.json();
      setLeads(data);
      
      // Keep selected lead sync'd if details refreshed
      if (selectedLead) {
        const updated = data.find((l: Lead) => l.id === selectedLead.id);
        if (updated) setSelectedLead(updated);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load leads.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  const getReadinessColor = (score: number) => {
    if (score >= 80) return "text-emerald-600 bg-emerald-50 border-emerald-200";
    if (score >= 60) return "text-amber-600 bg-amber-50 border-amber-200";
    return "text-rose-600 bg-rose-50 border-rose-200";
  };

  const getScopeName = (level: number) => {
    switch (level) {
      case 1: return "Styling & Furnishings";
      case 2: return "Soft Remodel (Cosmetic)";
      case 3: return "Full Gut Renovation";
      default: return "Interior Design";
    }
  };

  const getMaterialName = (level: number) => {
    switch (level) {
      case 1: return "Premium (High Street)";
      case 2: return "Luxury (Custom Millwork)";
      case 3: return "Ultra-Luxury (Bespoke)";
      default: return "Custom Luxury";
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-luxury-lightGray/40">
      {/* Dashboard Navbar */}
      <header className="border-b border-luxury-border bg-white py-4 px-6 md:px-12 flex justify-between items-center sticky top-0 z-40 shadow-sm">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-luxury-brass" />
          <span className="font-serif text-lg font-bold tracking-widest text-luxury-charcoal">
            DESIGNER PORTAL
          </span>
          <span className="text-[10px] bg-luxury-brass/15 text-luxury-brass px-2 py-0.5 rounded font-bold uppercase tracking-wider ml-2">
            Lead Management
          </span>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={() => fetchLeads(true)}
            disabled={refreshing}
            className="p-2 border border-luxury-border rounded hover:bg-luxury-cream transition text-luxury-charcoal/60"
            title="Refresh Leads"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin text-luxury-brass" : ""}`} />
          </button>
          <a 
            href="/" 
            className="flex items-center gap-1 text-xs uppercase tracking-widest text-luxury-charcoal hover:text-luxury-brass font-semibold transition"
          >
            <Home className="w-4 h-4" />
            Client View
          </a>
        </div>
      </header>

      {/* Workspace */}
      <main className="flex-1 flex flex-col md:flex-row max-w-7xl mx-auto w-full p-4 md:p-8 gap-6">
        
        {/* Left Side: Leads List */}
        <div className="w-full md:w-2/5 flex flex-col bg-white border border-luxury-border rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b border-luxury-border flex justify-between items-center bg-luxury-cream/30">
            <h2 className="font-serif text-lg font-semibold text-luxury-charcoal">Pre-Discovery Leads</h2>
            <span className="text-xs text-luxury-charcoal/60 font-semibold">{leads.length} Leads</span>
          </div>

          {errorMsg && (
            <div className="bg-red-50 text-red-700 text-xs p-3 m-4 rounded border border-red-100">
              {errorMsg}
            </div>
          )}

          {loading ? (
            <div className="flex-1 flex items-center justify-center p-12">
              <Loader2 className="w-8 h-8 animate-spin text-luxury-brass" />
            </div>
          ) : leads.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
              <FileText className="w-12 h-12 text-luxury-border mb-3" />
              <p className="text-sm font-semibold">No Leads Found</p>
              <p className="text-xs text-luxury-charcoal/50 mt-1">
                Completed pre-discovery sessions will appear here.
              </p>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto divide-y divide-luxury-border max-h-[600px]">
              {leads.map((lead) => (
                <div 
                  key={lead.id}
                  onClick={() => setSelectedLead(lead)}
                  className={`p-4 cursor-pointer hover:bg-luxury-lightGray/30 transition flex justify-between items-center ${
                    selectedLead?.id === lead.id ? "bg-luxury-cream/60 border-l-4 border-l-luxury-brass" : ""
                  }`}
                >
                  <div className="space-y-1 pr-2">
                    <div className="font-semibold text-sm text-luxury-charcoal">{lead.name || "Anonymous Client"}</div>
                    <div className="text-[10px] text-luxury-charcoal/60 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-luxury-brass" /> {lead.location} • {lead.room_type}
                    </div>
                    <div className="text-[10px] text-luxury-charcoal/40">
                      {new Date(lead.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="text-right flex flex-col items-end gap-1.5">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getReadinessColor(lead.readiness_score)}`}>
                      R: {lead.readiness_score}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Side: Detail Lead Review and Report Drawer */}
        <div className="flex-1 bg-white border border-luxury-border rounded-xl shadow-sm overflow-hidden flex flex-col">
          {selectedLead ? (
            <div className="flex-1 flex flex-col">
              
              {/* Detail Header */}
              <div className="p-6 border-b border-luxury-border flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-luxury-cream/10">
                <div>
                  <h2 className="font-serif text-2xl font-semibold text-luxury-charcoal">
                    {selectedLead.name}
                  </h2>
                  <p className="text-xs text-luxury-charcoal/60 flex items-center gap-1 mt-1">
                    <Calendar className="w-3.5 h-3.5 text-luxury-brass" />
                    Onboarded: {new Date(selectedLead.created_at).toLocaleString()}
                  </p>
                </div>
                {selectedLead.pdf_path && (
                  <a 
                    href={`${API_BASE}/static/reports/report_${selectedLead.id}.pdf`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full md:w-auto px-4 py-2 border border-luxury-brass bg-white hover:bg-luxury-cream text-luxury-brass text-xs font-bold uppercase tracking-widest rounded transition flex items-center justify-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Download Intelligence Report
                  </a>
                )}
              </div>

              {/* Detail Content Grid */}
              <div className="p-6 overflow-y-auto max-h-[500px] space-y-6">
                
                {/* 2 Columns metrics info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-luxury-cream border border-luxury-border rounded-lg p-4 flex flex-col justify-center">
                    <span className="text-[10px] uppercase font-bold text-luxury-brass tracking-wider">Readiness Score</span>
                    <div className="flex items-center gap-2 mt-1">
                      <Gauge className="w-5 h-5 text-luxury-brass" />
                      <span className="text-xl font-bold">{selectedLead.readiness_score}/100</span>
                    </div>
                  </div>
                  <div className="bg-luxury-cream border border-luxury-border rounded-lg p-4 flex flex-col justify-center">
                    <span className="text-[10px] uppercase font-bold text-luxury-brass tracking-wider">Design DNA Style</span>
                    <span className="text-base font-bold text-luxury-charcoal mt-1 truncate">{selectedLead.design_dna || "Not Assessment Complete"}</span>
                  </div>
                </div>

                {/* Left/Right Detail Blocks */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  {/* Contacts & Specifications */}
                  <div className="space-y-4">
                    <h3 className="font-serif text-base font-bold border-b border-luxury-border pb-1 text-luxury-charcoal">
                      Lead Details & Specs
                    </h3>
                    <div className="space-y-2.5 text-xs">
                      <div className="flex items-center gap-2 text-luxury-charcoal/80">
                        <User className="w-4 h-4 text-luxury-brass shrink-0" />
                        <span>Name: <span className="font-semibold text-luxury-charcoal">{selectedLead.name}</span></span>
                      </div>
                      <div className="flex items-center gap-2 text-luxury-charcoal/80">
                        <Mail className="w-4 h-4 text-luxury-brass shrink-0" />
                        <span>Email: <span className="font-semibold text-luxury-charcoal">{selectedLead.email}</span></span>
                      </div>
                      <div className="flex items-center gap-2 text-luxury-charcoal/80">
                        <Phone className="w-4 h-4 text-luxury-brass shrink-0" />
                        <span>Phone: <span className="font-semibold text-luxury-charcoal">{selectedLead.phone}</span></span>
                      </div>
                      <div className="flex items-center gap-2 text-luxury-charcoal/80">
                        <MapPin className="w-4 h-4 text-luxury-brass shrink-0" />
                        <span>Location: <span className="font-semibold text-luxury-charcoal">{selectedLead.location}</span></span>
                      </div>
                      <div className="flex items-center gap-2 text-luxury-charcoal/80">
                        <Home className="w-4 h-4 text-luxury-brass shrink-0" />
                        <span>Target Space: <span className="font-semibold text-luxury-charcoal">{selectedLead.room_type}</span></span>
                      </div>
                      <div className="flex items-center gap-2 text-luxury-charcoal/80">
                        <Maximize2 className="w-4 h-4 text-luxury-brass shrink-0" />
                        <span>Size: <span className="font-semibold text-luxury-charcoal">{selectedLead.area_sqft ? `${selectedLead.area_sqft} sq ft` : "Not provided"}</span></span>
                      </div>
                      <div className="border-t border-luxury-border pt-2 mt-2">
                        <span className="font-bold block text-[10px] uppercase text-luxury-brass tracking-wider">Project Schedule Timeline</span>
                        <p className="text-luxury-charcoal/80 mt-1">{selectedLead.timeline || "No timeline parsed"}</p>
                      </div>
                      </div>
                  </div>

                  {/* Administrative Configuration */}
                  <div className="space-y-4">
                    <h3 className="font-serif text-base font-bold border-b border-luxury-border pb-1 text-luxury-charcoal">
                      Administrative & ML Specs
                    </h3>
                    <div className="space-y-3 text-xs">
                      <div>
                        <span className="font-bold text-[10px] uppercase text-luxury-brass tracking-wider">Scope Level</span>
                        <p className="text-luxury-charcoal/80 font-semibold">{getScopeName(selectedLead.scope_level)}</p>
                      </div>
                      <div>
                        <span className="font-bold text-[10px] uppercase text-luxury-brass tracking-wider">Material Grade Tier</span>
                        <p className="text-luxury-charcoal/80 font-semibold">{getMaterialName(selectedLead.material_tier)}</p>
                      </div>
                      <div>
                        <span className="font-bold text-[10px] uppercase text-luxury-brass tracking-wider">Initial Database Status</span>
                        <div className="mt-1 flex items-center gap-2">
                          <span className="bg-luxury-brass/10 border border-luxury-brass/30 text-luxury-brass text-[10px] font-bold px-2 py-0.5 rounded">
                            {selectedLead.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                </div>

                {/* Spatial Vision AI profile */}
                {selectedLead.vision_analysis && (
                  <div className="border-t border-luxury-border pt-6 mt-6">
                    <h3 className="font-serif text-base font-bold text-luxury-charcoal mb-4">
                      GPT-4o Vision AI Spatial Scan
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs bg-luxury-lightGray/10 border border-luxury-border p-4 rounded-lg">
                      <div className="space-y-3">
                        <div>
                          <span className="font-bold text-luxury-brass uppercase tracking-wider block">🏛️ Structure & Crown Bones</span>
                          <p className="text-luxury-charcoal/85 mt-1 leading-relaxed">{selectedLead.vision_analysis.architectural_bones}</p>
                        </div>
                        <div>
                          <span className="font-bold text-luxury-brass uppercase tracking-wider block">☀️ Natural Light Profile</span>
                          <p className="text-luxury-charcoal/85 mt-1 leading-relaxed">{selectedLead.vision_analysis.lighting_profile}</p>
                        </div>
                        <div>
                          <span className="font-bold text-luxury-brass uppercase tracking-wider block">🎨 Current Design Aesthetic</span>
                          <p className="text-luxury-charcoal/85 mt-1 leading-relaxed">{selectedLead.vision_analysis.current_style}</p>
                        </div>
                      </div>
                      <div className="space-y-3">
                        <div>
                          <span className="font-bold text-luxury-brass uppercase tracking-wider block">📐 Estimated Layout Scale</span>
                          <p className="text-luxury-charcoal/85 mt-1 leading-relaxed">{selectedLead.vision_analysis.estimated_dimensions}</p>
                        </div>
                        <div>
                          <span className="font-bold text-luxury-brass uppercase tracking-wider block">⚠️ Spatial Pain Points & Obstacles</span>
                          <p className="text-luxury-charcoal/85 mt-1 leading-relaxed">{selectedLead.vision_analysis.potential_pain_points}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
              <Sparkles className="w-16 h-16 text-luxury-border mb-4 animate-pulse" />
              <h3 className="font-serif text-xl font-semibold text-luxury-charcoal">Select a Lead to Review</h3>
              <p className="text-xs text-luxury-charcoal/50 max-w-sm mt-2 leading-relaxed">
                Click on any pre-qualified interior design lead on the left to inspect their
                design briefing metrics, readiness matrix, and download files.
              </p>
            </div>
          )}
        </div>

      </main>

      {/* Dashboard Footer */}
      <footer className="border-t border-luxury-border py-4 text-center text-[10px] tracking-wider text-luxury-charcoal/50 uppercase bg-white">
        © 2026 The Design Concierge Dashboard. All rights reserved.
      </footer>
    </div>
  );
}
