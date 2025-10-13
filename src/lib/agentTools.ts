import { mockIQVIAData, mockPatentData, mockClinicalTrialsData, mockEXIMData, mockInternalDocs } from "./mockData";

// Tool definitions for the AI agent
export const agentTools = [
  {
    type: "function",
    function: {
      name: "query_iqvia_api",
      description: "Query IQVIA market data for therapy areas or molecules. Returns market size, growth rate, and competitor information.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "The therapy area or molecule name to search for (e.g., 'neuropathic pain', 'erectile dysfunction')",
          },
        },
        required: ["query"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "query_patent_database",
      description: "Search patent database for a specific molecule. Returns patent status, expiry dates, and assignees.",
      parameters: {
        type: "object",
        properties: {
          molecule: {
            type: "string",
            description: "The molecule name to search patents for (e.g., 'sildenafil', 'metformin')",
          },
        },
        required: ["molecule"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "query_clinical_trials",
      description: "Search clinical trials database for a molecule or condition. Returns trial details including status, phase, and sponsors.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "The molecule or condition to search for (e.g., 'sildenafil', 'glp-1')",
          },
        },
        required: ["query"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "query_exim_data",
      description: "Get import/export data for APIs and formulations. Returns trade volumes and major trading partners.",
      parameters: {
        type: "object",
        properties: {
          molecule: {
            type: "string",
            description: "The molecule name",
          },
          country: {
            type: "string",
            description: "The country code (e.g., 'us', 'eu', 'india')",
          },
        },
        required: ["molecule", "country"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "search_internal_docs",
      description: "Search internal knowledge base for relevant documents and research. Returns document summaries with citations.",
      parameters: {
        type: "object",
        properties: {
          topic: {
            type: "string",
            description: "The topic to search for in internal documents",
          },
        },
        required: ["topic"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "web_search",
      description: "Perform web search for scientific publications and news. Returns summarized results with sources.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "The search query",
          },
        },
        required: ["query"],
      },
    },
  },
];

// Mock implementations of the tool functions
export function executeToolCall(toolName: string, args: any): any {
  const query = args.query?.toLowerCase() || "";
  const molecule = args.molecule?.toLowerCase() || "";
  
  switch (toolName) {
    case "query_iqvia_api":
      const iqviaKey = Object.keys(mockIQVIAData).find(key => query.includes(key));
      return iqviaKey ? mockIQVIAData[iqviaKey] : { error: "No data found for this therapy area" };
    
    case "query_patent_database":
      return mockPatentData[molecule] || [];
    
    case "query_clinical_trials":
      const trialsKey = Object.keys(mockClinicalTrialsData).find(key => query.includes(key));
      return trialsKey ? mockClinicalTrialsData[trialsKey] : [];
    
    case "query_exim_data":
      const eximKey = `${molecule}-${args.country?.toLowerCase() || 'us'}`;
      return mockEXIMData[eximKey] || { error: "No trade data available" };
    
    case "search_internal_docs":
      return mockInternalDocs.filter(doc => 
        doc.content.toLowerCase().includes(query) ||
        doc.title.toLowerCase().includes(query)
      );
    
    case "web_search":
      return {
        summary: `Web search results for "${query}": Found multiple recent publications and clinical reports. Key findings suggest ongoing research in this area with promising preliminary results.`,
        sources: [
          "PubMed Central - Recent review articles",
          "ClinicalTrials.gov - Active trials database",
          "Nature Medicine - Latest research publications",
        ],
      };
    
    default:
      return { error: "Unknown tool" };
  }
}
