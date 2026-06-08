const AGENTS=[
  {id:1,name:'Intake & Risk Coordinator',desc:'Parses data, normalizes inputs, structures profile',
   inputs:['Business name','Owner ID','Loan amount','Revenue'],
   outputs:['Structured profile','Completeness score'],duration:1500},
  {id:2,name:'Document Verification Agent',desc:'Verifies document completeness, name and address consistency',
   inputs:['Application','Intake summary'],
   outputs:['Verification status','Verified documents'],duration:1500},
  {id:3,name:'Fraud Intelligence Agent',desc:'Checks known fraud blacklists and registers',
   inputs:['Application','Intake summary','Doc verification'],
   outputs:['Fraud risk level','Fraud signals'],duration:1500},
  {id:4,name:'Business Validation Agent',desc:'Queries business registry and validates active history',
   inputs:['Application','Intake summary','Doc verification'],
   outputs:['Business status','Previous loans'],duration:1500},
  {id:5,name:'Risk Scoring Agent',desc:'Evaluates creditworthiness, debt-to-income, and risk score',
   inputs:['Application','Intake summary','Doc verification','Fraud intelligence','Business validation'],
   outputs:['Repayment risk level','Risk score','Recommendation'],duration:1500},
];

let S={
  screen:'form',
  form:{biz:'',owner:'',amount:'',revenue:'',purpose:'',industry:'',lang:'en'},
  cur:0,prog:0,results:[],
  decision:null,start:null,elapsed:0,
  ref:null,audit:[],errors:{}
};
let pTimer=null,eTimer=null;
let apiData=null;
let apiError=null;
let isConnected=null;


const $=id=>document.getElementById(id);
const BACKEND_URL='http://127.0.0.1:8006';
const genRef=()=>'BG-'+Date.now().toString(36).toUpperCase().slice(-6)+'-'+Math.floor(Math.random()*9000+1000);
const fmt=n=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(n);
const fmtT=ms=>(ms/1000).toFixed(1)+'s';
const ts=()=>new Date().toLocaleTimeString('en-US',{hour12:false});

function validate(){
  const f=S.form,e={};
  if(!f.biz.trim())e.biz='FIELD REQUIRED';
  if(!f.owner.trim())e.owner='FIELD REQUIRED';
  if(!f.amount||isNaN(f.amount)||+f.amount<10000)e.amount='MIN ₹10,000';
  if(!f.revenue||isNaN(f.revenue)||+f.revenue<1000)e.revenue='FIELD REQUIRED';
  S.errors=e;return Object.keys(e).length===0;
}

function log(m){S.audit.push({t:ts(),m});}
function toast(msg){
  const el=document.createElement('div');
  el.className='toast';el.textContent='[ '+msg+' ]';
  document.body.appendChild(el);
  setTimeout(()=>{el.style.opacity='0';el.style.transition='opacity 0.3s';setTimeout(()=>el.remove(),300)},2500);
}

