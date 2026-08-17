"use client";

import { FormEvent, useState } from "react";
import { EngineeringNotice } from "./EngineeringNotice";
import { Field } from "./Field";
import { ApiError, apiRequest } from "../lib/api";
import {
  CalculationResult,
  LowRiseResult,
  GeneralStaticResult,
  ComponentsResult,
  WindResults,
} from "./WindResults";

type Route = "WIND-LR" | "WIND-GS" | "WIND-CC";
type Terrain = "open" | "rough";
type LoadCase = "A" | "B";
type PressureApplication =
  | "building_as_whole"
  | "external_pressure_and_suction";

type LowRiseApplicability = LowRiseResult["applicability"];

type ExposureResponse = {
  exposure_factor: number;
};

type LowRiseLookupResponse = {
  cgcp: number;
  load_case: LoadCase;
  roof_slope: number;
  surface: string;
  source: string;
};

type PressureResponse = {
  pressure: number;
  unit: string;
};

type GeneralStaticRunResponse = GeneralStaticResult["data"];

type ComponentsLookupResponse = {
  cgcp: number;
  zone: string;
  actual_area: number;
  lookup_area: number;
  source: string;
};

const numberValue = (value: string) => Number(value);

function errorMessage(error: unknown): string {
  const apiError = error as Partial<ApiError>;
  return typeof apiError?.message === "string"
    ? apiError.message
    : "The calculation request could not be completed.";
}

const lowRiseSurfaces = [
  "1",
  "1E",
  "2",
  "2E",
  "3",
  "3E",
  "4",
  "4E",
  "5",
  "5E",
  "6",
  "6E",
] as const;

