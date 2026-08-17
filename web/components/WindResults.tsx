"use client";

import { ResultCard } from "./ResultCard";

export type LowRiseResult = {
  route: "WIND-LR";
  applicability: {
    applicable: boolean;
    height_limit_satisfied: boolean;
    aspect_ratio_limit_satisfied: boolean;
    minimum_plan_dimension: number;
    height_to_minimum_plan_dimension_ratio: number;
  };
  exposureFactor?: number;
  pressure?: number;
};

export type GeneralStaticResult = {
  route: "WIND-GS";
  data: {
    exposure_factor: number;
    gust_effect_factor: number;
    windward: { cp: number; pressure: number };
    leeward: { cp: number; pressure: number };
    parallel_wall: { cp: number; pressure: number };
    roof: { cp: number; pressure: number };
  };
};

export type ComponentsResult = {
  route: "WIND-CC";
  actual_area: number;
  lookup_area: number;
  maximum_table_area: number;
  unit: string;
};

export type CalculationResult = LowRiseResult | GeneralStaticResult | ComponentsResult;

export function WindResults({ result, terrain }: { result: CalculationResult; terrain: string }) {
  if (result.route === "WIND-LR") {
    const a = result.applicability;
    return (
      <div className="results-grid">
        <ResultCard title="Applicability" value={a.applicable ? "Applicable" : "Not applicable"} detail="WIND-LR" />
        <ResultCard title="Height limit" value={a.height_limit_satisfied ? "Satisfied" : "Not satisfied"} />
        <ResultCard title="Aspect ratio" value={a.aspect_ratio_limit_satisfied ? "Satisfied" : "Not satisfied"} />
        <ResultCard title="H / Bmin" value={a.height_to_minimum_plan_dimension_ratio.toFixed(3)} detail={`Bmin = ${a.minimum_plan_dimension.toFixed(2)} m`} />
        {result.exposureFactor !== undefined && <ResultCard title="Exposure factor Ce" value={result.exposureFactor.toFixed(3)} detail={`${terrain} terrain`} />}
        {result.pressure !== undefined && <ResultCard title="External wind pressure" value={`${result.pressure.toFixed(3)} kPa`} detail="Approved Agent #2 engine output" />}
      </div>
    );
  }

  if (result.route === "WIND-GS") {
    const d = result.data;
    return (
      <div className="results-grid">
        <ResultCard title="Exposure factor Ce" value={d.exposure_factor.toFixed(3)} />
        <ResultCard title="Gust effect factor Cg" value={d.gust_effect_factor.toFixed(3)} />
        {(["windward", "leeward", "parallel_wall", "roof"] as const).map((surface) => (
          <ResultCard
            key={surface}
            title={surface.replace("_", " ")}
            value={`${d[surface].pressure.toFixed(3)} kPa`}
            detail={`Cp = ${d[surface].cp.toFixed(3)}`}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="results-grid">
      <ResultCard title="Actual component area" value={`${result.actual_area.toFixed(2)} ${result.unit}`} />
      <ResultCard title="Lookup area" value={`${result.lookup_area.toFixed(2)} ${result.unit}`} />
      <ResultCard title="Maximum table area" value={`${result.maximum_table_area.toFixed(2)} ${result.unit}`} />
    </div>
  );
}
