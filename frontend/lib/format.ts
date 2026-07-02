export function formatMoney(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "0원";
  }

  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return "0원";
  }

  return `${Math.round(numericValue).toLocaleString()}원`;
}
