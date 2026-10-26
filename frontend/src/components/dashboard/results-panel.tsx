import { useMemo } from "react";
import { CheckCircle2, CircleAlert, FileSearch, Gauge, Lightbulb, ScanText, Sparkles, Target } from "lucide-react";
import type { ResumeAnalysis } from "@/types/ranking";

type ResultsPanelProps = { response: ResumeAnalysis | null };

function SkillPills({ items, tone }: { items: string[]; tone: "good" | "missing" | "neutral" }) {
  if (!items.length) return <p className="text-sm text-muted-foreground">No items detected.</p>;
  const styles = {
    good: "border-emerald-400/20 bg-emerald-400/10 text-emerald-200",
    missing: "border-amber-400/20 bg-amber-400/10 text-amber-100",
    neutral: "border-border/70 bg-background/60 text-muted-foreground",
  };
  return <div className="flex flex-wrap gap-2">{items.map((item) => <span key={item} className={`rounded-full border px-3 py-1.5 text-xs font-medium ${styles[tone]}`}>{item}</span>)}</div>;
}

function ScoreRing({ score }: { score: number }) {
  const safe = Math.max(0, Math.min(100, score));
  const style = useMemo(() => ({ background: `conic-gradient(var(--brand-cyan) ${safe * 3.6}deg, oklch(0.3 0.03 246) 0deg)` }), [safe]);
  return <div className="flex h-36 w-36 items-center justify-center rounded-full p-[9px]" style={style}>
    <div className="flex h-full w-full flex-col items-center justify-center rounded-full bg-card"><span className="font-display text-3xl font-bold">{Math.round(safe)}%</span><span className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">Match</span></div>
  </div>;
}