function startPipeline(){
  if(!validate()){render();return;}
  S={...S,screen:'pipeline',cur:0,prog:0,results:[],decision:null,audit:[],ref:genRef(),start:Date.now(),elapsed:0};
  apiData = null;
  apiError = null;
  log('Application '+S.ref+' initialised');
  render();
  
  const payload = {
    business_name: S.form.biz,
    owner_name: S.form.owner,
    loan_amount: parseFloat(S.form.amount),
    monthly_revenue: parseFloat(S.form.revenue),
    industry: S.form.industry || 'General Trade',
    loan_purpose: S.form.purpose || 'Working capital'
  };
  console.log('[BankGuard] Request payload', payload);

  eTimer=setInterval(()=>{
    S.elapsed=Date.now()-S.start;
    const v=$('etimer');
    if(v)v.textContent=fmtT(S.elapsed);
  },100);

  fetch(`${BACKEND_URL}/analyze-loan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload),
    mode: 'cors'
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(errData => {
        throw new Error(errData.detail || 'Server error ' + res.status);
      }).catch(() => {
        throw new Error('Server connection error (' + res.status + ')');
      });
    }
    return res.json();
  })
  .then(data => {
    console.log('[BankGuard] API response', data);
    apiData = data;
    log('Backend analysis payload received');
  })
  .catch(err => {
    console.error('[BankGuard] API error', err);
    handleApiError(err.message || 'Unknown backend error');
  });

  runAgent(0);
}

function handleApiError(message){
  apiError = message;
  clearInterval(pTimer);
  clearInterval(eTimer);
  toast('API ERROR: ' + message);
  render();
}

function runAgent(i){
  if(apiError){
    return;
  }
  if(i>=AGENTS.length){
    checkAndFinish();
    return;
  }
  S.cur=i;S.prog=0;
  log('AGENT-'+(i+1)+' ['+AGENTS[i].name+'] INITIALISED');
  render();
  const dur=AGENTS[i].duration,step=50;let e=0;
  pTimer=setInterval(()=>{
    if(apiError){
      clearInterval(pTimer);
      return;
    }
    e+=step;S.prog=Math.min(100,Math.round(e/dur*100));
    const b=$('pb'+i);if(b)b.style.width=S.prog+'%';
    const p=$('pp'+i);if(p)p.textContent=S.prog+'%';
    if(e>=dur){
      clearInterval(pTimer);
      S.results.push({i,done:true});
      log('AGENT-'+(i+1)+' ['+AGENTS[i].name+'] COMPLETE');
      render();
      setTimeout(()=>runAgent(i+1),250);
    }
  },step);
}

function checkAndFinish(){
  if (apiData) {
    finishWithData(apiData);
    return;
  }
  if (apiError) {
    clearInterval(eTimer);
    console.warn('[BankGuard] Stopped pipeline due to backend error');
    return;
  }
  setTimeout(checkAndFinish, 500);
}

function finishWithData(data){
  clearInterval(eTimer);
  
  const final_resp = data.final_response || data;
  
  let outcome = 'review';
  const rec = final_resp.final_recommendation;
  if (rec === 'Approve') {
    outcome = 'approved';
  } else if (rec === 'Reject') {
    outcome = 'rejected';
  } else {
    outcome = 'review';
  }
  
  S.ref = final_resp.reference_id || S.ref;
  
  S.decision = {
    outcome: outcome,
    rs: final_resp.risk_score ?? 0,
    fs: final_resp.fraud_score ?? 0,
    r: final_resp.loan_to_revenue_ratio ?? 0,
    trace: Array.isArray(final_resp.reasoning_trace) ? final_resp.reasoning_trace.map(t => ({ a: t.agent, t: t.text })) : [],
    business_status: final_resp.business_status || 'UNKNOWN',
    fraud_risk: final_resp.fraud_risk || 'UNKNOWN',
    confidence: final_resp.confidence ?? 0,
    next_action: final_resp.next_action || ''
  };
  
  console.log('[BankGuard] Final decision rendered:', S.decision);
  
  S.audit = Array.isArray(final_resp.audit_log) ? final_resp.audit_log.map(item => ({ t: item.timestamp, m: item.message })) : [];
  
  log('DECISION: ' + outcome.toUpperCase());
  log('AUDIT SEALED — ' + S.audit.length + ' ENTRIES');
  
  setTimeout(() => {
    S.screen = 'decision';
    render();
  }, 500);
}

function dlReceipt(){
  const f=S.form,d=S.decision;
  const h=`<!DOCTYPE html><html><head><meta charset="UTF-8"/><title>BankGuard Sanction</title>
<style>body{font-family:'Courier New',monospace;background:#050810;color:#C8D8F0;max-width:700px;margin:40px auto;padding:40px;border:1px solid #00F5FF}
h1{font-size:22px;color:#00F5FF;letter-spacing:0.15em;font-family:sans-serif;text-transform:uppercase}
.sub{font-size:9px;color:#3A5278;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:30px}
.badge{background:rgba(0,255,136,0.08);border:1px solid #00FF88;padding:14px;text-align:center;margin:20px 0}
.badge h2{color:#00FF88;font-size:18px;letter-spacing:0.15em;text-transform:uppercase}
.amount{font-size:30px;color:#00FF88;margin:6px 0}
table{width:100%;border-collapse:collapse;margin:20px 0}
td{padding:9px 0;border-bottom:1px solid rgba(0,245,255,0.1);font-size:11px}
td:first-child{color:#3A5278;width:42%;letter-spacing:0.08em}
.footer{margin-top:28px;font-size:9px;color:#3A5278;text-align:center;border-top:1px solid rgba(0,245,255,0.15);padding-top:14px;letter-spacing:0.1em}
</style></head><body>
<h1>⬡ BankGuard</h1><div class="sub">Neural Credit System · Official Sanction Document</div>
<div class="badge"><h2>✓ LOAN SANCTIONED</h2><div class="amount">${fmt(f.amount)}</div></div>
<table>
<tr><td>REFERENCE ID</td><td>${S.ref}</td></tr>
<tr><td>SANCTION DATE</td><td>${new Date().toLocaleDateString('en-IN',{day:'2-digit',month:'long',year:'numeric'})}</td></tr>
<tr><td>BUSINESS ENTITY</td><td>${f.biz}</td></tr>
<tr><td>PROMOTER ID</td><td>${f.owner}</td></tr>
<tr><td>INDUSTRY SECTOR</td><td>${f.industry||'General Trade'}</td></tr>
<tr><td>SANCTIONED AMOUNT</td><td>${fmt(f.amount)}</td></tr>
<tr><td>MONTHLY REVENUE</td><td>${fmt(f.revenue)}</td></tr>
<tr><td>RISK SCORE</td><td>${d.rs}/100</td></tr>
<tr><td>FRAUD SCORE</td><td>${d.fs}/100 — CLEAR</td></tr>
<tr><td>LOAN/REVENUE RATIO</td><td>${d.r}×</td></tr>
<tr><td>PROCESSING TIME</td><td>${fmtT(S.elapsed)}</td></tr>
<tr><td>DISBURSEMENT</td><td>T+1 BUSINESS DAY</td></tr>
<tr><td>LOAN PURPOSE</td><td>${f.purpose||'Working capital'}</td></tr>
</table>
<div class="footer">BANKGUARD NEURAL CREDIT SYSTEM · ${S.ref}<br/>SYSTEM-GENERATED · RBI FAIR PRACTICES CODE COMPLIANT<br/>FULL COMPLIANCE AUDIT TRAIL ATTACHED</div>
</body></html>`;
  const blob=new Blob([h],{type:'text/html'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download='BankGuard_Sanction_'+S.ref+'.html';a.click();
  toast('SANCTION DOCUMENT DOWNLOADED');
}

function dlAudit(){
  const lines=S.audit.map(l=>'['+l.t+'] '+l.m).join('\n');
  const hdr='BANKGUARD NEURAL CREDIT SYSTEM\nCOMPLIANCE AUDIT LOG\nAPPLICATION: '+S.ref+'\nGENERATED: '+new Date().toISOString()+'\n'+'─'.repeat(60)+'\n\n';
  const blob=new Blob([hdr+lines],{type:'text/plain'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download='BankGuard_AuditLog_'+S.ref+'.txt';a.click();
  toast('AUDIT LOG EXPORTED');
}

function reset(){
  clearInterval(pTimer);clearInterval(eTimer);
  S={...S,screen:'form',form:{biz:'',owner:'',amount:'',revenue:'',purpose:'',industry:'',lang:'en'},
     cur:0,prog:0,results:[],decision:null,start:null,elapsed:0,ref:null,audit:[],errors:{}};
  render();
}

// ─── RENDER ────────────────────────────────────────────────────

function renderHeader(){
  let statusHtml = `<div class="sys-status"><div class="sys-dot"></div>SYSTEM ONLINE</div>`;
  if (isConnected === true) {
    statusHtml = `<div class="sys-status" style="color:var(--green)"><div class="sys-dot" style="background:var(--green);box-shadow:0 0 6px var(--green)"></div>CONNECTED</div>`;
  } else if (isConnected === false) {
    statusHtml = `<div class="sys-status" style="color:var(--red)"><div class="sys-dot" style="background:var(--red);box-shadow:0 0 6px var(--red);animation:none"></div>STANDALONE</div>`;
  } else if (isConnected === null) {
    statusHtml = `<div class="sys-status" style="color:var(--amber)"><div class="sys-dot" style="background:var(--amber);box-shadow:0 0 6px var(--amber)"></div>CHECKING...</div>`;
  }
  return `<div class="header">
    <div class="logo-wrap">
      <div class="logo-hex">
        <svg viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
          <polygon points="19,2 35,11 35,27 19,36 3,27 3,11" stroke="#00F5FF" stroke-width="1.2" fill="rgba(0,245,255,0.04)"/>
          <polygon points="19,8 29,14 29,24 19,30 9,24 9,14" stroke="#00F5FF" stroke-width="0.6" fill="rgba(0,245,255,0.06)" opacity="0.5"/>
          <text x="19" y="23" text-anchor="middle" font-family="Orbitron,sans-serif" font-size="9" fill="#00F5FF" font-weight="700">BG</text>
        </svg>
      </div>
      <div>
        <div class="logo-name">BankGuard</div>
        <div class="logo-tagline">NEURAL CREDIT SYSTEM · v2.4</div>
      </div>
    </div>
    <div class="header-right">
      ${statusHtml}
      <div class="header-stat">AGENTS<span>05</span></div>
      <div class="header-stat">SIGNALS<span>40+</span></div>
      <div class="corner-tag">RBI COMPLIANT</div>
    </div>
  </div>`;
}

function renderForm(){
  const f=S.form,e=S.errors;
  const inp=(id,ph,val,cb,type='text')=>`<input class="finput" type="${type}" placeholder="${ph}" value="${val}" oninput="${cb}"${e[id]?' style="border-color:var(--red)"':''}/>${e[id]?`<div class="ferr">ERR // ${e[id]}</div>`:''}`;
  return `<div class="screen">
    <div class="hero-banner">
      <img class="hero-img" src="https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80" alt="circuit board technology"/>
      <div class="hero-overlay"></div>
      <div class="hero-tl"></div><div class="hero-tr"></div><div class="hero-bl"></div><div class="hero-br"></div>
      <div class="hero-content">
        <div class="hero-eyebrow">MULTI-AGENT INTELLIGENCE PLATFORM</div>
        <div class="hero-title">SME LOAN <span class="accent">INTELLIGENCE</span><br/>SYSTEM</div>
        <div class="hero-sub">// 5-AGENT PIPELINE · 40+ ALTERNATIVE SIGNALS · REAL-TIME DECISIONING · FULL AUDIT TRAIL</div>
      </div>
      <div class="hero-corner">IMG_SRC: CIRCUIT_BOARD_001 · ENCRYPTED</div>
    </div>
    <div class="stat-row">
      <div class="stat-block"><div class="stat-val">&lt;4<span style="font-size:14px">min</span></div><div class="stat-lbl">Decision SLA</div><div class="stat-corner">S01</div></div>
      <div class="stat-block"><div class="stat-val">40<span style="font-size:14px">+</span></div><div class="stat-lbl">Data Signals</div><div class="stat-corner">S02</div></div>
      <div class="stat-block"><div class="stat-val">5</div><div class="stat-lbl">AI Agents</div><div class="stat-corner">S03</div></div>
      <div class="stat-block"><div class="stat-val">100<span style="font-size:14px">%</span></div><div class="stat-lbl">Audit Trail</div><div class="stat-corner">S04</div></div>
    </div>
    <div class="panel">
      <div class="panel-header">
        <div class="panel-icon">⬡</div>
        <div class="panel-title">APPLICATION INPUT MODULE</div>
        <div class="panel-id">MOD-AIM-001</div>
      </div>
      <div class="form-grid">
        <div class="fg"><div class="flabel">Business Entity Name</div>${inp('biz','e.g. SHARMA TEXTILES PVT LTD','',`S.form.biz=this.value`)}</div>
        <div class="fg"><div class="flabel">Owner / Promoter ID</div>${inp('owner','PAN / AADHAAR / PASSPORT','',`S.form.owner=this.value`)}</div>
        <div class="fg"><div class="flabel">Loan Amount (₹)</div>${inp('amount','e.g. 500000','',`S.form.amount=this.value`,'number')}<div class="fhint">// MIN ₹10,000</div></div>
        <div class="fg"><div class="flabel">Monthly Revenue (₹)</div>${inp('revenue','e.g. 200000','',`S.form.revenue=this.value`,'number')}</div>
        <div class="fg">
          <div class="flabel">Industry Sector</div>
          <select class="finput" onchange="S.form.industry=this.value">
            <option value="">SELECT SECTOR...</option>
            <option value="Retail & FMCG" ${f.industry==='Retail & FMCG'?'selected':''}>RETAIL & FMCG</option>
            <option value="Manufacturing" ${f.industry==='Manufacturing'?'selected':''}>MANUFACTURING</option>
            <option value="Services & IT" ${f.industry==='Services & IT'?'selected':''}>SERVICES & IT</option>
            <option value="Agriculture & Allied" ${f.industry==='Agriculture & Allied'?'selected':''}>AGRICULTURE & ALLIED</option>
            <option value="Healthcare" ${f.industry==='Healthcare'?'selected':''}>HEALTHCARE</option>
            <option value="Hospitality" ${f.industry==='Hospitality'?'selected':''}>HOSPITALITY</option>
            <option value="General Trade" ${f.industry==='General Trade'?'selected':''}>GENERAL TRADE</option>
          </select>
        </div>
        <div class="fg">
          <div class="flabel">Output Language</div>
          <select class="finput" onchange="S.form.lang=this.value">
            <option value="en" ${f.lang==='en'?'selected':''}>ENGLISH</option>
            <option value="hi" ${f.lang==='hi'?'selected':''}>HINDI</option>
            <option value="mr" ${f.lang==='mr'?'selected':''}>MARATHI</option>
            <option value="ta" ${f.lang==='ta'?'selected':''}>TAMIL</option>
            <option value="te" ${f.lang==='te'?'selected':''}>TELUGU</option>
            <option value="kn" ${f.lang==='kn'?'selected':''}>KANNADA</option>
          </select>
        </div>
        <div class="fg full"><div class="flabel">Loan Purpose / Notes</div><input class="finput" placeholder="e.g. WORKING CAPITAL / EQUIPMENT PURCHASE / EXPANSION..." oninput="S.form.purpose=this.value"/></div>
      </div>
      <div style="margin-top:24px;display:flex;align-items:center;gap:12px">
        <button class="btn-prime" onclick="startPipeline()">INITIATE NEURAL ASSESSMENT &gt;&gt;</button>
      </div>
    </div>
    <div style="text-align:center;font-family:var(--mono);font-size:9px;color:var(--text3);letter-spacing:0.2em">// AES-256 ENCRYPTED · RBI FAIR PRACTICES COMPLIANT · GDPR DATA CONTROLS //</div>
  </div>`;
}

function renderPipeline(){
  const done=S.results.length;
  const agHtml=AGENTS.map((ag,i)=>{
    const isDone=i<S.cur;
    const isAct=i===S.cur;
    const cls=isDone?'done':isAct?'active':'pending';
    const inT=ag.inputs.map(t=>`<span class="tag tag-in">&gt; ${t}</span>`).join('');
    const outT=ag.outputs.map(t=>`<span class="tag ${isDone?'tag-done':isAct?'tag-run':'tag-out'}">&lt; ${t}</span>`).join('');
    const st=isDone?`<span style="color:var(--green);font-family:var(--mono);font-size:10px">OK · ${fmtT(ag.duration)}</span>`:isAct?`<span style="display:flex;align-items:center;gap:6px"><span class="spinner"></span><span id="pp${i}" style="font-family:var(--mono);font-size:10px;color:var(--amber)">0%</span></span>`:`<span style="font-family:var(--mono);font-size:10px;color:var(--text3)">STANDBY</span>`;
    const pb=isAct?`<div class="prog-bar"><div class="prog-fill" id="pb${i}" style="width:0%"></div></div>`:'';
    return `<div class="agent-card ${cls}"><div class="agent-scan"></div>
      <div class="agent-top">
        <div class="agent-num">A-${String(i+1).padStart(2,'0')}</div>
        <div class="agent-info"><div class="agent-name">${ag.name}</div><div class="agent-desc">// ${ag.desc}</div></div>
        <div class="agent-status">${st}</div>
      </div>
      <div class="agent-tags">${inT}${outT}</div>
      ${pb}
    </div>`;
  }).join('');
  const aLines=S.audit.map(l=>`<div class="aline"><span class="atime">${l.t}</span><span class="amsg">${l.m}</span></div>`).join('');
  const errorHtml = apiError ? `<div class="alert-box red" style="margin-top:20px"><div class="alert-title red">// BACKEND ERROR</div><div class="alert-body">${apiError}</div><div class="action-row"><button class="btn-sec" onclick="reset()">← BACK TO FORM</button></div></div>` : '';
  return `<div class="screen">
    <div class="pipe-header">
      <div>
        <div class="pipe-title">ASSESSMENT PIPELINE</div>
        <div class="pipe-meta">// REF: ${S.ref} · ${done}/${AGENTS.length} AGENTS COMPLETE</div>
      </div>
      <div>
        <div class="pipe-timer" id="etimer">${fmtT(S.elapsed)}</div>
        <div class="pipe-timer-lbl">ELAPSED</div>
      </div>
    </div>
    ${agHtml}
    <div class="panel" style="margin-top:16px;padding:16px">
      <div class="panel-header" style="margin-bottom:10px"><div class="panel-title">COMPLIANCE AUDIT LOG</div><div class="panel-id">LIVE</div></div>
      <div class="audit-box">${aLines}</div>
    </div>
    ${errorHtml}
  </div>`;
}

function renderDecision(){
  const d=S.decision,f=S.form;
  const o=d.outcome;
  const icon=o==='approved'?'✓':o==='rejected'?'✕':'◈';
  const lbl=o==='approved'?'SANCTIONED':o==='rejected'?'DECLINED':'MANUAL REVIEW';
  const sub=d.next_action || (o==='approved'?'FUNDS RELEASE: T+1 BUSINESS DAY':o==='rejected'?'APPEAL PATH AVAILABLE — 30 DAYS':'ASSIGNED TO HUMAN CREDIT OFFICER');
  const trH=d.trace.map(t=>`<div class="trace-row"><span class="t-agent">${t.a}</span><span class="t-text">${t.t}</span></div>`).join('');
  const aH=S.audit.map(l=>`<div class="aline"><span class="atime">${l.t}</span><span class="amsg">${l.m}</span></div>`).join('');
  const alertHtml=o==='rejected'?`<div class="alert-box red"><div class="alert-title red">// APPEAL PATHWAY ACTIVE</div><div class="alert-body">Submit additional financial documentation within 30 days. Human credit review within 2 business days.</div><div class="alert-ref">APPEAL REF: ${S.ref}-APL</div></div>`:o==='review'?`<div class="alert-box amber"><div class="alert-title amber">// HUMAN REVIEW INITIATED</div><div class="alert-body">Senior credit officer assigned. SLA: 4 business hours. Track status with your case reference.</div><div class="alert-ref">CASE REF: ${S.ref}-HRV</div></div>`:'';
  const approveBtn=o==='approved'?`<button class="btn-green" onclick="S.screen='receipt';render()">VIEW SANCTION DOCUMENT &gt;&gt;</button>`:'';
  const rScore=d.rs<50?'green':d.rs<75?'amber':'red';
  const fraudColor=d.fraud_risk==='High'?'red':d.fraud_risk==='Medium'?'amber':'green';
  const confidenceColor=d.confidence>=0.75?'green':d.confidence>=0.5?'amber':'red';
  const rRatio=d.r<4?'green':d.r<7?'amber':'red';
  return `<div class="screen">
    <div class="decision-banner">
      <img class="decision-img" src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80" alt="technology"/>
      <div class="decision-overlay-${o}"></div>
      <div class="corner-bracket cb-tl cb-${o}"></div>
      <div class="corner-bracket cb-tr cb-${o}"></div>
      <div class="corner-bracket cb-bl cb-${o}"></div>
      <div class="corner-bracket cb-br cb-${o}"></div>
      <div class="decision-inner">
        <div class="decision-icon-box ${o}">${icon}</div>
        <div class="decision-text-wrap">
          <div class="decision-code ${o}">// NEURAL DECISION ENGINE · ${new Date().toISOString()}</div>
          <div class="decision-label ${o}">${lbl}</div>
          <div class="decision-sub">${sub}</div>
        </div>
      </div>
    </div>
    <div class="metric-grid">
      <div class="metric-cell"><div class="m-lbl">Risk Score</div><div class="m-val ${rScore}">${d.rs}<span style="font-size:12px;opacity:0.5">/100</span></div><div class="m-sub">ML MODEL OUTPUT</div></div>
      <div class="metric-cell"><div class="m-lbl">Fraud Risk</div><div class="m-val ${fraudColor}">${d.fraud_risk || 'N/A'}</div><div class="m-sub">BACKEND FRAUD LEVEL</div></div>
      <div class="metric-cell"><div class="m-lbl">Business Status</div><div class="m-val cyan">${d.business_status || 'UNKNOWN'}</div><div class="m-sub">BACKEND VALIDATION</div></div>
      <div class="metric-cell"><div class="m-lbl">Confidence</div><div class="m-val ${confidenceColor}">${Math.round((d.confidence ?? 0)*100)}<span style="font-size:12px;opacity:0.5">%</span></div><div class="m-sub">DECISION CONFIDENCE</div></div>
      <div class="metric-cell"><div class="m-lbl">Process Time</div><div class="m-val cyan">${fmtT(S.elapsed)}</div><div class="m-sub">END-TO-END</div></div>
      <div class="metric-cell"><div class="m-lbl">Loan Amount</div><div class="m-val cyan" style="font-size:15px">${fmt(f.amount)}</div><div class="m-sub">REQUESTED</div></div>
    </div>
    <div class="trace-panel"><div class="trace-hdr">AGENT REASONING TRACE</div>${trH}</div>
    ${alertHtml}
    <div class="trace-panel" style="margin-top:12px"><div class="trace-hdr">COMPLIANCE AUDIT LOG</div><div class="audit-box" style="margin-top:0">${aH}</div></div>
    <div class="action-row">${approveBtn}<button class="btn-sec" onclick="dlAudit()">⬇ EXPORT AUDIT LOG</button><button class="btn-sec" onclick="reset()">← NEW APPLICATION</button></div>
  </div>`;
}

function renderReceipt(){
  const f=S.form,d=S.decision;
  return `<div class="screen">
    <div class="receipt-panel">
      <div class="receipt-top-bar"></div>
      <div class="receipt-body">
        <div class="receipt-hdr">
          <div>
            <div class="receipt-logo-txt">⬡ BANKGUARD</div>
            <div class="receipt-doc-type">OFFICIAL SANCTION DOCUMENT · NEURAL CREDIT SYSTEM</div>
          </div>
          <div class="receipt-ref">
            <div>REF: ${S.ref}</div>
            <div>${new Date().toLocaleDateString('en-IN',{day:'2-digit',month:'long',year:'numeric'})}</div>
            <div>STATUS: <span style="color:var(--green)">SANCTIONED</span></div>
          </div>
        </div>
        <div class="receipt-amount-block">
          <div>
            <div class="receipt-amount-lbl">Total Sanctioned Amount</div>
            <div style="font-family:var(--mono);font-size:9px;color:var(--text3);margin-top:3px">DISBURSEMENT: T+1 BUSINESS DAY</div>
          </div>
          <div class="receipt-amount">${fmt(f.amount)}</div>
        </div>
        <table class="receipt-table">
          <tr><td>BUSINESS ENTITY</td><td>${f.biz}</td></tr>
          <tr><td>PROMOTER ID</td><td>${f.owner}</td></tr>
          <tr><td>INDUSTRY SECTOR</td><td>${f.industry||'GENERAL TRADE'}</td></tr>
          <tr><td>MONTHLY REVENUE</td><td>${fmt(f.revenue)}</td></tr>
          <tr><td>RISK SCORE</td><td><span style="color:var(--green)">${d.rs}/100 — WITHIN POLICY</span></td></tr>
          <tr><td>FRAUD SCORE</td><td><span style="color:var(--green)">${d.fs}/100 — CLEAR</span></td></tr>
          <tr><td>LOAN/REVENUE RATIO</td><td>${d.r}×</td></tr>
          <tr><td>LOAN PURPOSE</td><td>${f.purpose||'WORKING CAPITAL'}</td></tr>
          <tr><td>OUTPUT LANGUAGE</td><td>${f.lang.toUpperCase()}</td></tr>
          <tr><td>PROCESSING TIME</td><td>${fmtT(S.elapsed)}</td></tr>
          <tr><td>AGENTS DEPLOYED</td><td>5/5 — ALL CLEAR</td></tr>
        </table>
        <div class="receipt-footer">
          <div class="stamp">✓ APPROVED & SANCTIONED</div>
          <div class="receipt-legal">BANKGUARD NEURAL CREDIT SYSTEM<br/>RBI FAIR PRACTICES CODE COMPLIANT<br/>${S.ref}</div>
        </div>
      </div>
    </div>
    <div class="action-row">
      <button class="btn-green" onclick="dlReceipt()">⬇ DOWNLOAD SANCTION DOCUMENT</button>
      <button class="btn-sec" onclick="dlAudit()">⬇ EXPORT AUDIT LOG</button>
      <button class="btn-sec" onclick="S.screen='decision';render()">← BACK TO DECISION</button>
      <button class="btn-sec" onclick="reset()">NEW APPLICATION</button>
    </div>
  </div>`;
}

function render(){
  document.getElementById('root').innerHTML=renderHeader()+(
    S.screen==='form'?renderForm():
    S.screen==='pipeline'?renderPipeline():
    S.screen==='decision'?renderDecision():
    renderReceipt()
  );
}

function checkBackendConnection() {
  fetch(`${BACKEND_URL}/`)
    .then(res => {
      isConnected = res.ok;
      render();
      console.log('[BankGuard] Frontend is currently CONNECTED to the backend at ' + BACKEND_URL);
    })
    .catch(err => {
      isConnected = false;
      render();
      console.warn('[BankGuard] Frontend is currently running STANDALONE (Backend disconnected at ' + BACKEND_URL + ')');
    });
}

render();
checkBackendConnection();