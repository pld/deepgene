// ABOUTME: Utility module for parsing gene symbols from positional gene strings
// ABOUTME: Extracts clean gene symbols (e.g., "CTNND2 (delta catenin-2)" → "CTNND2")

/**
 * Extract gene symbol from positional gene string.
 *
 * Handles common formats:
 * - "CTNND2 (delta catenin-2)" → "CTNND2"
 * - "BRCA1" → "BRCA1"
 * - "TP53 (tumor protein p53)" → "TP53"
 * - "FOXL3" → "FOXL3"
 * - "WI2-2373I1.2" → "WI2-2373I1.2"
 *
 * @param positionalGene - Gene name with optional description
 * @returns Gene symbol (first token before space or parenthesis), or empty string if input is invalid
 *
 * @example
 * extractGeneSymbol("CTNND2 (delta catenin-2)") // => "CTNND2"
 * extractGeneSymbol("WI2-2373I1.2") // => "WI2-2373I1.2"
 * extractGeneSymbol("") // => ""
 */
export function extractGeneSymbol(positionalGene: string): string {
  if (!positionalGene) {
    return '';
  }

  const trimmed = positionalGene.trim();

  if (!trimmed) {
    return '';
  }

  const parts = trimmed.split(/[\s(]/, 2);
  if (parts && parts[0]) {
    return parts[0].trim();
  }

  return '';
}
