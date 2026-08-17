type ResultCardProps = {
  title: string;
  value: string;
  detail?: string;
};

export function ResultCard({ title, value, detail }: ResultCardProps) {
  return (
    <article className="result-card">
      <span>{title}</span>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </article>
  );
}
