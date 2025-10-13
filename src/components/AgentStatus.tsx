import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle2, Database, Globe, FileText, Search, TrendingUp, Scale, FileSpreadsheet } from "lucide-react";

interface AgentStatusProps {
  activeAgent?: string;
  completedAgents?: string[];
}

const agentIcons: Record<string, any> = {
  "IQVIA Insights": TrendingUp,
  "EXIM Trends": Globe,
  "Patent Landscape": Scale,
  "Clinical Trials": FileSpreadsheet,
  "Internal Knowledge": Database,
  "Web Intelligence": Search,
  "Report Generator": FileText,
};

export const AgentStatus = ({ activeAgent, completedAgents = [] }: AgentStatusProps) => {
  const agents = [
    "IQVIA Insights",
    "EXIM Trends",
    "Patent Landscape",
    "Clinical Trials",
    "Internal Knowledge",
    "Web Intelligence",
    "Report Generator",
  ];

  if (!activeAgent && completedAgents.length === 0) return null;

  return (
    <Card className="p-4 mb-4 bg-muted/50 border-dashed animate-fade-in">
      <h3 className="text-sm font-semibold mb-3">Agent Activity</h3>
      <div className="grid grid-cols-2 gap-2">
        {agents.map((agent) => {
          const Icon = agentIcons[agent];
          const isActive = activeAgent === agent;
          const isCompleted = completedAgents.includes(agent);

          return (
            <div
              key={agent}
              className="flex items-center gap-2 text-sm"
            >
              {isActive && <Loader2 className="w-4 h-4 animate-spin text-primary" />}
              {isCompleted && <CheckCircle2 className="w-4 h-4 text-green-500" />}
              {!isActive && !isCompleted && <Icon className="w-4 h-4 text-muted-foreground" />}
              <span className={isActive ? "text-primary font-medium" : "text-muted-foreground"}>
                {agent}
              </span>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
