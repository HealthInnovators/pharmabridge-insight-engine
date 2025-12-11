import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import { User, Bot, Download } from "lucide-react";
import ReactMarkdown from 'react-markdown';

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
          <ReactMarkdown
            components={{
              a: ({node, ...props}) => (
                <a 
                  {...props} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                />
              ),
              ul: ({node, ...props}) => (
                <ul className="list-disc pl-5 mb-2" {...props} />
              ),
              li: ({node, ...props}) => (
                <li className="mb-1" {...props} />
              ),
              p: ({node, ...props}) => (
                <p className="mb-2" {...props} />
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
        {metadata?.agents && (
          <div className="mt-2 pt-2 border-t border-border/50">
            <p className="text-xs text-muted-foreground">
              Consulted: {metadata.agents.join(", ")}
            </p>
          </div>
        )}
        {metadata?.report_id && backendUrl && (
          <div className="mt-3 pt-2 border-t border-border/50">
            <a
              href={`${backendUrl}/api/reports/${metadata.report_id}`}
              target="_blank"
              rel="noreferrer"
              className="text-sm font-medium text-primary hover:underline inline-flex items-center gap-1"
            >
              <Download className="w-4 h-4" />
              Download Full Report (PDF)
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
