export function isAccountHandoff(eventOrigin:string, sameWindow:boolean, data:unknown, tool:string, nonce:string, now:number): data is {type:string;tool:string;state:string;token:string;expiresAt:number} {
 if(eventOrigin!=="https://www.linkoteq.com"||!sameWindow||!nonce||!data||typeof data!=="object")return false;
 const x=data as Record<string,unknown>;
 return x.type==="linkoteq:account-handoff"&&x.tool===tool&&x.state===nonce&&typeof x.token==="string"&&x.token.length>20&&typeof x.expiresAt==="number"&&Number.isFinite(x.expiresAt)&&x.expiresAt*1000>now+10000&&x.expiresAt*1000<now+86400000;
}
