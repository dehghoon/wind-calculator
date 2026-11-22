import test from 'node:test';import assert from 'node:assert/strict';import {isAccountHandoff} from '../lib/account-handoff.ts';
const now=1700000000000,nonce='a'.repeat(64),payload={type:'linkoteq:account-handoff',tool:'wind_load',state:nonce,token:'a'.repeat(100),expiresAt:now/1000+3600};
test('handoff requires exact authority, source window, tool, nonce and unexpired session',()=>{
 assert.equal(isAccountHandoff('https://www.linkoteq.com',true,payload,'wind_load',nonce,now),true);
 for(const x of [()=>isAccountHandoff('https://evil.test',true,payload,'wind_load',nonce,now),()=>isAccountHandoff('https://www.linkoteq.com',false,payload,'wind_load',nonce,now),()=>isAccountHandoff('https://www.linkoteq.com',true,payload,'earthquake',nonce,now),()=>isAccountHandoff('https://www.linkoteq.com',true,payload,'wind_load','other',now),()=>isAccountHandoff('https://www.linkoteq.com',true,{...payload,expiresAt:now/1000},'wind_load',nonce,now)])assert.equal(x(),false);
});
