"use client";

import { FormEvent, useState } from "react";
import { EngineeringNotice } from "./EngineeringNotice";
import { Field } from "./Field";
import { ApiError, apiRequest } from "../lib/api";
import { CalculationResult, WindResults } from "./WindResults";

type Route = "WIND-LR" | "WIND-GS" | "WIND-CC";
type Terrain = "open" | "rough";
type PressureApplication = "building_as_whole" | "external_pressure_and_suction";

const n = (value: string) => Number(value);

function errorMessage(error: unknown) {
  const apiError = error as Partial<ApiError>;
  return typeof apiError?.message === "string"
    ? apiError.message
    : "The calculation request could not be completed.";
}

export function WindCalculator() {
  const [route, setRoute] = useState<Route>("WIND-LR");
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [height, setHeight] = useState("12");
  const [windDimension, setWindDimension] = useState("24");
  const [planB, setPlanB] = useState("24");
  const [planW, setPlanW] = useState("30");
  const [roofSlope, setRoofSlope] = useState("5");
  const [terrain, setTerrain] = useState<Terrain>("open");
  const [codeEdition, setCodeEdition] = useState("NBC_2020");
  const [importanceFactor, setImportanceFactor] = useState("1.0");
  const [q, setQ] = useState("0.5");
  const [ct, setCt] = useState("1.0");
  const [application, setApplication] = useState<PressureApplication>("building_as_whole");
  const [referenceHeight, setReferenceHeight] = useState("12");
  const [cgcp, setCgcp] = useState("-1.2");
  const [ch, setCh] = useState("1.0");
  const [componentArea, setComponentArea] = useState("2");
  const [maximumTableArea, setMaximumTableArea] = useState("50");

  function changeRoute(next: Route) {
    setResult(null);
    setError("");
    setRoute(next);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setResult(null);
    setError("");

    try {
      if (route === "WIND-LR") {
        const applicability = await apiRequest<any>("/api/v1/calculations/low-rise/applicability", {
          method: "POST",
          body: JSON.stringify({
            height: n(height),
            plan_dimension_b: n(planB),
            plan_dimension_w: n(planW),
            wind_parallel_dimension: n(windDimension),
            roof_slope: n(roofSlope),
          }),
        });

        if (!applicability.applicable) {
          setResult({ route: "WIND-LR", applicability });
          return;
        }

        const exposure = await apiRequest<{ exposure_factor: number }>(
          "/api/v1/calculations/exposure-factor",
          {
            method: "POST",
            body: JSON.stringify({ terrain, reference_height: n(referenceHeight) }),
          },
        );

        const pressure = await apiRequest<{ pressure: number }>(
          "/api/v1/calculations/low-rise/external-pressure",
          {
            method: "POST",
            body: JSON.stringify({
              code_edition: codeEdition,
              importance_factor: n(importanceFactor),
              reference_velocity_pressure: n(q),
              exposure_factor: exposure.exposure_factor,
              gust_pressure_coefficient: n(cgcp),
              height_factor: n(ch),
            }),
          },
        );

        setResult({
          route: "WIND-LR",
          applicability,
          exposureFactor: exposure.exposure_factor,
          pressure: pressure.pressure,
        });
      } else if (route === "WIND-GS") {
        const data = await apiRequest<any>("/api/v1/calculations/general-static/run", {
          method: "POST",
          body: JSON.stringify({
            code_edition: codeEdition,
            height: n(height),
            wind_parallel_dimension: n(windDimension),
            terrain,
            importance_factor: n(importanceFactor),
            reference_velocity_pressure: n(q),
            topographic_factor: n(ct),
            pressure_application: application,
          }),
        });
        setResult({ route: "WIND-GS", data });
      } else {
        const data = await apiRequest<any>(
          "/api/v1/calculations/components-cladding/area-lookup",
          {
            method: "POST",
            body: JSON.stringify({
              actual_area: n(componentArea),
              maximum_table_area: n(maximumTableArea),
            }),
          },
        );
        setResult({ route: "WIND-CC", ...data });
      }
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  const select = (
    id: string,
    label: string,
    value: string,
    onChange: (value: string) => void,
    options: [string, string][],
  ) => (
    <label className="field" htmlFor={id}>
      <span className="field-label">{label}</span>
      <span className="field-control">
        <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
          {options.map(([optionValue, text]) => (
            <option key={optionValue} value={optionValue}>{text}</option>
          ))}
        </select>
      </span>
    </label>
  );

  return (
    <>
      <header className="hero">
        <div className="hero-copy">
          <span className="eyebrow">WIND-DUAL-001</span>
          <h1>Wind Calculator</h1>
          <p>Engineering calculations are performed by the approved Agent #2 engine through FastAPI.</p>
        </div>
        <span className="status-pill">SI Units</span>
      </header>

      <section className="workspace">
        <nav className="route-tabs" aria-label="Calculation route">
          {(["WIND-LR", "WIND-GS", "WIND-CC"] as Route[]).map((item) => (
            <button key={item} type="button" className={route === item ? "active" : ""} onClick={() => changeRoute(item)}>
              {item}
            </button>
          ))}
        </nav>

        <div className="panel-grid">
          <section className="panel">
            <span className="eyebrow">Engineering inputs</span>
            <h2>{route === "WIND-LR" ? "Low-Rise Wind Pressure" : route === "WIND-GS" ? "General Static Wind Pressure" : "Components & Cladding Area Lookup"}</h2>

            <form onSubmit={submit}>
              {route !== "WIND-CC" && (
                <>
                  <Field label="Building / reference height H" name="height" value={height} onChange={setHeight} unit="m" min={0.01} />
                  <Field label="Wind-parallel dimension D" name="windDimension" value={windDimension} onChange={setWindDimension} unit="m" min={0.01} />
                </>
              )}

              {route === "WIND-LR" && (
                <>
                  <Field label="Plan dimension B" name="planB" value={planB} onChange={setPlanB} unit="m" min={0.01} />
                  <Field label="Plan dimension W" name="planW" value={planW} onChange={setPlanW} unit="m" min={0.01} />
                  <Field label="Roof slope" name="roofSlope" value={roofSlope} onChange={setRoofSlope} unit="deg" min={0} max={90} />
                </>
              )}

              {route !== "WIND-CC" && (
                <>
                  {select("codeEdition", "Code edition", codeEdition, setCodeEdition, [["NBC_2020", "NBC 2020"], ["NBC_2010", "NBC 2010"]])}
                  {select("terrain", "Terrain", terrain, (v) => setTerrain(v as Terrain), [["open", "Open terrain"], ["rough", "Rough terrain"]])}
                  <Field label="Importance factor Iw" name="importanceFactor" value={importanceFactor} onChange={setImportanceFactor} min={0.01} step={0.01} />
                  <Field label="Reference velocity pressure q" name="q" value={q} onChange={setQ} unit="kPa" min={0.001} step={0.001} />
                </>
              )}

              {route === "WIND-LR" && (
                <>
                  <Field label="Reference height h for Ce" name="referenceHeight" value={referenceHeight} onChange={setReferenceHeight} unit="m" min={0.01} />
                  <Field label="Gust pressure coefficient CgCp" name="cgcp" value={cgcp} onChange={setCgcp} step={0.01} />
                  <Field label="Height factor Ch" name="ch" value={ch} onChange={setCh} min={0.001} step={0.001} />
                  <EngineeringNotice
                    title="Current Agent #2 boundary"
                    message="Ce is now calculated automatically from terrain and reference height. The approved Agent #2 package.does not yet contain the complete Low-Rise CgCp lookup dataset or an approved Ch rule, so those two values remain explicit inputs rather than being invented in the web client."
                  />
                </>
              )}

              {route === "WIND-GS" && (
                <>
                  <Field label="Topographic factor Ct" name="ct" value={ct} onChange={setCt} min={0.001} step={0.001} />
                  {select("application", "Pressure application", application, (v) => setApplication(v as PressureApplication), [["building_as_whole", "Building as a whole"], ["external_pressure_and_suction", "External pressure and suction"]])}
                  <EngineeringNotice
                    title="Automatic General Static coefficients"
                    message="For WIND-GS, Ce, Cg and all four Cp values are calculated or selected by the approved Agent #2 engine."
                  />
                </>
              )}

              {route === "WIND-CC" && (
                <>
                  <Field label="Actual component area" name="componentArea" value={componentArea} onChange={setComponentArea} unit="m²" min={0.01} />
                  <Field label="Maximum table area" name="maximumTableArea" value={maximumTableArea} onChange={setMaximumTableArea} unit="m²" min={1} />
                </>
              )}

              <button className="primary-button" type="submit" disabled={loading}>
                {loading ? "Calculating…" : "Run calculation"}
              </button>
            </form>
          </section>

          <section className="panel results-panel">
            <span className="eyebrow">Approved engine output</span>
            <h2>Results</h2>
            {error && <EngineeringNotice title="Calculation unavailable" message={error} />}
            {!result && !error && <div className="empty-state"><strong>No calculation has been run.</strong><span>Enter project values and submit the selected route.</span></div>}
            {result && <WindResults result={result} terrain={terrain} />}
          </section>
        </div>
      </section>
    </>
  );
}
