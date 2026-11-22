"use client";
import {useEffect,useRef,useState,type ReactNode} from "react";
import {setToolSession} from "../lib/tool-session";
import {isAccountHandoff} from "../lib/account-handoff";
const origin="https://www.linkoteq.com",tool="wind_load";
export default function ToolAccessGate({children}:{children:ReactNode}){
 const [allowed,setAllowed]=useState(false),[message,setMessage]=useState("Checking your Linkoteq access…");
 const popup=useRef<Window|null>(null),nonce=useRef(""),locallySignedOut=useRef(false);
 useEffect(()=>{
  let revision=0,active=true,currentToken:string|null=null,popupSession=false,expiresAt=0;
  const frame=()=>document.querySelector("linkoteq-header")?.shadowRoot?.querySelector<HTMLIFrameElement>('iframe[src^="https://www.linkoteq.com/account/header-session"]');
  const request=()=>frame()?.contentWindow?.postMessage({type:"linkoteq:tool-session-request"},origin);
  const clear=()=>{++revision;currentToken=null;popupSession=false;setToolSession(null);setAllowed(false);};
  async function verify(token:string,fromPopup:boolean,expiry=0){const check=++revision;
   try{const response=await fetch(origin+"/api/entitlements/execution?tool="+tool,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(12000)});const result=await response.json();if(!active||revision!==check)return;
    if(response.ok&&result.active===true&&result.tool===tool){currentToken=token;popupSession=fromPopup;expiresAt=expiry;setToolSession(token);setAllowed(true);setMessage("");if(fromPopup){popup.current?.close();popup.current=null;nonce.current="";}}
    else{clear();setMessage(response.status===403?"Approved access is required for this calculator.":"Your session could not be verified. Connect your account again.");}
   }catch{if(active&&revision===check){clear();setMessage("Account verification is unavailable. Please retry.");}}
  }
  function receive(event:MessageEvent){
   if(locallySignedOut.current)return;
   if(isAccountHandoff(event.origin,event.source===popup.current,event.data,tool,nonce.current,Date.now())){void verify(event.data.token,true,event.data.expiresAt);return;}
   const f=frame();if(event.origin!==origin||!f||event.source!==f.contentWindow)return;
   if(event.data?.type==="linkoteq:header-account"||event.data?.type==="linkoteq:header-ready"){request();return;}
   if(event.data?.type!=="linkoteq:tool-session")return;
   const token=typeof event.data.token==="string"?event.data.token:null;
   if(token){void verify(token,popupSession,expiresAt);}else if(!popupSession){clear();setMessage("Connect your Linkoteq account to open this calculator.");}
  }
  function signout(){locallySignedOut.current=true;clear();setMessage("Signed out of this calculator. Connect your account to continue.");}
  window.addEventListener("message",receive);window.addEventListener("linkoteq-signout",signout);window.addEventListener("linkoteq-connect-account",connect);
  const start=window.setInterval(request,1000);const timeout=window.setTimeout(()=>{window.clearInterval(start);if(active&&!currentToken)setMessage("Connect your Linkoteq account. This connection also works when embedded browser storage is blocked.");},12000);
  const retry=window.setInterval(()=>{if(popupSession&&expiresAt*1000<=Date.now()+10000){clear();setMessage("Your session expired. Reconnect your account.");}else if(currentToken)void verify(currentToken,popupSession,expiresAt);else request();},60000);request();
  return()=>{active=false;++revision;setToolSession(null);popup.current?.close();popup.current=null;nonce.current="";window.removeEventListener("message",receive);window.removeEventListener("linkoteq-signout",signout);window.removeEventListener("linkoteq-connect-account",connect);window.clearInterval(start);window.clearInterval(retry);window.clearTimeout(timeout);};
 },[]);
 function connect(){locallySignedOut.current=false;const bytes=crypto.getRandomValues(new Uint8Array(32));nonce.current=Array.from(bytes,x=>x.toString(16).padStart(2,"0")).join("");const url=new URL("/account/tool-session",origin);url.searchParams.set("tool",tool);url.searchParams.set("origin",window.location.origin);url.searchParams.set("state",nonce.current);popup.current?.close();popup.current=window.open(url.toString(),"linkoteq-account-connect","popup,width=560,height=740");if(!popup.current)setMessage("Allow the account connection window for this calculator, then retry.");}
 if(allowed)return <>{children}</>;
 return <main className="accessGate"><h1>Linkoteq calculator access</h1><p role="status">{message}</p><button className="primaryButton" type="button" onClick={connect}>Connect / sign in with Linkoteq</button><p><a href={origin+"/customer-login?tool="+tool}>Request Beta access</a>{" · "}<a href={origin+"/tools/wind-load"}>Back to tool page</a></p><p>Beta · Evaluation only. Your backend access is checked for every protected operation.</p></main>;
}
