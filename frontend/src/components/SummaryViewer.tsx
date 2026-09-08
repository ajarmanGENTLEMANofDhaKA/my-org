import React, { useMemo } from "react";
import { BookOpen, FlaskConical, Lightbulb, ChevronRight, FileText, BookMarked } from "lucide-react";

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

interface ParsedSection {
  title: string;
  level: number;
  content: string;
  items: BulletItem[];
}

interface BulletItem {
  key: string | null;
  value: string;
}

interface StructuredSummary {
  title: string | null;
  abstract: ParsedSection | null;
  researchData: ParsedSection | null;
  keyFindings: ParsedSection | null;
  otherSections: ParsedSection[];
}

// ─────────────────────────────────────────────────────────────────────────────
// Markdown Parsing Utilities
// ─────────────────────────────────────────────────────────────────────────────

function stripInline(text: string): string {
  return text
    .replace(/\*\*\*(.+?)\*\*\*/g, "$1")
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/\*(.+?)\*/g, "$1")
    .replace(/__(.+?)__/g, "$1")
    .replace(/_(.+?)_/g, "$1")
    .replace(/`(.+?)`/g, "$1")
    .trim();
}

function renderInline(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  const regex = /(\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    if (match[2]) {
      parts.push(<strong key={match.index} className="font-semibold italic">{match[2]}</strong>);
    } else if (match[3]) {
      parts.push(<strong key={match.index} className="font-semibold text-foreground">{match[3]}</strong>);
    } else if (match[4]) {
      parts.push(<em key={match.index} className="italic">{match[4]}</em>);
    } else if (match[5]) {
      parts.push(
        <code key={match.index} className="px-1 py-0.5 rounded bg-muted text-xs font-mono">
          {match[5]}
        </code>
      );
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : [text];
}

function parseBulletItem(line: string): BulletItem {
  const clean = line.replace(/^[\s]*[-*\u2022]\s*/, "").trim();
  const kvMatch = clean.match(/^\*\*(.+?)\*\*\s*:?\s*(.*)$/);
  if (kvMatch) {
    // Strip any trailing colon captured inside the bold markers (e.g. **Title:** → key="Title")
    return { key: kvMatch[1].trim().replace(/:$/, ""), value: kvMatch[2].trim() };
  }
  const simpleKvMatch = clean.match(/^([A-Z][^:]{2,40}):\s*(.+)$/);
  if (simpleKvMatch) {
    return { key: simpleKvMatch[1].trim(), value: simpleKvMatch[2].trim() };
  }
  return { key: null, value: stripInline(clean) };
}

function parseMarkdown(raw: string): ParsedSection[] {
  const lines = raw.split(/\r?\n/);
  const sections: ParsedSection[] = [];
  let current: ParsedSection | null = null;
  let contentLines: string[] = [];

  const flush = () => {
    if (current) {
      const proseLines: string[] = [];
      const bullets: BulletItem[] = [];
      for (const l of contentLines) {
        if (/^[\s]*[-*\u2022]\s/.test(l)) {
          bullets.push(parseBulletItem(l));
        } else if (l.trim().length > 0) {
          proseLines.push(l.trim());
        }
      }
      // Join with double-newline so the Prose component can split into paragraphs
      current.content = proseLines.join("\n\n");
      current.items = bullets;
      sections.push(current);
    }
  };

  for (const line of lines) {
    const h1 = line.match(/^#\s+(.+)/);
    const h2 = line.match(/^##\s+(.+)/);
    const h3 = line.match(/^###\s+(.+)/);

    if (h1 || h2 || h3) {
      flush();
      const level = h1 ? 1 : h2 ? 2 : 3;
      const title = (h1?.[1] || h2?.[1] || h3?.[1] || "").trim();
      current = { title: stripInline(title), level, content: "", items: [] };
      contentLines = [];
    } else if (current) {
      contentLines.push(line);
    }
  }

  flush();
  return sections;
}

function structureSummary(sections: ParsedSection[], rawText: string): StructuredSummary {
  const result: StructuredSummary = {
    title: null,
    abstract: null,
    researchData: null,
    keyFindings: null,
    otherSections: [],
  };

  // Two-pass categorisation ensures high-priority keyword matches always win.
  // Pass 1: strict / high-priority keywords only (exact section names Gemini commonly produces).
  // Pass 2: broader fallback keywords fill any slots still empty after pass 1.
  // Sections that never match either pass are collected in otherSections in document order.

  const strictAbstractKw = ["abstract", "study overview", "introduction", "background"];
  const strictDataKw     = ["research data", "methodology", "methods", "data collection"];
  const strictFindingsKw = ["key findings", "findings", "results", "conclusions", "discussion", "outcomes"];

  const broadAbstractKw  = ["overview", "summary"];   // e.g. "Research Summary" if no ## Abstract exists
  const broadDataKw      = ["participants", "sample", "procedure"];
  const broadFindingsKw  = ["conclusion"];             // "Conclusion" as standalone section

  // Collect unmatched sections so pass 2 can re-evaluate them in document order
  const unmatchedAfterPass1: ParsedSection[] = [];

  // Pass 1 — strict keywords
  for (const sec of sections) {
    const tl = sec.title.toLowerCase();

    if (sec.level === 1 && !result.title) {
      result.title = sec.title;
      // Do NOT continue — fall through so the section's content is also categorized below
    }

    if (!result.abstract && strictAbstractKw.some((k) => tl.includes(k))) {
      result.abstract = sec;
    } else if (!result.researchData && strictDataKw.some((k) => tl.includes(k))) {
      result.researchData = sec;
    } else if (!result.keyFindings && strictFindingsKw.some((k) => tl.includes(k))) {
      result.keyFindings = sec;
    } else {
      unmatchedAfterPass1.push(sec);
    }
  }

  // Pass 2 — broader keywords for sections not matched in pass 1
  for (const sec of unmatchedAfterPass1) {
    const tl = sec.title.toLowerCase();

    if (!result.abstract && broadAbstractKw.some((k) => tl.includes(k))) {
      result.abstract = sec;
    } else if (!result.researchData && broadDataKw.some((k) => tl.includes(k))) {
      result.researchData = sec;
    } else if (!result.keyFindings && broadFindingsKw.some((k) => tl.includes(k))) {
      result.keyFindings = sec;
    } else {
      result.otherSections.push(sec);
    }
  }

  // Intentionally do NOT fall back to extracting a title from body text.
  // If no # level-1 heading exists (common with Gemini output), leave title as null.
  // The SummaryViewer will display summaryName from props as the document identifier instead.

  return result;
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────────────

function Prose({ text }: { text: string }) {
  if (!text.trim()) return null;
  const paragraphs = text.split(/\n{2,}/);
  return (
    <div className="space-y-3">
      {paragraphs.map((para, i) => (
        <p key={i} className="text-sm leading-7 text-foreground/90">
          {renderInline(para.trim())}
        </p>
      ))}
    </div>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
        {label}
      </span>
      <span className="text-sm font-medium text-foreground leading-snug">
        {renderInline(value)}
      </span>
    </div>
  );
}

function BulletList({ items }: { items: BulletItem[] }) {
  if (items.length === 0) return null;
  return (
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2">
          <ChevronRight className="w-3.5 h-3.5 mt-1 shrink-0 text-primary/60" />
          <span className="text-sm leading-6 text-foreground/90">
            {item.key ? (
              <>
                <span className="font-semibold text-foreground">{item.key}:</span>{" "}
                {renderInline(item.value)}
              </>
            ) : (
              renderInline(item.value)
            )}
          </span>
        </li>
      ))}
    </ul>
  );
}

function ResearchDataSection({ section }: { section: ParsedSection }) {
  const kvItems = section.items.filter((item) => item.key);
  const listItems = section.items.filter((item) => !item.key);

  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-4 border-b border-border bg-secondary/40">
        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
          <FlaskConical className="w-4 h-4 text-primary" />
        </div>
        <h2 className="text-base font-semibold text-foreground">{section.title}</h2>
      </div>
      <div className="p-5 space-y-5">
        {section.content && <Prose text={section.content} />}
        {kvItems.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {kvItems.map((item, i) => (
              <div key={i} className="rounded-lg bg-secondary/50 border border-border/60 px-4 py-3">
                <MetaRow label={item.key!} value={item.value} />
              </div>
            ))}
          </div>
        )}
        {listItems.length > 0 && <BulletList items={listItems} />}
      </div>
    </div>
  );
}

function AbstractSection({ section }: { section: ParsedSection }) {
  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-4 border-b border-border bg-secondary/40">
        <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
          <BookMarked className="w-4 h-4 text-accent" />
        </div>
        <h2 className="text-base font-semibold text-foreground">{section.title}</h2>
      </div>
      <div className="p-5 space-y-4">
        {section.content && <Prose text={section.content} />}
        {section.items.length > 0 && <BulletList items={section.items} />}
      </div>
    </div>
  );
}

