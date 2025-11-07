import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import { User, Bot } from "lucide-react";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  metadata?: any;
}

export const ChatMessage = ({ role, content, metadata }: ChatMessageProps) => {
  const isUser = role === "user";
  const backendUrl = import.meta.env.VITE_BACKEND_URL as string | undefined;

  return (
    <div className={cn("flex gap-3 mb-4 animate-fade-in", isUser && "justify-end")}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
          <Bot className="w-5 h-5 text-primary" />
        </div>
      )}
      <Card className={cn(
        "max-w-[80%] p-4",
        isUser ? "bg-primary text-primary-foreground" : "bg-card"
      )}>
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <p className="whitespace-pre-wrap m-0">{content}</p>
        </div>
        {metadata?.agents && (
          <div className="mt-2 pt-2 border-t border-border/50">
            <p className="text-xs text-muted-foreground">
              Consulted: {metadata.agents.join(", ")}
            </p>
          </div>
        )}
        {metadata?.report_id && backendUrl && (
          <div className="mt-2">
            <a
              href={`${backendUrl}/api/reports/${metadata.report_id}`}
              target="_blank"
              rel="noreferrer"
              className="text-xs underline text-primary"
            >
              Download report (PDF)
            </a>
          </div>
        )}
      </Card>
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary/10 flex items-center justify-center">
          <User className="w-5 h-5 text-secondary" />
        </div>
      )}
    </div>
  );
};
