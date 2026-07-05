import { Sparkles } from "lucide-react";

interface ExplanationBadgeProps {
  explanation: string;
}

export function ExplanationBadge({ explanation }: ExplanationBadgeProps) {
  return (
    <p className="flex items-start gap-1.5 text-xs text-[var(--color-bone-dim)]">
      <Sparkles size={12} className="mt-0.5 shrink-0 text-[var(--color-signal)]" />
      <span>{explanation}</span>
    </p>
  );
}
