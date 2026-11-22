"use client";

import { FormEvent, useEffect, useState, useRef } from "react";
import LoadWorkspace,{DraftReport} from "./LoadWorkspace";
import ParameterHelp from "./ParameterHelp";
import InputGuide from "./InputGuide";
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

type WindClimate = {
  source: { printing: number; reference: string };
  records: { id: string; location: string; provinceOrTerritory: string; q10KPa: number; q50KPa: number }[];
};

type GeneralStaticRunResponse = GeneralStaticResult["data"];

type ComponentsLookupResponse = {
  cgcp: number;
  zone: string;
  actual_area: number;
  lookup_area: number;
  source: string;
  maximum_table_area: number;
  unit: string;
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
  const revision=useRef(0);
  const [reportInputs,setReportInputs]=useState<Record<string,unknown>|null>(null);
  function invalidate(){++revision.current;setResult(null);setReportInputs(null);setError("");setLoading(false);}
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
  const [q, setQ] = useState("");
  const [windClimate, setWindClimate] = useState<WindClimate | null>(null);
  const [climateError, setClimateError] = useState(false);
  const [station, setStation] = useState("");
  const [province, setProvince] = useState("");
  const stations = windClimate?.records ?? [];
  const provinces = Array.from(new Set(stations.map(row => row.provinceOrTerritory)));
  const selectedStation = stations.find(row => row.id === station);
  useEffect(() => {
    const controller = new AbortController();
    apiRequest<WindClimate>("/api/v1/climate/nbc-2020/wind-pressure", { signal: controller.signal })
      .then(result => { if (!controller.signal.aborted) setWindClimate(result); })
      .catch(() => { if (!controller.signal.aborted) setClimateError(true); });
    return () => controller.abort();
  }, []);
  const [ct, setCt] = useState("1.0");
  const [application, setApplication] =
    useState<PressureApplication>("building_as_whole");

  const [loadCase, setLoadCase] = useState<LoadCase>("A");
  const [surface, setSurface] = useState<string>("1");
  const [ch, setCh] = useState("1.0");

  const [componentArea, setComponentArea] = useState("2");
  const [ccZone, setCcZone] = useState<string>("-C");

  function changeRoute(next: Route) {
    invalidate();
    setRoute(next);
  }

  async function runLowRise(rev:number): Promise<void> {
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
      if(rev===revision.current)setResult({ route: "WIND-LR", applicability });
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

    if(rev===revision.current)setResult({
      route: "WIND-LR",
      applicability,
      exposureFactor: exposure.exposure_factor,
      cgcp: lookup.cgcp,
      loadCase,
      surface,
      pressure: pressure.pressure,
    });
  }

  async function runGeneralStatic(rev:number): Promise<void> {
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

    if(rev===revision.current)setResult({ route: "WIND-GS", data });
  }

  async function runComponents(rev:number): Promise<void> {
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
    if(rev===revision.current)setResult(componentsResult);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const rev=++revision.current;
    const snapshot=route==="WIND-CC"?{route,component_area_m2:componentArea,cc_zone:ccZone}:{route,code_edition:codeEdition,height_m:height,wind_parallel_dimension_m:windDimension,terrain,importance_factor_Iw:importanceFactor,reference_pressure_q_kPa:q,climate_station:station,...(route==="WIND-LR"?{plan_B_m:planB,plan_W_m:planW,roof_slope_degrees:roofSlope,load_case:loadCase,surface,Ch:ch}:{Ct:codeEdition==="NBC_2010"?"1 (effective)":ct,pressure_application:application})};
    setLoading(true);
    setResult(null);
    setError("");

    try {
      if (route === "WIND-LR") {
        await runLowRise(rev);
      } else if (route === "WIND-GS") {
        await runGeneralStatic(rev);
      } else {
        await runComponents(rev);
      }
      if(rev===revision.current)setReportInputs(snapshot);
    } catch (err) {
      if(rev===revision.current)setError(errorMessage(err));
    } finally {
      if(rev===revision.current)setLoading(false);
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
      <span className="field-label">{label}<ParameterHelp label={label} text={id==="surface"?"Match the numbered wall/roof region and E variant from the selected edition’s low-building pressure figure for Load Case A or B. E is an edge-region identifier, not east. The geometry sketch does not assign surface numbers.":id==="terrain"?"Choose open or rough terrain from the upwind exposure. Ce is calculated from terrain and height; review terrain transitions separately.":id==="loadCase"?"A and B are separate code loading arrangements. Review the adopted code figure and repeat each required wind orientation.":id==="ccZone"?"Match this coefficient ID to the adopted code’s component/cladding zone and pressure sign. A coefficient is not a completed net pressure calculation.":id==="application"?"Select the pressure application defined by the general-static method. The engine selects its applicable coefficients.":"Select the project-specific option for the adopted code edition. The Illustrated guide explains its source and effect on the calculation."}/></span>
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
          <span className="eyebrow">Wind loads · Beta</span>
          <h1>Wind Calculator</h1>
          <p>
            Select the design route, enter the project inputs and review signed wind pressures. Open the illustrated guide for parameter definitions and surface selection.
          </p>
        </div>
        <span className="status-pill">SI Units</span>
      </header>

      <LoadWorkspace input={<>        <nav className="route-tabs" aria-label="Calculation route">
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

          <section className="panel">
            <span className="eyebrow">Engineering inputs</span>
            <h2>
              {route === "WIND-LR"
                ? "Low-Rise Wind Pressure"
                : route === "WIND-GS"
                  ? "General Static Wind Pressure"
                  : "Components & Cladding Lookup"}
            </h2>

            <form onSubmit={submit} onChange={invalidate}>
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
                    value={planW}
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
                    edition => {
                      if (station) setQ("");
                      setStation("");
                      setCodeEdition(edition);
                    },
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
                  {codeEdition === "NBC_2020" && windClimate ? (
                    <>
                      {select(
                        "windProvince",
                        "Province or territory",
                        province,
                        value => {
                          if (station) setQ("");
                          setStation("");
                          setProvince(value);
                        },
                        [["", "All provinces and territories"], ...provinces.map(name => [name, name] as const)],
                      )}
                      {select(
                        "windStation",
                        "NBC 2020 wind station · second printing",
                        station,
                        id => {
                          const selected = stations.find(row => row.id === id);
                          setStation(id);
                          setQ(selected ? String(selected.q50KPa) : "");
                        },
                        [["", "Enter project pressure manually"], ...stations
                          .filter(row => !province || row.provinceOrTerritory === province)
                          .map(row => [row.id, `${row.location}, ${row.provinceOrTerritory}`] as const)],
                      )}
                      {selectedStation ? (
                        <small>Table C-2 · 1 in 10 years: {selectedStation.q10KPa.toFixed(2)} kPa · 1 in 50 years: {selectedStation.q50KPa.toFixed(2)} kPa (used for calculation).</small>
                      ) : null}
                    </>
                  ) : null}
                  {codeEdition === "NBC_2020" && climateError ? <small>Core wind station lookup unavailable. Enter the project pressure manually.</small> : null}
                  <Field
                    label="Reference velocity pressure q"
                    name="q"
                    value={q}
                    onChange={value => { setStation(""); setQ(value); }}
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
                    lowRiseSurfaces.map((item) => [item, `Surface ${item}`] as const),
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
                      ccZones.map((item) => [item, item] as const),
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

</>} results={          <section className="panel results-panel">
            <span className="eyebrow">Calculation results</span>
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
          </section>} report={<DraftReport title="Wind load calculation" inputs={reportInputs} result={result} formula={route==="WIND-LR"?"pₑ = Iw · q · Ce · (CgCp) · Ch · external pressure only":route==="WIND-GS"?"p = Iw · q · Ce · Ct · Cg · Cp":"C&C coefficient lookup · no net design pressure"}/>} guide={<InputGuide/>}/>
    </>
  );
}
