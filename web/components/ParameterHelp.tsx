"use client";
import {useRef} from "react";
export default function ParameterHelp({label,text}:{label:string;text:string}){
 const dialog=useRef<HTMLDialogElement>(null);
 return <><button className="help-button" type="button" aria-label={`Help: ${label}`} onClick={e=>{e.preventDefault();e.stopPropagation();dialog.current?.showModal();}}>?</button><dialog className="parameterDialog" ref={dialog} aria-label={label} onClick={e=>e.stopPropagation()}><button type="button" onClick={e=>{e.preventDefault();dialog.current?.close();}}>Close ×</button><h2>{label}</h2><img src="/input-guide.svg" alt="Input geometry and parameter context"/><p>{text}</p><p>Open the Illustrated guide tab for the complete parameter table, formulas, sources and report instructions.</p></dialog></>;
}
