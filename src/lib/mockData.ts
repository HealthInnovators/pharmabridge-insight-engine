// Mock data for the various external APIs

export const mockIQVIAData: Record<string, any> = {
  "neuropathic pain": {
    therapy_area: "Neuropathic Pain",
    market_size_usd: "6.5B",
    cagr_5yr: 0.07,
    major_competitors: ["Lyrica", "Cymbalta", "Gabapentin"],
  },
  "erectile dysfunction": {
    therapy_area: "Erectile Dysfunction",
    market_size_usd: "4.2B",
    cagr_5yr: 0.05,
    major_competitors: ["Viagra", "Cialis", "Levitra"],
  },
  "pulmonary arterial hypertension": {
    therapy_area: "Pulmonary Arterial Hypertension",
    market_size_usd: "8.3B",
    cagr_5yr: 0.12,
    major_competitors: ["Revatio", "Adempas", "Uptravi"],
  },
};

export const mockPatentData: Record<string, any[]> = {
  "sildenafil": [
    {
      patent_id: "US6469012B1",
      title: "Pyrazolopyrimidinones for the treatment of impotence",
      status: "Expired",
      expiry_date: "2019-10-22",
      assignee: "Pfizer Inc.",
    },
    {
      patent_id: "US7943607B2",
      title: "Sildenafil formulations for pulmonary hypertension",
      status: "Active",
      expiry_date: "2027-03-15",
      assignee: "Generic Pharma Co.",
    },
  ],
  "metformin": [
    {
      patent_id: "US4369172A",
      title: "Metformin composition for diabetes treatment",
      status: "Expired",
      expiry_date: "1999-01-18",
      assignee: "Bristol-Myers Squibb",
    },
  ],
};

export const mockClinicalTrialsData: Record<string, any[]> = {
  "sildenafil": [
    {
      nct_id: "NCT04567890",
      title: "Sildenafil in Treatment of Raynaud's Phenomenon",
      status: "Recruiting",
      phase: "Phase 3",
      sponsor: "University Medical Center",
      conditions: ["Raynaud's Disease", "Vascular Disorders"],
    },
    {
      nct_id: "NCT03456789",
      title: "Sildenafil for Altitude Sickness Prevention",
      status: "Completed",
      phase: "Phase 2",
      sponsor: "Mountain Research Institute",
      conditions: ["Acute Mountain Sickness"],
    },
  ],
  "glp-1": [
    {
      nct_id: "NCT05123456",
      title: "GLP-1 Agonist in NASH Treatment",
      status: "Recruiting",
      phase: "Phase 3",
      sponsor: "Metabolic Health Institute",
      conditions: ["NASH", "Liver Disease"],
    },
  ],
};

export const mockEXIMData: Record<string, any> = {
  "metformin-us": {
    molecule: "Metformin",
    country: "United States",
    import_volume_kg_5yr: [120000, 135000, 150000, 162000, 178000],
    export_volume_kg_5yr: [45000, 52000, 48000, 55000, 60000],
    major_importers: ["India", "China", "Germany"],
    major_exporters: ["Ireland", "India", "China"],
  },
};

export const mockInternalDocs = [
  {
    id: "doc1",
    title: "Project Phoenix - Sildenafil Repurposing Study",
    content: "Internal research indicates that sildenafil shows promising results in treating Raynaud's phenomenon in preliminary in-vitro studies. The vasodilatory effects suggest potential for improved blood flow in peripheral vascular diseases. Safety profile appears favorable based on existing cardiovascular use data.",
    category: "Research",
  },
  {
    id: "doc2",
    title: "Market Analysis - Rare Disease Opportunities Q4 2024",
    content: "Analysis reveals significant unmet need in pulmonary arterial hypertension (PAH) market. Current therapies have limited efficacy and high cost. Generic sildenafil could be positioned as cost-effective alternative for specific PAH patient segments.",
    category: "Market Intelligence",
  },
  {
    id: "doc3",
    title: "Regulatory Strategy - Novel Delivery Systems",
    content: "FDA guidance suggests that novel formulations of existing molecules may qualify for 505(b)(2) pathway if they demonstrate clinical benefits. Foam-based delivery systems have shown improved bioavailability in topical applications.",
    category: "Regulatory",
  },
];