function KeyFindingsSection({ section }: { section: ParsedSection }) {
  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-4 border-b border-border bg-secondary/40">
        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
          <Lightbulb className="w-4 h-4 text-primary" />
        </div>
        <h2 className="text-base font-semibold text-foreground">{section.title}</h2>
      </div>
      <div className="p-5 space-y-4">
        {section.content && <Prose text={section.content} />}
        {section.items.length > 0 && (
          <div className="space-y-3">
            {section.items.map((item, i) => (
              <div
                key={i}
                className="flex gap-4 p-4 rounded-lg bg-primary/5 border border-primary/10"
              >
                <div className="w-8 h-8 rounded-full bg-primary/15 flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-primary">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  {item.key && (
                    <p className="text-sm font-semibold text-foreground mb-1">{item.key}</p>
                  )}
                  <p className="text-sm leading-6 text-foreground/80">
                    {renderInline(item.value)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function GenericSection({ section }: { section: ParsedSection }) {
  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-4 border-b border-border bg-secondary/40">
        <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center shrink-0">
          <BookOpen className="w-4 h-4 text-muted-foreground" />
        </div>
        <h2 className="text-base font-semibold text-foreground">{section.title}</h2>
      </div>
      <div className="p-5 space-y-4">
        {section.content && <Prose text={section.content} />}
        {section.items.length > 0 && <BulletList items={section.items} />}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main SummaryViewer
// ─────────────────────────────────────────────────────────────────────────────

interface SummaryViewerProps {
  content: string;
  summaryName?: string;
}

export function SummaryViewer({ content, summaryName }: SummaryViewerProps) {
  const structured = useMemo<StructuredSummary>(() => {
    if (!content?.trim()) {
      return { title: null, abstract: null, researchData: null, keyFindings: null, otherSections: [] };
    }
    try {
      const sections = parseMarkdown(content);
      return structureSummary(sections, content);
    } catch {
      return { title: null, abstract: null, researchData: null, keyFindings: null, otherSections: [] };
    }
  }, [content]);

  const hasParsedContent =
    structured.abstract ||
    structured.researchData ||
    structured.keyFindings ||
    structured.otherSections.length > 0;

  // Fallback: raw sections not caught by categoriser
  if (!hasParsedContent && content?.trim()) {
    const sections = parseMarkdown(content);
    if (sections.length > 0) {
      return (
        <div className="space-y-4 animate-fade-in">
          {structured.title && (
            <div className="pb-2 border-b border-border">
              <h1 className="text-xl font-bold text-foreground">{structured.title}</h1>
            </div>
          )}
          {sections.map((sec, i) => (
            <GenericSection key={i} section={sec} />
          ))}
        </div>
      );
    }
    // Pure plain-text fallback
    return (
      <div className="rounded-xl border border-border bg-card p-6">
        <Prose text={stripInline(content)} />
      </div>
    );
  }

  // Determine what to show in the title bar:
  // - If there is a real # level-1 Markdown title, show it as h1 with summaryName as subtitle
  // - If there is no # heading (normal for Gemini output), show summaryName as the primary label
  const displayTitle = structured.title ?? summaryName ?? null;
  const displaySubtitle = structured.title && summaryName ? summaryName : null;

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Document title bar — always visible when a name is available */}
      {displayTitle && (
        <div className="pb-3 border-b border-border">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shrink-0 mt-0.5">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground leading-snug">{displayTitle}</h1>
              {displaySubtitle && (
                <p className="text-xs text-muted-foreground mt-0.5">{displaySubtitle}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {structured.abstract && <AbstractSection section={structured.abstract} />}
      {structured.researchData && <ResearchDataSection section={structured.researchData} />}
      {structured.keyFindings && <KeyFindingsSection section={structured.keyFindings} />}
      {structured.otherSections.map((sec, i) => (
        <GenericSection key={i} section={sec} />
      ))}
    </div>
  );
}

export default SummaryViewer;
