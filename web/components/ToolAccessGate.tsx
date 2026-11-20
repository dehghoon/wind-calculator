"use client";
import { useEffect, useState, type ReactNode } from "react";
import { setToolSession } from "../lib/tool-session";
const origin = "https://www.linkoteq.com";
export default function ToolAccessGate({ children }: { children: ReactNode }) {
  const [allowed, setAllowed] = useState(false);
  const [message, setMessage] = useState("Checking your Linkoteq access…");
  useEffect(() => {
    let revision = 0;
    const request = () => {
      const frame = document.querySelector("linkoteq-header")?.shadowRoot?.querySelector<HTMLIFrameElement>('iframe[src^="https://www.linkoteq.com/account/header-session"]');
      frame?.contentWindow?.postMessage({ type: "linkoteq:tool-session-request" }, origin);
    };
    async function receive(event: MessageEvent) {
      const frame = document.querySelector("linkoteq-header")?.shadowRoot?.querySelector<HTMLIFrameElement>('iframe[src^="https://www.linkoteq.com/account/header-session"]');
      if (event.origin !== origin || !frame || event.source !== frame.contentWindow) return;
      if (event.data?.type === "linkoteq:header-account" || event.data?.type === "linkoteq:header-ready") { request(); return; }
      if (event.data?.type !== "linkoteq:tool-session") return;
      window.clearInterval(start); window.clearTimeout(timeout);
      const check = ++revision;
      const token = typeof event.data.token === "string" ? event.data.token : null;

      if (!token) { setAllowed(false); setToolSession(null); setMessage("Sign in to Linkoteq to open this calculator."); return; }
      try {
        const response = await fetch(origin + "/api/entitlements/execution?tool=wind_load", {
          headers: { Authorization: `Bearer ${token}` }, cache: "no-store", signal: AbortSignal.timeout(12000),
        });
        const result = await response.json();
        if (check !== revision) return;
        if (response.ok && result.active === true && result.tool === "wind_load") {
          setToolSession(token); setAllowed(true);
        } else { setAllowed(false); setToolSession(null); setMessage(response.status === 403 ? "Approved Beta access is required. Employees can use their Employee Workspace account." : "Your session could not be verified. Please sign in again."); }
      } catch { if (check === revision) { setAllowed(false); setToolSession(null); setMessage("Access verification is unavailable. Please try again."); } }
    }
    window.addEventListener("message", receive);
    const retry = window.setInterval(request, 60000);
    const start = window.setInterval(request, 1000);
    const timeout = window.setTimeout(() => { window.clearInterval(start); setMessage("Sign in to Linkoteq to open this calculator. If already signed in, allow the Linkoteq account connection and reload."); }, 15000);
    request();
    return () => { ++revision; setToolSession(null); window.removeEventListener("message", receive); window.clearInterval(retry); window.clearInterval(start); window.clearTimeout(timeout); };
  }, []);
  if (allowed) return <>{children}</>;
  return <main className="accessGate"><h1>Linkoteq calculator access</h1><p>{message}</p>
    <p><a className="primaryButton" href={origin + "/customer-login?tool=wind_load"}>Client sign in</a>{" "}
    <a href={origin + "/blog/login"}>Employee sign in</a></p>
    <p>Beta · Under development. Evaluation only.</p></main>;
}
