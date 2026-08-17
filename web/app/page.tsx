"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { EngineeringNotice } from "../components/EngineeringNotice";
import { Field } from "../components/Field";
import { ResultCard } from "../components/ResultCard";
import { ApiError, apiRequest, getCapabilities } from "../lib/api";

type Route = "WIND-LR" | "WIND-GS" | "WIND-CC";
type Capabilities = {
  routes: string[];
  code_editions: string[];
  limitations: string[];
};

type LowRiseApplicability = {
  applicable: boolean;
  height_limit_satisfied: boolean;
  aspect_ratio_limit_satisfied: boolean;
  minimum_plan_dimension: number;
  height_to_minimum_plan_dimension_ratio: number;
};

type LowRiseResult = {
  applicability: LowRiseApplicability;
  pressure?: {
    pressure: number;
    unit: string;
  };
};

type GeneralStaticResult = {
  windward: number;
  leeward: number;
  parallel_wall: number;
  roof: number;
};

type AreaLookupResult = {
  actual_area: number;
  lookup_area: number;
  maximum_table_area: number;
  unit: string;
};

function number(value: string): number {
  return Number(value);
}

function getErrorMessage(error: unknown): string {
  const apiError = error as Partial<ApiError>;
  return typeof apiError?.message === "string"
    ? apiError.message
    : "The calculation request could not be completed.";
}

