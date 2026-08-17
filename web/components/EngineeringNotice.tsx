export function EngineeringNotice({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  return (
    <aside className="notice" role="status">
      <strong>{title}</strong>
      <p>{message}</p>
    </aside>
  );
}
