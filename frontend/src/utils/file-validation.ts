const SUPPORTED_FILE_EXTENSIONS = [".pdf", ".docx"] as const;
const MAX_FILE_SIZE_MB = 8;

export function getAcceptedFileTypes(): string {
  return ".pdf,.docx";
}

export function getSupportedFileTypesLabel(): string {
  return "PDF | DOCX";
}

export function validateCandidateFile(file: File): string | null {
  const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  if (!SUPPORTED_FILE_EXTENSIONS.includes(extension as (typeof SUPPORTED_FILE_EXTENSIONS)[number])) {
    return "Unsupported resume format. Upload a PDF or DOCX file.";
  }
  if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
    return `File is too large. Please upload a resume smaller than ${MAX_FILE_SIZE_MB} MB.`;
  }
  return null;
}