export default function HomePage() {
  const [route, setRoute] = useState<Route>("WIND-LR");
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null);
  const [capabilityError, setCapabilityError] = useState("");
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [height, setHeight] = useState("12");
  const [planB, setPlanB] = useState("24");
  const [planW, setPlanW] = useState("30");
  const [windDimension, setWindDimension] = useState("24");
  const [roofSlope, setRoofSlope] = useState("5");

  const [codeEdition, setCodeEdition] = useState("NBC_2020");
  const [importanceFactor, setImportanceFactor] = useState("1.0");
  const [referenceVelocityPressure, setReferenceVelocityPressure] = useState("0.5");
  const [exposureFactor, setExposureFactor] = useState("1.0");
  const [gustPressureCoefficient, setGustPressureCoefficient] = useState("-1.2");
  const [heightFactor, setHeightFactor] = useState("1.0");

  const [componentArea, setComponentArea] = useState("2");
  const [maximumTableArea, setMaximumTableArea] = useState("50");

  useEffect(() => {
    getCapabilities()
      .then(setCapabilities)
      .catch((err: unknown) => setCapabilityError(getErrorMessage(err)));
  }, []);

  useEffect(() => {
    setResult(null);
    setError("");
  }, [route]);

  const results = useMemo(() => {
    if (!result) return null;

    if (route === "WIND-LR") {
      const value = result as LowRiseResult;
      const applicability = value.applicability;
      return (
        <div className="results-grid">
          <ResultCard
            title="Applicability"
            value={applicability.applicable ? "Applicable" : "Not applicable"}
            detail="WIND-LR"
          />
          <ResultCard
            title="Height limit"
            value={applicability.height_limit_satisfied ? "Satisfied" : "Not satisfied"}
          />
          <ResultCard
            title="Aspect ratio"
            value={applicability.aspect_ratio_limit_satisfied ? "Satisfied" : "Not satisfied"}
          />
          <ResultCard
            title="H / Bmin"
            value={applicability.height_to_minimum_plan_dimension_ratio.toFixed(3)}
            detail={`Bmin = ${applicability.minimum_plan_dimension.toFixed(2)} m`}
          />
          {value.pressure ? (
            <ResultCard
              title="External wind pressure"
              value={`${value.pressure.pressure.toFixed(3)} ${value.pressure.unit}`}
              detail="Approved Agent #2 engine output"
            />
          ) : null}
        </div>
      );
    }

    if (route === "WIND-GS") {
      const value = result as GeneralStaticResult;
      return (
        <div className="results-grid">
          <ResultCard title="Windward Cp" value={value.windward.toFixed(3)} />
          <ResultCard title="Leeward Cp" value={value.leeward.toFixed(3)} />
          <ResultCard title="Parallel wall Cp" value={value.parallel_wall.toFixed(3)} />
          <ResultCard title="Roof Cp" value={value.roof.toFixed(3)} />
        </div>
      );
    }

    const value = result as AreaLookupResult;
    return (
      <div className="results-grid">
        <ResultCard
          title="Actual component area"
          value={`${value.actual_area.toFixed(2)} ${value.unit}`}
        />
        <ResultCard
          title="Lookup area"
          value={`${value.lookup_area.toFixed(2)} ${value.unit}`}
        />
        <ResultCard
          title="Maximum table area"
          value={`${value.maximum_table_area.toFixed(2)} ${value.unit}`}
        />
      </div>
    );
  }, [result, route]);

  async function runCalculation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      if (route === "WIND-LR") {
        const applicability = await apiRequest<LowRiseApplicability>(
          "/api/v1/calculations/low-rise/applicability",
          {
            method: "POST",
            body: JSON.stringify({
              height: number(height),
              plan_dimension_b: number(planB),
              plan_dimension_w: number(planW),
              wind_parallel_dimension: number(windDimension),
              roof_slope: number(roofSlope),
            }),
          },
        );

        if (!applicability.applicable) {
          setResult({ applicability } satisfies LowRiseResult);
          return;
        }

        const pressure = await apiRequest<{ pressure: number; unit: string }>(
          "/api/v1/calculations/low-rise/external-pressure",
          {
            method: "POST",
            body: JSON.stringify({
              code_edition: codeEdition,
              importance_factor: number(importanceFactor),
              reference_velocity_pressure: number(referenceVelocityPressure),
              exposure_factor: number(exposureFactor),
              gust_pressure_coefficient: number(gustPressureCoefficient),
              height_factor: number(heightFactor),
            }),
          },
        );

        setResult({ applicability, pressure } satisfies LowRiseResult);
      } else if (route === "WIND-GS") {
        setResult(
          await apiRequest<GeneralStaticResult>(
            "/api/v1/calculations/general-static/cp",
            {
              method: "POST",
              body: JSON.stringify({
                height: number(height),
                wind_parallel_dimension: number(windDimension),
              }),
            },
          ),
        );
      } else {
        setResult(
          await apiRequest<AreaLookupResult>(
            "/api/v1/calculations/components-cladding/area-lookup",
            {
              method: "POST",
              body: JSON.stringify({
                actual_area: number(componentArea),
                maximum_table_area: number(maximumTableArea),
              }),
            },
          ),
        );
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header className="hero">
        <div className="hero-copy">
          <span className="eyebrow">WIND-DUAL-001</span>
          <h1>Wind Calculator</h1>
          <p>
            Engineering inputs are sent to the approved FastAPI calculation engine.
            This web client does not duplicate or reinterpret engineering formulas.
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
              aria-pressed={route === item}
              onClick={() => setRoute(item)}
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
                  ? "General Static Pressure Coefficients"
                  : "Components & Cladding Area Lookup"}
            </h2>

            <form onSubmit={runCalculation}>
              {route !== "WIND-CC" && (
                <>
                  <Field label="Building height H" name="height" value={height} onChange={setHeight} unit="m" min={0.01} />
                  <Field label="Wind-parallel dimension D" name="windDimension" value={windDimension} onChange={setWindDimension} unit="m" min={0.01} />
                </>
              )}

              {route === "WIND-LR" && (
                <>
                  <Field label="Plan dimension B" name="planB" value={planB} onChange={setPlanB} unit="m" min={0.01} />
                  <Field label="Plan dimension W" name="planW" value={planW} onChange={setPlanW} unit="m" min={0.01} />
                  <Field label="Roof slope" name="roofSlope" value={roofSlope} onChange={setRoofSlope} unit="deg" min={0} max={90} />

                  <div className="input-section">
                    <span className="eyebrow">Pressure parameters</span>
                    <p className="section-help">
                      These values are passed directly to the approved Agent #2 pressure endpoint.
                    </p>
                  </div>

                  <label className="field" htmlFor="codeEdition">
                    <span className="field-label">Code edition</span>
                    <span className="field-control">
                      <select
                        id="codeEdition"
                        name="codeEdition"
                        value={codeEdition}
                        onChange={(event) => setCodeEdition(event.target.value)}
                      >
                        <option value="NBC_2020">NBC 2020</option>
                        <option value="NBC_2010">NBC 2010</option>
                      </select>
                    </span>
                  </label>

                  <Field label="Importance factor Iw" name="importanceFactor" value={importanceFactor} onChange={setImportanceFactor} min={0.01} step={0.01} />
                  <Field label="Reference velocity pressure q" name="referenceVelocityPressure" value={referenceVelocityPressure} onChange={setReferenceVelocityPressure} unit="kPa" min={0.001} step={0.001} />
                  <Field label="Exposure factor Ce" name="exposureFactor" value={exposureFactor} onChange={setExposureFactor} min={0.001} step={0.001} />
                  <Field label="Gust pressure coefficient CgCp" name="gustPressureCoefficient" value={gustPressureCoefficient} onChange={setGustPressureCoefficient} step={0.01} />
                  <Field label="Height factor Ch" name="heightFactor" value={heightFactor} onChange={setHeightFactor} min={0.001} step={0.001} />

                  <EngineeringNotice
                    title="Engineering data boundary"
                    message="CgCp and Ch are not inferred by the web client. Enter only values supported by the approved project/code source. The backend preserves the Agent #2 engineering rules."
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
                {loading ? "Calculating…" : route === "WIND-LR" ? "Run pressure calculation" : "Run calculation"}
              </button>
            </form>
          </section>

          <section className="panel results-panel">
            <span className="eyebrow">Approved engine output</span>
            <h2>Results</h2>
            {error && <EngineeringNotice title="Calculation unavailable" message={error} />}
            {results ?? (
              <div className="empty-state">
                <strong>No calculation has been run.</strong>
                <span>Enter project values and submit the selected route.</span>
              </div>
            )}
          </section>
        </div>
      </section>

      <section className="limitations">
        <span className="eyebrow">Engineering boundaries</span>
        <h2>Current implementation limitations</h2>
        {capabilityError ? (
          <EngineeringNotice title="Capability metadata unavailable" message={capabilityError} />
        ) : (
          <ul>
            {(capabilities?.limitations ?? ["Loading engineering capability metadata from the API."]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