export function ResultsPanel({ response }: ResultsPanelProps) {
  if (!response) {
    return <section className="rounded-[1.75rem] border border-dashed border-border/70 bg-card/45 px-6 py-12 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-cyan/10 text-brand-cyan"><FileSearch className="h-7 w-7" /></div>
      <h2 className="mt-4 font-display text-xl font-semibold">Your analysis will appear here</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted-foreground">Upload your resume, add the job description, and run the analysis to see semantic alignment, skill gaps, and tailored improvement tips.</p>
    </section>;
  }

  const sections = Object.entries(response.section_presence || {});
  return <section className="space-y-5 animate-fade-up" aria-live="polite">
    <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
      <div><p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-cyan">Analysis complete</p><h2 className="mt-2 font-display text-2xl font-semibold">Resume match report</h2><p className="mt-1 text-sm text-muted-foreground">{response.filename || "Uploaded resume"} · Results are based on your supplied job description.</p></div>
      <div className="inline-flex w-fit items-center gap-2 rounded-full border border-brand-cyan/20 bg-brand-cyan/10 px-3 py-2 text-xs text-brand-cyan"><Sparkles className="h-4 w-4" /> NLP-powered analysis</div>
    </div>

    <div className="grid gap-4 lg:grid-cols-[0.85fr_1.15fr]">
      <div className="flex flex-col items-center justify-center rounded-[1.6rem] border border-border/70 bg-card/85 p-6 shadow-panel sm:flex-row sm:gap-6">
        <ScoreRing score={response.overall_match_score} />
        <div className="mt-4 w-full space-y-4 sm:mt-0">
          <div><div className="mb-1 flex items-center justify-between text-sm"><span className="text-muted-foreground">Semantic similarity</span><strong>{response.semantic_similarity_score}%</strong></div><div className="h-2 overflow-hidden rounded-full bg-background"><div className="h-full rounded-full bg-brand-cyan transition-all" style={{ width: `${Math.max(0, Math.min(100, response.semantic_similarity_score))}%` }} /></div></div>
          <div><div className="mb-1 flex items-center justify-between text-sm"><span className="text-muted-foreground">Skill coverage</span><strong>{response.skill_coverage_score}%</strong></div><div className="h-2 overflow-hidden rounded-full bg-background"><div className="h-full rounded-full bg-brand-gold transition-all" style={{ width: `${Math.max(0, Math.min(100, response.skill_coverage_score))}%` }} /></div></div>
          <p className="text-xs leading-5 text-muted-foreground">Overall score combines semantic similarity (65%) and recognized skill coverage (35%).</p>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-[1.5rem] border border-border/70 bg-card/85 p-5"><div className="flex items-center gap-2 text-emerald-200"><CheckCircle2 className="h-5 w-5"/><h3 className="font-semibold">Matched skills</h3></div><p className="my-3 text-sm text-muted-foreground">Skills found in both texts.</p><SkillPills items={response.matched_skills} tone="good" /></div>
        <div className="rounded-[1.5rem] border border-border/70 bg-card/85 p-5"><div className="flex items-center gap-2 text-amber-100"><CircleAlert className="h-5 w-5"/><h3 className="font-semibold">Skill gaps</h3></div><p className="my-3 text-sm text-muted-foreground">Job-description skills not detected in your resume.</p><SkillPills items={response.missing_skills} tone="missing" /></div>
      </div>
    </div>

    <div className="grid gap-4 lg:grid-cols-2">
      <div className="rounded-[1.5rem] border border-border/70 bg-card/85 p-5 md:p-6"><div className="mb-4 flex items-center gap-2"><Target className="h-5 w-5 text-brand-cyan"/><h3 className="font-display text-lg font-semibold">What is working well</h3></div><ul className="space-y-3">{response.strengths.map((item, i) => <li key={`${i}-${item}`} className="flex gap-3 text-sm leading-6 text-muted-foreground"><CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-emerald-300"/>{item}</li>)}</ul></div>
      <div className="rounded-[1.5rem] border border-border/70 bg-card/85 p-5 md:p-6"><div className="mb-4 flex items-center gap-2"><Lightbulb className="h-5 w-5 text-brand-gold"/><h3 className="font-display text-lg font-semibold">Recommended improvements</h3></div><ul className="space-y-3">{response.recommendations.map((item, i) => <li key={`${i}-${item}`} className="flex gap-3 text-sm leading-6 text-muted-foreground"><span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-gold/10 text-xs text-brand-gold">{i + 1}</span>{item}</li>)}</ul></div>
    </div>

    <div className="rounded-[1.5rem] border border-border/70 bg-card/85 p-5 md:p-6"><div className="mb-4 flex items-center gap-2"><ScanText className="h-5 w-5 text-brand-cyan"/><h3 className="font-display text-lg font-semibold">Resume section check</h3></div><div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">{sections.map(([name, present]) => <div key={name} className="flex items-center gap-2 rounded-xl border border-border/60 bg-background/55 p-3 text-sm"><span className={`h-2.5 w-2.5 rounded-full ${present ? "bg-emerald-300" : "bg-amber-300"}`} /><span className="capitalize">{name}</span><span className="ml-auto text-xs text-muted-foreground">{present ? "Found" : "Not found"}</span></div>)}</div><p className="mt-3 text-xs text-muted-foreground">Section detection relies on common headings and may not recognize creative layouts.</p></div>

    <div className="rounded-[1.5rem] border border-border/70 bg-card/85 p-5 md:p-6"><h3 className="font-display text-lg font-semibold">Detected skill inventory</h3><p className="mb-4 mt-1 text-sm text-muted-foreground">Known skills detected by the current starter dictionary.</p><SkillPills items={response.resume_skills_detected} tone="neutral" /><details className="mt-5 rounded-xl border border-border/60 bg-background/50 p-4"><summary className="cursor-pointer text-sm font-semibold">View extracted resume text preview</summary><pre className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-muted-foreground">{response.extracted_text_preview}</pre></details></div>
    <p className="rounded-xl border border-amber-300/15 bg-amber-300/5 p-4 text-xs leading-5 text-muted-foreground"><strong className="text-amber-100">Important:</strong> {response.disclaimer}</p>
  </section>;
}
