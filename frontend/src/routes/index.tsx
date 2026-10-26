import { createFileRoute } from "@tanstack/react-router";

import { ResumeRankerPage } from "@/components/dashboard/resume-ranker-page";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "TalentMind AI Resume Optimizer" },
      {
        name: "description",
        content:
          "AI-powered resume matching, semantic similarity, skill-gap detection, and resume improvement suggestions.",
      },
      { property: "og:title", content: "TalentMind AI Resume Optimizer" },
      {
        property: "og:description",
        content:
          "Compare your resume with a job description and discover strengths, missing skills, and improvement suggestions.",
      },
    ],
  }),
  component: ResumeRankerPage,
});
