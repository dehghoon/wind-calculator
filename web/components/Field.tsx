import ParameterHelp from "./ParameterHelp";
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
      <span className="field-label">{label}<ParameterHelp label={label} text={name==="q"?"Reference velocity pressure q is in kPa. Use the adopted edition and verified project station; NBC 2020 station selection uses q50.":name==="ch"?"Ch is a documented engineering input. The current workbook does not provide its standalone selection; do not use the default as a project determination.":name==="height"?"Height H is the building/reference height above grade in metres. Ce is determined by height and terrain.":name==="importanceFactor"?"Iw is the wind importance factor for the adopted code and building category.":name==="ct"?"Ct is the topographic factor for the 2020 general-static route. The engine uses effective Ct=1 for NBC 2010.":name==="componentArea"?"Enter the component tributary/effective area in square metres for the selected roof zone. This route returns a coefficient lookup only.":name==="roofSlope"?"Roof slope is in degrees, not percent. Its value is used with load case and surface to look up CgCp.":"Enter the measured project dimension in metres. D is parallel to wind; B and W are the plan dimensions. Confirm orientation for every wind case."}/></span>
      <span className="field-control">
        <input
          id={name}
          name={name}
          type="number"
          required
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