const ccZones = [
  "-C",
  "-OC",
  "-OS",
  "-OR",
  "-S",
  "-R",
  "+S",
  "+R",
  "+C",
] as const;

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
  const [application, setApplication] =
    useState<PressureApplication>("building_as_whole");

  const [loadCase, setLoadCase] = useState<LoadCase>("A");
  const [surface, setSurface] = useState<string>("1");
  const [ch, setCh] = useState("1.0");

  const [componentArea, setComponentArea] = useState("2");
  const [ccZone, setCcZone] = useState<string>("-C");

  function changeRoute(next: Route) {
    setResult(null);
    setError("");
    setRoute(next);
  }

  async function runLowRise(): Promise<void> {
    const applicability = await apiRequest<LowRiseApplicability>(
      "/api/v1/calculations/low-rise/applicability",
      {
        method: "POST",
        body: JSON.stringify({
          height: numberValue(height),
          plan_dimension_b: numberValue(planB),
          plan_dimension_w: numberValue(planW),
          wind_parallel_dimension: numberValue(windDimension),
          roof_slope: numberValue(roofSlope),
        }),
      },
    );

    if (!applicability.applicable) {
      setResult({ route: "WIND-LR", applicability });
      return;
    }

    const [exposure, lookup] = await Promise.all([
      apiRequest<ExposureResponse>("/api/v1/calculations/exposure-factor", {
        method: "POST",
        body: JSON.stringify({
          terrain,
          reference_height: numberValue(height),
        }),
      }),
      apiRequest<LowRiseLookupResponse>(
        "/api/v1/lookups/low-rise/main-structural/cgcp",
        {
          method: "POST",
          body: JSON.stringify({
            load_case: loadCase,
            roof_slope: numberValue(roofSlope),
            surface,
          }),
        },
      ),
    ]);

    const pressure = await apiRequest<PressureResponse>(
      "/api/v1/calculations/low-rise/external-pressure",
      {
        method: "POST",
        body: JSON.stringify({
          code_edition: codeEdition,
          importance_factor: numberValue(importanceFactor),
          reference_velocity_pressure: numberValue(q),
          exposure_factor: exposure.exposure_factor,
          gust_pressure_coefficient: lookup.cgcp,
          height_factor: numberValue(ch),
        }),
      },
    );

    setResult({
      route: "WIND-LR",
      applicability,
      exposureFactor: exposure.exposure_factor,
      cgcp: lookup.cgcp,
      loadCase,
      surface,
      pressure: pressure.pressure,
    });
  }

  async function runGeneralStatic(): Promise<void> {
    const data = await apiRequest<GeneralStaticRunResponse>(
      "/api/v1/calculations/general-static/run",
      {
        method: "POST",
        body: JSON.stringify({
          code_edition: codeEdition,
          height: numberValue(height),
          wind_parallel_dimension: numberValue(windDimension),
          terrain,
          importance_factor: numberValue(importanceFactor),
          reference_velocity_pressure: numberValue(q),
          topographic_factor: numberValue(ct),
          pressure_application: application,
        }),
      },
    );

    setResult({ route: "WIND-GS", data });
  }

  async function runComponents(): Promise<void> {
    const lookup = await apiRequest<ComponentsLookupResponse>(
      "/api/v1/lookups/components-cladding/low-slope-roof/cgcp",
      {
        method: "POST",
        body: JSON.stringify({
          zone: ccZone,
          area: numberValue(componentArea),
        }),
      },
    );

    const componentsResult: ComponentsResult = {
      route: "WIND-CC",
      ...lookup,
    };
    setResult(componentsResult);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setResult(null);
    setError("");

    try {
      if (route === "WIND-LR") {
        await runLowRise();
      } else if (route === "WIND-GS") {
        await runGeneralStatic();
      } else {
        await runComponents();
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
    options: readonly (readonly [string, string])[],
  ) => (
    <label className="field" htmlFor={id}>
      <span className="field-label">{label}</span>
      <span className="field-control">
        <select
          id={id}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        >
          {options.map(([optionValue, text]) => (
            <option key={optionValue} value={optionValue}>
              {text}
            </option>
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
          <p>
            Engineering calculations and approved workbook lookups are
            performed through the FastAPI / Agent #2 engine.
          </p>
        </div>
        <span className="status-pill">SI Units</span>
      </header>

      <section className="workspace">
        <nav className="route-tabs" aria-label="Calculation route">
          {(["WIND-LR", "WIND-GS", "WIND-CC"] as Route[]).map((item) => (
            <button
              key={item}
              type="button"
              className={route === item ? "active" : ""}
              onClick={() => changeRoute(item)}
            >
              {item}
            </button>
          ))}
        </nav>

        <div className="panel-grid">
          <section className="panel">
            <span className="eyebrow">Engineering inputs</span>
            <h2>
              {route === "WIND-LR"
                ? "Low-Rise Wind Pressure"
                : route === "WIND-GS"
                  ? "General Static Wind Pressure"
                  : "Components & Cladding Lookup"}
            </h2>

            <form onSubmit={submit}>
              {route !== "WIND-CC" && (
                <>
                  <Field
                    label="Building / reference height H"
                    name="height"
                    value={height}
                    onChange={setHeight}
                    unit="m"
                    min={0.01}
                  />
                  <Field
                    label="Wind-parallel dimension D"
                    name="windDimension"
                    value={windDimension}
                    onChange={setWindDimension}
                    unit="m"
                    min={0.01}
                  />
                </>
              )}

              {route === "WIND-LR" && (
                <>
                  <Field
                    label="Plan dimension B"
                    name="planB"
                    value={planB}
                    onChange={setPlanB}
                    unit="m"
                    min={0.01}
                  />
                  <Field
                    label="Plan dimension W"
                    name="planW"
                    value={planT}
                    onChange={setPlanW}
                    unit="m"
                    min={0.01}
                  />
                  <Field
                    label="Roof slope"
                    name="roofSlope"
                    value={roofSlope}
                    onChange={setRoofSlope}
                    unit="deg"
                    min={0}
                    max={60}
                  />
                </>
              )}

              {route !== "WIND-CC" && (
                <>
                  {select(
                    "codeEdition",
                    "Code edition",
                    codeEdition,
                    setCodeEdition,
                    [
                      ["NBC_2020", "NBC 2020"],
                      ["NBC_2010", "NBC 2010"],
                    ],
                  )}
                  {select(
                    "terrain",
                    "Terrain",
                    terrain,
                    (value) => setTerrain(value as Terrain),
                    [
                      ["open", "Open terrain"],
                      ["rough", "Rough terrain"],
                    ],
                  )}
                  <Field
                    label="Importance factor Iw"
                    name="importanceFactor"
                    value={importanceFactor}
                    onChange={setImportanceFactor}
                    min={0.01}
                    step={0.01}
                  />
                  <Field
                    label="Reference velocity pressure q"
                    name="q"
                    value={q}
                    onChange={setQ}
                    unit="kPa"
                    min={0.001}
                    step={0.001}
                  />
                </>
              )}

              {route === "WIND-LR" && (
                <>
                  {select(
                    "loadCase",
                    "Load case",
                    loadCase,
                    (value) => setLoadCase(value as LoadCase),
                    [
                      ["A", "Load Case A"],
                      ["B", "Load Case B"],
                    ],
                  )}
                  {select(
                    "surface",
                    "Surface",
                    surface,
                    setSurface,
                    lowRiseSurfaces.map((item) => [item, `Surface ${item}`]),
                  )}
                  <Field
                    label="Height factor Ch"
                    name="ch"
                    value={ch}
                    onChange={setCh}
                    min={0.001}
                    step={0.001}
                  />
                  <EngineeringNotice
                    title="Workbook-backed CgCp"
                    message="CgCp is selected automatically from wind_loadf Sheet1 using Load Case, Roof Slope and Surface. Ce is calculated from Terrain and Height. The supplied workbook uses Ch in pressure equations but does not provide a standalone Ch lookup/formula, so Ch remains an explicit engineering input."
                  />
                </>
              )}

              {route === "WIND-GS" && (
                <>
                  <Field
                    label="Topographic factor Ct"
                    name="ct"
                    value={ct}
                    onChange={setCt}
                    min={0.001}
                    step={0.001}
                  />
                  {select(
                    "application",
                    "Pressure application",
                    application,
                    (value) => setApplication(value as PressureApplication),
                    [
                      ["building_as_whole", "Building as a whole"],
                      [
                        "external_pressure_and_suction",
                        "External pressure and suction",
                      ],
                    ],
                  )}
                  <EngineeringNotice
                    title="Automatic General Static coefficients"
                    message="For WIND-GS, Ce, Cg and all four Cp values are calculated or selected by the approved Agent #2 engine."
                  />
                </>
              )}

              {route === "WIND-CC" && (
                <>
                    {select(
                      "ccZone",
                      "C&C zone",
                      ccZone,
                      setCcZone,
                      ccZones.map((item) => [item, item]),
                    )}
                  <Field
                    label="Tributary area"
                    name="componentArea"
                    value={componentArea}
                    onChange={setComponentArea}
                    unit="m²"
                    min={0.01}
                    step={0.01}
                  />
                  <EngineeringNotice
                    title="Workbook-backed C&C lookup"
                    message="CgCp is selected automatically from wind_loadf Sheet2 using Zone and Tributary Area, including the workbook-defined interpolation and lookup-area bounds."
                  />
                </>
              )}

              <button
                className="primary-button"
                type="submit"
                disabled={loading}
              >
                {loading ? "Calculating…" : "Run calculation"}
              </button>
            </form>
          </section>

          <section className="panel results-panel">
            <span className="eyebrow">Approved engine output</span>
            <h2>Results</h2>
            {error && (
              <EngineeringNotice title="Calculation unavailable" message={error} />
            )}
            {!result && !error && (
              <div className="empty-state">
                <strong>No calculation has been run.</strong>
                <span>Enter project values and submit the selected route.</span>
              </div>
            )}
            {result && <WindResults result={result} terrain={terrain} />}
          </section>
        </div>
      </section>
    </>
  );
}
