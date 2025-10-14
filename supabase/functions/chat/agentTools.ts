const mockData = {
  iqvia: { "neuropathic pain": { market_size_usd: "6.5B", cagr_5yr: 0.07 } },
  patents: { "sildenafil": [{ patent_id: "US6469012B1", status: "Expired", expiry_date: "2019-10-22" }] },
  trials: { "sildenafil": [{ nct_id: "NCT04567890", title: "Sildenafil in Raynaud's", phase: "Phase 3" }] }
};

export const agentTools = [
  {
    type: "function",
    function: {
      name: "query_iqvia_api",
      description: "Get market data for therapy areas",
      parameters: {
        type: "object",
        properties: { query: { type: "string" } },
        required: ["query"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "query_patent_database",
      description: "Search patents for molecules",
      parameters: {
        type: "object",
        properties: { molecule: { type: "string" } },
        required: ["molecule"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "query_clinical_trials",
      description: "Search clinical trials",
      parameters: {
        type: "object",
        properties: { query: { type: "string" } },
        required: ["query"]
      }
    }
  }
];

export function executeToolCall(toolName: string, args: any): any {
  const q = (args.query || args.molecule || "").toLowerCase();
  if (toolName === "query_iqvia_api") return (mockData.iqvia as any)[q] || { error: "Not found" };
  if (toolName === "query_patent_database") return (mockData.patents as any)[q] || [];
  if (toolName === "query_clinical_trials") return (mockData.trials as any)[q] || [];
  return { info: "Mock data for " + toolName };
}
