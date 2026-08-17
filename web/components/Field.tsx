type FieldProps = {
  label: string;
  name: string;
  value: string;
  onChange: (value: string) => void;
  unit?: string;
  min?: number;
  max?: number;
  step?: number;
};

export function Field({
  label,
  name,
  value,
  onChange,
  unit,
  min,
  max,
  step = 0.01,
}: FieldProps) {
  return (
    <label className="field" htmlFor={name}>
      <span className="field-label">{label}</span>
      <span className="field-control">
        <input
          id={name}
          name={name}
          type="number"
          value={value}
          min={min}
          max={max}
          step={step}
          onChange={(event) => onChange(event.target.value)}
        />
        {unit ? <span className="field-unit">{unit}</span> : null}
      </span>
    </label>
  );
}
