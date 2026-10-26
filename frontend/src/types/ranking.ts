export type AnalysisPhase = "idle" | "uploading" | "processing";
export type BackendConnectionState = "checking" | "online" | "offline";
export type BackendStatus = { message: string };

export type ResumeAnalysis = {
  filename: string;
  candidate_name?: string;
  email?: string | null;
  phone?: string | null;
  experience_years_mentioned?: number | null;
  rank?: number | null;
  resume_word_count?: number;
  extracted_text_preview: string;
  overall_match_score: number;
  semantic_similarity_score: number;
  skill_coverage_score: number;
  matched_skills: string[];
  missing_skills: string[];
  resume_skills_detected: string[];
  job_skills_detected: string[];
  strengths: string[];
  recommendations: string[];
  section_presence: Record<string, boolean>;
  disclaimer: string;
};
export type BatchResponse = {
  job_description: string;
  mode: "single" | "ranking";
  summary: { total_uploaded: number; total_analyzed: number; failed_count: number; analyzed_at: string };
  candidates: ResumeAnalysis[];
  errors: string[];
};
export type ImprovedResume = {
  filename: string;
  suggested_filename: string;
  improved_resume_text: string;
  notice: string;
  analysis: ResumeAnalysis;
};
