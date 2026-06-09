
const {useState,useEffect,useRef,useCallback,useMemo}=React;
const BACKEND = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://127.0.0.1:8006' 
  : window.location.origin;

// ─── ICONS (inline SVG) ────────────────────────────────────────────────────
const Icon=({name,size=16,color='currentColor',className=''})=>{
  const s={width:size,height:size,display:'inline-block',flexShrink:0,className};
  const icons={
    dashboard:`<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>`,
    apps:`<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>`,
    brain:`<path d="M9.5 2a4.5 4.5 0 0 1 4.5 4.5V20m-4.5-18a4.5 4.5 0 0 0-4.5 4.5V20m4.5-18c1.5 0 2.8.7 3.7 1.8M9.5 2c-1.5 0-2.8.7-3.7 1.8m0 0A4.5 4.5 0 0 0 2 9.5m3.8-5.7A4.5 4.5 0 0 1 9.5 6m0 0a4.5 4.5 0 0 1 4.5-4.5"/><circle cx="12" cy="12" r="2"/>`,
    shield:`<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>`,
    chart:`<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>`,
    audit:`<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>`,
    report:`<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>`,
    settings:`<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>`,
    check:`<polyline points="20 6 9 17 4 12"/>`,
    x:`<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>`,
    alert:`<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>`,
    building:`<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>`,
    user:`<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>`,
    db:`<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>`,
    cpu:`<rect x="9" y="9" width="6" height="6"/><rect x="2" y="2" width="20" height="20" rx="2" ry="2"/><line x1="9" y1="2" x2="9" y2="9"/><line x1="15" y1="2" x2="15" y2="9"/><line x1="9" y1="15" x2="9" y2="22"/><line x1="15" y1="15" x2="15" y2="22"/><line x1="2" y1="9" x2="9" y2="9"/><line x1="2" y1="15" x2="9" y2="15"/><line x1="15" y1="9" x2="22" y2="9"/><line x1="15" y1="15" x2="22" y2="15"/>`,
    zap:`<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>`,
    search:`<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>`,
    sun:`<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>`,
    bell:`<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>`,
    plus:`<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>`,
    play:`<polygon points="5 3 19 12 5 21 5 3"/>`,
    loader:`<line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>`,
    trending:`<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>`,
    info:`<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>`,
    external:`<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>`,
    download:`<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>`,
    eye:`<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>`,
  };
  return React.createElement('svg',{
    xmlns:'http://www.w3.org/2000/svg',viewBox:'0 0 24 24',
    fill:'none',stroke:color,strokeWidth:'2',strokeLinecap:'round',strokeLinejoin:'round',
    style:{width:size,height:size,display:'inline-block',flexShrink:0},
    className,
    dangerouslySetInnerHTML:{__html:icons[name]||''}
  });
};

// ─── DEMO CASES ─────────────────────────────────────────────────────────────
const DEMO_CASES=[
  {id:'DEMO-01',label:'Healthy Approval',name:'ABC Traders Pvt Ltd',owner:'Rajesh Kumar',amount:500000,revenue:200000,industry:'Retail & FMCG',purpose:'Working capital expansion',expected:'Approve',color:'emerald',ratio:'2.5×',note:'Low ratio · clean fraud record · verified business'},
  {id:'DEMO-02',label:'High Risk Ratio',name:'New Startup Ltd',owner:'Test User',amount:50000000,revenue:100000,industry:'Services & IT',purpose:'Expansion',expected:'Reject',color:'rose',ratio:'500×',note:'Loan-to-revenue 500× exceeds 100× ceiling'},
  {id:'DEMO-03',label:'Fraud DB Match',name:'Fake Corp Ltd',owner:'Fraud User',amount:1000000,revenue:100000,industry:'General Trade',purpose:'Equipment purchase',expected:'Reject',color:'rose',ratio:'10×',note:'Matched fraud_cases record in MongoDB — FC_TEST_001'},
];

// ─── GAUGE COMPONENT (SVG semicircle) ───────────────────────────────────────
const RiskGauge=({score=0,animateKey=0})=>{
  const [current,setCurrent]=useState(0);
  const W=220,H=130,cx=W/2,cy=H-10,r=95;
  const startAngle=Math.PI,endAngle=0;
  const scoreAngle=startAngle-(score/100)*Math.PI;
  const curAngle=startAngle-(current/100)*Math.PI;
  const toXY=(a,radius=r)=>({x:cx+radius*Math.cos(a),y:cy-radius*Math.sin(a)});
  const arcPath=(a1,a2,rr)=>{
    const s=toXY(a1,rr),e=toXY(a2,rr);
    return `M${s.x},${s.y} A${rr},${rr} 0 0 1 ${e.x},${e.y}`;
  };
  const needleTip=toXY(curAngle,r-10);
  const getColor=s=>s<30?'#10B981':s<60?'#F59E0B':s<80?'#F97316':'#EF4444';
  const getLabel=s=>s<30?'LOW RISK':s<60?'MODERATE':s<80?'HIGH RISK':'CRITICAL';
  useEffect(()=>{
    setCurrent(0);
    const start=Date.now(),dur=1200;
    const frame=()=>{
      const t=Math.min(1,(Date.now()-start)/dur);
      const ease=1-Math.pow(1-t,3);
      setCurrent(Math.round(score*ease));
      if(t<1)requestAnimationFrame(frame);
    };
    const id=setTimeout(()=>requestAnimationFrame(frame),100);
    return()=>clearTimeout(id);
  },[score,animateKey]);
  const zones=[{a:Math.PI,b:Math.PI*0.7,c:'#10B981'},{a:Math.PI*0.7,b:Math.PI*0.4,c:'#F59E0B'},{a:Math.PI*0.4,b:Math.PI*0.2,c:'#F97316'},{a:Math.PI*0.2,b:0,c:'#EF4444'}];
  return React.createElement('div',{style:{textAlign:'center'}},
    React.createElement('svg',{width:W,height:H,viewBox:`0 0 ${W} ${H}`,style:{overflow:'visible'}},
      React.createElement('defs',null,
        React.createElement('filter',{id:'gaugeglow'},
          React.createElement('feGaussianBlur',{stdDeviation:'3',result:'blur'}),
          React.createElement('feMerge',null,React.createElement('feMergeNode',{in:'blur'}),React.createElement('feMergeNode',{in:'SourceGraphic'}))
        )
      ),
      // Background arc
      React.createElement('path',{d:arcPath(Math.PI,0,r),fill:'none',stroke:'rgba(255,255,255,0.06)',strokeWidth:16,strokeLinecap:'butt'}),
      // Zone arcs
      ...zones.map((z,i)=>React.createElement('path',{key:i,d:arcPath(z.a,z.b,r),fill:'none',stroke:z.c,strokeWidth:14,strokeLinecap:'butt',opacity:0.25})),
      // Active arc
      score>0&&React.createElement('path',{d:arcPath(Math.PI,scoreAngle,r),fill:'none',stroke:getColor(score),strokeWidth:14,strokeLinecap:'round',filter:'url(#gaugeglow)',opacity:0.9}),
      // Tick marks
      ...[0,25,50,75,100].map((v,i)=>{
        const a=Math.PI-(v/100)*Math.PI;
        const o=toXY(a,r+10),n=toXY(a,r+18);
        return React.createElement('g',{key:i},
          React.createElement('line',{x1:o.x,y1:o.y,x2:n.x,y2:n.y,stroke:'rgba(255,255,255,0.2)',strokeWidth:1.5}),
          React.createElement('text',{x:toXY(a,r+28).x,y:toXY(a,r+28).y,textAnchor:'middle',dominantBaseline:'middle',fill:'rgba(255,255,255,0.3)',fontSize:9,fontFamily:'Inter'},v)
        );
      }),
      // Needle
      React.createElement('line',{x1:cx,y1:cy,x2:needleTip.x,y2:needleTip.y,stroke:getColor(current),strokeWidth:3,strokeLinecap:'round',filter:'url(#gaugeglow)'}),
      React.createElement('circle',{cx,cy,r:6,fill:getColor(current),filter:'url(#gaugeglow)'}),
      React.createElement('circle',{cx,cy,r:3,fill:'#0D1432'}),
      // Score text
      React.createElement('text',{x:cx,y:cy-40,textAnchor:'middle',fill:'#E2E8F0',fontSize:32,fontWeight:700,fontFamily:'Inter'},current),
      React.createElement('text',{x:cx,y:cy-20,textAnchor:'middle',fill:'rgba(255,255,255,0.4)',fontSize:11,fontFamily:'Inter'},'/ 100'),
    ),
    React.createElement('div',{style:{marginTop:4,fontSize:12,fontWeight:600,letterSpacing:'0.1em',color:getColor(current)}},getLabel(current))
  );
};

// ─── MINI BAR CHART (inline SVG, no external lib) ───────────────────────────
const BarChart=({data,height=80})=>{
  const max=Math.max(...data.map(d=>Math.max(d.loan,d.revenue)),1);
  const W=300,H=height,barW=18,gap=8;
  const total=data.length*(barW*2+gap)+gap;
  return React.createElement('svg',{viewBox:`0 0 ${total} ${H}`,style:{width:'100%',height:H}},
    data.map((d,i)=>{
      const x=i*(barW*2+gap)+gap;
      const lh=(d.loan/max)*(H-20);
      const rh=(d.revenue/max)*(H-20);
      return React.createElement('g',{key:i},
        React.createElement('rect',{x,y:H-lh-10,width:barW,height:lh,rx:3,fill:'#3B82F6',opacity:0.8}),
        React.createElement('rect',{x:x+barW,y:H-rh-10,width:barW,height:rh,rx:3,fill:'#10B981',opacity:0.8}),
        React.createElement('text',{x:x+barW,y:H-2,textAnchor:'middle',fill:'rgba(255,255,255,0.3)',fontSize:7,fontFamily:'Inter'},d.name)
      );
    })
  );
};

// ─── AGENT TIMELINE ──────────────────────────────────────────────────────────
const AGENTS=[
  {id:1,name:'Intake & Risk Coordinator',desc:'Parses data, normalizes inputs',icon:'zap',color:'#3B82F6'},
  {id:2,name:'Document Verification',desc:'Verifies document completeness',icon:'audit',color:'#8B5CF6'},
  {id:3,name:'Fraud Intelligence',desc:'Checks MongoDB fraud_cases',icon:'shield',color:'#EF4444'},
  {id:4,name:'Business Validation',desc:'Validates business registry',icon:'building',color:'#06B6D4'},
  {id:5,name:'Risk Scoring',desc:'Evaluates creditworthiness',icon:'chart',color:'#F59E0B'},
];

const AgentTimeline=({stage,results})=>
  React.createElement('div',{style:{display:'flex',flexDirection:'column',gap:0}},
    AGENTS.map((ag,i)=>{
      const done=results&&i<results.length;
      const active=stage===i&&!done;
      const status=done?'DONE':active?'RUNNING':'STANDBY';
      const dotColor=done?'#10B981':active?ag.color:'rgba(255,255,255,0.1)';
      return React.createElement('div',{key:ag.id,style:{display:'flex',alignItems:'flex-start',gap:12}},
        React.createElement('div',{style:{display:'flex',flexDirection:'column',alignItems:'center'}},
          React.createElement('div',{style:{width:32,height:32,borderRadius:'50%',background:done?'rgba(16,185,129,0.15)':active?`rgba(${ag.color==='#3B82F6'?'59,130,246':ag.color==='#8B5CF6'?'139,92,246':ag.color==='#EF4444'?'239,68,68':ag.color==='#06B6D4'?'6,182,212':'245,158,11'},0.15)`:'rgba(255,255,255,0.05)',border:`1px solid ${done?'rgba(16,185,129,0.4)':active?ag.color+'66':'rgba(255,255,255,0.1)'}`,display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0,boxShadow:active?`0 0 16px ${ag.color}44`:undefined}},
            done
              ?React.createElement(Icon,{name:'check',size:14,color:'#10B981'})
              :active
                ?React.createElement('div',{className:'spinner',style:{width:14,height:14,borderColor:`${ag.color}33`,borderTopColor:ag.color}})
                :React.createElement(Icon,{name:ag.icon,size:14,color:'rgba(255,255,255,0.25)'})
          ),
          i<AGENTS.length-1&&React.createElement('div',{style:{width:2,height:28,background:done?'rgba(16,185,129,0.3)':'rgba(255,255,255,0.05)',margin:'4px 0'}})
        ),
        React.createElement('div',{style:{flex:1,paddingTop:6,paddingBottom:i<AGENTS.length-1?24:0}},
          React.createElement('div',{style:{display:'flex',alignItems:'center',gap:8,marginBottom:2}},
            React.createElement('span',{style:{fontSize:13,fontWeight:600,color:done?'#E2E8F0':active?ag.color:'rgba(255,255,255,0.3)'}},ag.name),
            React.createElement('span',{className:`badge ${done?'badge-green':active?'badge-blue':''}`,style:done||active?{}:{background:'rgba(255,255,255,0.04)',color:'rgba(255,255,255,0.2)',border:'1px solid rgba(255,255,255,0.08)',fontSize:9}},status)
          ),
          React.createElement('div',{style:{fontSize:11,color:'rgba(255,255,255,0.3)'}},ag.desc)
        )
      );
    })
  );

// ─── FORM COMPONENT ──────────────────────────────────────────────────────────
const LoanForm=({onSubmit,loading})=>{
  const [form,setForm]=useState({biz:'',owner:'',amount:'',revenue:'',industry:'',purpose:''});
  const [errors,setErrors]=useState({});
  const [showDemo,setShowDemo]=useState(false);
  const [activeDemo,setActiveDemo]=useState(null);
  const upd=k=>e=>setForm(f=>({...f,[k]:e.target.value}));
  const loadDemo=idx=>{
    const c=DEMO_CASES[idx];
    setForm({biz:c.name,owner:c.owner,amount:String(c.amount),revenue:String(c.revenue),industry:c.industry,purpose:c.purpose});
    setActiveDemo(idx);setErrors({});
  };
  const validate=()=>{
    const e={};
    if(!form.biz.trim())e.biz='Required';
    if(!form.owner.trim())e.owner='Required';
    if(!form.amount||isNaN(form.amount)||+form.amount<10000)e.amount='Min ₹10,000';
    if(!form.revenue||isNaN(form.revenue)||+form.revenue<1000)e.revenue='Required';
    setErrors(e);return Object.keys(e).length===0;
  };
  const submit=()=>{if(validate())onSubmit(form);};
  const fmt=n=>n?'₹'+Number(n).toLocaleString('en-IN'):'';
  const Field=({label,id,placeholder,type='text',half=false})=>
    React.createElement('div',{style:{gridColumn:half?'span 1':'span 2'}},
      React.createElement('label',{style:{display:'block',fontSize:12,fontWeight:500,color:'rgba(255,255,255,0.5)',marginBottom:6,letterSpacing:'0.04em'}},label),
      React.createElement('input',{className:`input-field ${errors[id]?'border-rose-500':''}`,type,placeholder,
        value:form[id]||'',onChange:upd(id),
        style:errors[id]?{borderColor:'rgba(239,68,68,0.5)',boxShadow:'0 0 0 3px rgba(239,68,68,0.1)'}:{}}),
      errors[id]&&React.createElement('p',{style:{fontSize:11,color:'#FCA5A5',marginTop:4}},errors[id])
    );
  const Select=({label,id,options})=>
    React.createElement('div',null,
      React.createElement('label',{style:{display:'block',fontSize:12,fontWeight:500,color:'rgba(255,255,255,0.5)',marginBottom:6,letterSpacing:'0.04em'}},label),
      React.createElement('select',{className:'input-field',value:form[id]||'',onChange:upd(id)},
        React.createElement('option',{value:''},'Select...'),
        options.map(o=>React.createElement('option',{key:o,value:o},o))
      )
    );
  return React.createElement('div',null,
    // Demo toggle
    React.createElement('div',{style:{marginBottom:24}},
      React.createElement('button',{className:'btn-demo',onClick:()=>setShowDemo(s=>!s),style:{display:'flex',alignItems:'center',justifyContent:'center',gap:8}},
        React.createElement(Icon,{name:'play',size:14,color:'#A78BFA'}),
        showDemo?'Hide Demo Cases':'⬡ Load Demo Cases — Hackathon Preview'
      )
    ),
    // Demo cases panel
    showDemo&&React.createElement('div',{style:{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:12,marginBottom:24},className:'fade-in'},
      DEMO_CASES.map((c,i)=>{
        const expColor=c.expected==='Approve'?'#10B981':'#EF4444';
        return React.createElement('div',{key:c.id,className:`demo-case-card ${activeDemo===i?'active':''}`,onClick:()=>loadDemo(i)},
          React.createElement('div',{style:{fontSize:9,color:'rgba(255,255,255,0.3)',letterSpacing:'0.15em',marginBottom:6}},c.id+' · '+c.label.toUpperCase()),
          React.createElement('div',{style:{fontSize:13,fontWeight:700,color:'#E2E8F0',marginBottom:4}},c.name),
          React.createElement('div',{style:{fontSize:10,color:'rgba(255,255,255,0.4)',lineHeight:1.7,marginBottom:8}},
            'Ratio: ',React.createElement('span',{style:{color:'#60A5FA',fontWeight:600}},c.ratio),React.createElement('br'),c.note
          ),
          React.createElement('div',{style:{display:'inline-flex',alignItems:'center',gap:4,padding:'3px 10px',borderRadius:100,fontSize:10,fontWeight:600,background:`${expColor}1A`,color:expColor,border:`1px solid ${expColor}4D`}},
            c.expected==='Approve'?'✓ APPROVE':'✕ REJECT'
          )
        );
      })
    ),
    // Form grid
    React.createElement('div',{style:{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginBottom:24}},
      React.createElement(Field,{label:'Business Entity Name',id:'biz',placeholder:'e.g. ABC Traders Pvt Ltd',half:false}),
      React.createElement(Field,{label:'Owner / Promoter',id:'owner',placeholder:'Full name',half:false}),
      React.createElement(Field,{label:'Loan Amount (₹)',id:'amount',placeholder:'e.g. 500000',type:'number',half:true}),
      React.createElement(Field,{label:'Monthly Revenue (₹)',id:'revenue',placeholder:'e.g. 200000',type:'number',half:true}),
      React.createElement('div',null,
        React.createElement('label',{style:{display:'block',fontSize:12,fontWeight:500,color:'rgba(255,255,255,0.5)',marginBottom:6}}, 'Industry Sector'),
        React.createElement('select',{className:'input-field',value:form.industry||'',onChange:upd('industry')},
          React.createElement('option',{value:''},'Select sector...'),
          ['Retail & FMCG','Manufacturing','Services & IT','Agriculture & Allied','Healthcare','Hospitality','General Trade'].map(o=>React.createElement('option',{key:o,value:o},o))
        )
      ),
      React.createElement('div',null,
        React.createElement('label',{style:{display:'block',fontSize:12,fontWeight:500,color:'rgba(255,255,255,0.5)',marginBottom:6}},'Loan Purpose'),
        React.createElement('input',{className:'input-field',placeholder:'e.g. Working capital / Equipment...',value:form.purpose||'',onChange:upd('purpose')})
      )
    ),
    // Summary preview
    (form.biz||form.amount)&&React.createElement('div',{style:{background:'rgba(59,130,246,0.06)',border:'1px solid rgba(59,130,246,0.15)',borderRadius:12,padding:12,marginBottom:16,display:'flex',gap:16,flexWrap:'wrap'}},
      form.biz&&React.createElement('span',{style:{fontSize:12,color:'rgba(255,255,255,0.5)'}},React.createElement('span',{style:{color:'rgba(255,255,255,0.3)'}}, 'Entity: '),React.createElement('span',{style:{color:'#60A5FA',fontWeight:500}},form.biz)),
      (form.amount&&form.revenue)&&React.createElement('span',{style:{fontSize:12,color:'rgba(255,255,255,0.5)'}},
        React.createElement('span',{style:{color:'rgba(255,255,255,0.3)'}}, 'Ratio: '),
        React.createElement('span',{style:{color:+form.amount/+form.revenue>100?'#EF4444':+form.amount/+form.revenue>20?'#F59E0B':'#10B981',fontWeight:600}},
          (+form.amount/+form.revenue).toFixed(1),'×'
        )
      )
    ),
    React.createElement('button',{className:'btn-primary',onClick:submit,disabled:loading,style:{width:'100%',display:'flex',alignItems:'center',justifyContent:'center',gap:10}},
      loading&&React.createElement('div',{className:'spinner',style:{width:16,height:16}}),
      loading?'Running Neural Assessment…':'Initiate Neural Assessment →'
    )
  );
};

// ─── RESULTS DASHBOARD ───────────────────────────────────────────────────────
const ResultsDashboard=({data,form,elapsed,onReset})=>{
  const fr=data.final_response||{};
  const a3=data.agent_3_output||{};
  const a4=data.agent_4_output||{};
  const a5=data.agent_5_output||{};
  const rec=fr.final_recommendation||'';
  const isApproved=rec==='Approve';
  const isRejected=rec==='Reject';
  const outcome=isApproved?'approved':isRejected?'rejected':'review';
  const decColor=isApproved?'#10B981':isRejected?'#EF4444':'#F59E0B';
  const fraudColor=fr.fraud_risk==='High'?'#EF4444':fr.fraud_risk==='Medium'?'#F59E0B':'#10B981';
  const fmt=n=>n?'₹'+Number(n).toLocaleString('en-IN'):'-';
  const ratio=+(fr.loan_to_revenue_ratio||0);
  const conf=Math.round((fr.confidence||0)*100);
  const explanation=fr.decision_explanation||'';
  const reasons=explanation.split('\n').filter(l=>l.startsWith('*')).map(l=>l.replace('* ',''));
  const chartData=[{name:'Loan',loan:+(form.amount||0),revenue:0},{name:'Revenue',loan:0,revenue:+(form.revenue||0)*12}];

  return React.createElement('div',{className:'fade-in',style:{display:'flex',flexDirection:'column',gap:20}},

    // ── FINAL DECISION ──────────────────────────────────────────────────────
    React.createElement('div',{style:{borderRadius:24,border:`2px solid ${decColor}`,padding:32,textAlign:'center',position:'relative',overflow:'hidden',background:`${decColor}08`,transition:'all 0.5s'},className:`decision-glow-${outcome}`},
      React.createElement('div',{style:{position:'absolute',inset:0,background:`radial-gradient(circle at 50% 0%, ${decColor}18, transparent 70%)`,pointerEvents:'none'}}),
      React.createElement('div',{style:{fontSize:11,letterSpacing:'0.2em',color:'rgba(255,255,255,0.4)',marginBottom:8,fontFamily:'JetBrains Mono, monospace'}},
        '// NEURAL DECISION ENGINE · '+new Date().toISOString()
      ),
      React.createElement('div',{style:{fontSize:64,marginBottom:8}},isApproved?'✓':isRejected?'✕':'◈'),
      React.createElement('div',{style:{fontSize:40,fontWeight:800,color:decColor,letterSpacing:'0.05em',textTransform:'uppercase',marginBottom:8}},
        isApproved?'SANCTIONED':isRejected?'DECLINED':'MANUAL REVIEW'
      ),
      React.createElement('div',{style:{display:'inline-flex',alignItems:'center',gap:8,padding:'8px 20px',borderRadius:100,background:`${decColor}1A`,border:`1px solid ${decColor}4D`,marginBottom:12}},
        React.createElement('span',{style:{fontSize:14,fontWeight:600,color:decColor}},'Confidence: '+conf+'%'),
      ),
      React.createElement('div',{style:{fontSize:13,color:'rgba(255,255,255,0.5)',maxWidth:500,margin:'0 auto',lineHeight:1.6}},fr.next_action||''),
      React.createElement('div',{style:{marginTop:16}},
        React.createElement('div',{style:{fontSize:11,color:'rgba(255,255,255,0.3)',fontFamily:'JetBrains Mono, monospace'}},
          `REF: ${fr.reference_id||'—'} · ELAPSED: ${(elapsed/1000).toFixed(1)}s · AGENTS: 5/5`
        )
      )
    ),

    // ── METRICS ROW ─────────────────────────────────────────────────────────
    React.createElement('div',{style:{display:'grid',gridTemplateColumns:'repeat(6,1fr)',gap:12}},
      [
        {label:'Risk Score',val:fr.risk_score||0,unit:'/100',color:+(fr.risk_score||0)<50?'#10B981':+(fr.risk_score||0)<75?'#F59E0B':'#EF4444',sub:'AGENT-5'},
        {label:'Fraud Risk',val:fr.fraud_risk||'—',color:fraudColor,sub:'AGENT-3'},
        {label:'Business',val:fr.business_status||'—',color:'#60A5FA',sub:'AGENT-4'},
        {label:'Confidence',val:conf+'%',color:conf>=75?'#10B981':conf>=50?'#F59E0B':'#EF4444',sub:'OVERALL'},
        {label:'Loan/Revenue',val:ratio+'×',color:ratio>100?'#EF4444':ratio>20?'#F59E0B':'#10B981',sub:'RATIO'},
        {label:'Elapsed',val:(elapsed/1000).toFixed(1)+'s',color:'#818CF8',sub:'PROCESSING'},
      ].map((m,i)=>React.createElement('div',{key:i,className:'metric-card',style:{textAlign:'center'}},
        React.createElement('div',{style:{fontSize:9,letterSpacing:'0.15em',color:'rgba(255,255,255,0.3)',marginBottom:8,textTransform:'uppercase'}},m.label),
        React.createElement('div',{style:{fontSize:20,fontWeight:700,color:m.color,marginBottom:4}},m.val),
        React.createElement('div',{style:{fontSize:8,color:'rgba(255,255,255,0.2)',letterSpacing:'0.1em'}},m.sub)
      ))
    ),

    // ── MAIN CONTENT GRID ────────────────────────────────────────────────────
    React.createElement('div',{style:{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:16}},

      // Risk Gauge
      React.createElement('div',{className:'metric-card'},
        React.createElement('div',{style:{fontSize:11,fontWeight:600,color:'rgba(255,255,255,0.4)',letterSpacing:'0.1em',marginBottom:16,textTransform:'uppercase'}},
          '⬡ Risk Meter'
        ),
        React.createElement(RiskGauge,{score:+(fr.risk_score||0),animateKey:Date.now()})
      ),

      // Loan Summary
      React.createElement('div',{className:'metric-card'},
        React.createElement('div',{style:{fontSize:11,fontWeight:600,color:'rgba(255,255,255,0.4)',letterSpacing:'0.1em',marginBottom:16,textTransform:'uppercase'}},'⬡ Loan Summary'),
        ...[
          {l:'Business',v:form.biz||'—',icon:'building'},
          {l:'Owner',v:form.owner||'—',icon:'user'},
          {l:'Industry',v:form.industry||'—',icon:'chart'},
          {l:'Loan Amount',v:fmt(form.amount),icon:'trending'},
          {l:'Monthly Revenue',v:fmt(form.revenue),icon:'trending'},
        ].map((r,i)=>React.createElement('div',{key:i,style:{display:'flex',alignItems:'center',gap:10,padding:'8px 0',borderBottom:'1px solid rgba(255,255,255,0.04)'}},
          React.createElement(Icon,{name:r.icon,size:13,color:'rgba(255,255,255,0.25)'}),
          React.createElement('span',{style:{fontSize:11,color:'rgba(255,255,255,0.35)',flex:1}},r.l),
          React.createElement('span',{style:{fontSize:12,fontWeight:500,color:'#E2E8F0',textAlign:'right',maxWidth:130,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}},r.v)
        ))
      ),

      // Fraud Detection
      React.createElement('div',{className:'metric-card'},
        React.createElement('div',{style:{fontSize:11,fontWeight:600,color:'rgba(255,255,255,0.4)',letterSpacing:'0.1em',marginBottom:16,textTransform:'uppercase'}},'⬡ Fraud Detection'),
        React.createElement('div',{style:{display:'flex',flexDirection:'column',gap:10}},
          React.createElement('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 12px',borderRadius:10,background:'rgba(255,255,255,0.03)',border:'1px solid rgba(255,255,255,0.06)'}},
            React.createElement('span',{style:{fontSize:11,color:'rgba(255,255,255,0.4)'}},'Fraud Risk'),
            React.createElement('span',{className:'badge',style:{background:`${fraudColor}1A`,color:fraudColor,border:`1px solid ${fraudColor}4D`,fontSize:10}},fr.fraud_risk||'—')
          ),
          React.createElement('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 12px',borderRadius:10,background:'rgba(255,255,255,0.03)',border:'1px solid rgba(255,255,255,0.06)'}},
            React.createElement('span',{style:{fontSize:11,color:'rgba(255,255,255,0.4)'}},'DB Match'),
            React.createElement('span',{className:a3.fraud_match?'badge badge-red':'badge badge-green',style:{fontSize:10}},a3.fraud_match?'MATCH FOUND':'CLEAR')
          ),
          React.createElement('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 12px',borderRadius:10,background:'rgba(255,255,255,0.03)',border:'1px solid rgba(255,255,255,0.06)'}},
            React.createElement('span',{style:{fontSize:11,color:'rgba(255,255,255,0.4)'}},'MongoDB'),
            React.createElement('span',{className:a3.mongodb_connected?'badge badge-green':'badge badge-red',style:{fontSize:10}},a3.mongodb_connected?'CONNECTED':'OFFLINE')
          ),
          a3.fraud_records_found>0&&React.createElement('div',{style:{padding:'8px 12px',borderRadius:10,background:'rgba(239,68,68,0.08)',border:'1px solid rgba(239,68,68,0.2)'}},
            React.createElement('div',{style:{fontSize:10,color:'#FCA5A5',marginBottom:4,fontWeight:600}},'Fraud Signals Detected'),
            (a3.fraud_signals||[]).filter(s=>s!=='None').map((s,i)=>React.createElement('div',{key:i,style:{fontSize:10,color:'rgba(255,255,255,0.4)',lineHeight:1.5}},s))
          )
        )
      )
    ),

    // ── EXPLANATION + AGENT TIMELINE ────────────────────────────────────────
    React.createElement('div',{style:{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}},

      // AI Explainability
      React.createElement('div',{className:'metric-card'},
        React.createElement('div',{style:{fontSize:11,fontWeight:600,color:'rgba(255,255,255,0.4)',letterSpacing:'0.1em',marginBottom:16,textTransform:'uppercase',display:'flex',alignItems:'center',gap:8}},
          React.createElement(Icon,{name:'brain',size:13,color:'rgba(255,255,255,0.3)'}),
          '⬡ Why This Decision'
        ),
        // Decision label
        React.createElement('div',{style:{padding:'12px 16px',borderRadius:12,background:`${decColor}0D`,border:`1px solid ${decColor}33`,marginBottom:14}},
          React.createElement('div',{style:{fontSize:13,fontWeight:700,color:decColor,marginBottom:4}},
            isApproved?'✓ APPROVED':isRejected?'✕ REJECTED':'◈ MANUAL REVIEW'
          ),
          React.createElement('div',{style:{fontSize:11,color:'rgba(255,255,255,0.4)'}},`Confidence: ${conf}%`)
        ),
        // Key reasons
        reasons.length>0
          ?reasons.map((r,i)=>React.createElement('div',{key:i,className:'finding-item'},
              React.createElement('div',{style:{width:18,height:18,borderRadius:'50%',background:isApproved?'rgba(16,185,129,0.15)':'rgba(239,68,68,0.15)',border:`1px solid ${isApproved?'rgba(16,185,129,0.4)':'rgba(239,68,68,0.4)'}`,display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0}},
                React.createElement(Icon,{name:isApproved?'check':'x',size:10,color:isApproved?'#10B981':'#EF4444'})
              ),
              React.createElement('span',{style:{fontSize:11,color:'rgba(255,255,255,0.6)',lineHeight:1.5}},r)
            ))
          :React.createElement('div',{style:{fontSize:11,color:'rgba(255,255,255,0.3)'}},explanation||'Analysis complete.')
      ),

      // Agent Timeline
      React.createElement('div',{className:'metric-card'},
        React.createElement('div',{style:{fontSize:11,fontWeight:600,color:'rgba(255,255,255,0.4)',letterSpacing:'0.1em',marginBottom:16,textTransform:'uppercase',display:'flex',alignItems:'center',gap:8}},
          React.createElement(Icon,{name:'cpu',size:13,color:'rgba(255,255,255,0.3)'}),
          '⬡ Agent Pipeline'
        ),
        React.createElement(AgentTimeline,{stage:5,results:[1,2,3,4,5]}),
        // Audit entries
        fr.audit_log&&React.createElement('div',{style:{marginTop:14,paddingTop:14,borderTop:'1px solid rgba(255,255,255,0.06)'}},
          React.createElement('div',{style:{fontSize:9,letterSpacing:'0.12em',color:'rgba(255,255,255,0.25)',marginBottom:8,textTransform:'uppercase'}}, 'Audit Log'),
          React.createElement('div',{style:{maxHeight:100,overflowY:'auto'}},
            (fr.audit_log||[]).map((l,i)=>React.createElement('div',{key:i,style:{display:'flex',gap:8,marginBottom:4}},
              React.createElement('span',{style:{fontSize:9,color:'#3B82F6',fontFamily:'JetBrains Mono, monospace',flexShrink:0}},l.timestamp),
              React.createElement('span',{style:{fontSize:9,color:'rgba(255,255,255,0.3)'}},l.message)
            ))
          )
        )
      )
    ),

    // ── REASONING TRACE ──────────────────────────────────────────────────────
    React.createElement('div',{className:'metric-card'},
      React.createElement('div',{style:{fontSize:11,fontWeight:600,color:'rgba(255,255,255,0.4)',letterSpacing:'0.1em',marginBottom:14,textTransform:'uppercase'}},'⬡ Reasoning Trace'),
      React.createElement('div',{style:{display:'flex',flexDirection:'column',gap:8}},
        (fr.reasoning_trace||[]).map((t,i)=>{
          const agentColors={'INTAKE':'#3B82F6','DOC-VERIFY':'#8B5CF6','FRAUD-INTEL':'#EF4444','BIZ-VALID':'#06B6D4','RISK-SCORING':'#F59E0B'};
          const c=agentColors[t.agent]||'#60A5FA';
          return React.createElement('div',{key:i,style:{display:'flex',gap:12,padding:'10px 14px',borderRadius:10,background:'rgba(255,255,255,0.03)',border:'1px solid rgba(255,255,255,0.06)'}},
            React.createElement('span',{style:{fontSize:9,padding:'2px 8px',borderRadius:4,background:`${c}1A`,color:c,border:`1px solid ${c}4D`,fontFamily:'JetBrains Mono, monospace',letterSpacing:'0.08em',flexShrink:0,alignSelf:'flex-start'}},t.agent),
            React.createElement('span',{style:{fontSize:11,color:'rgba(255,255,255,0.5)',lineHeight:1.55}},t.text)
          );
        })
      )
    ),

    // ── ACTIONS ──────────────────────────────────────────────────────────────
    React.createElement('div',{style:{display:'flex',gap:12,justifyContent:'center'}},
      React.createElement('button',{className:'btn-secondary',onClick:onReset,style:{display:'flex',alignItems:'center',gap:6}},
        React.createElement(Icon,{name:'plus',size:13,color:'currentColor'}),'New Application'
      ),
      React.createElement('button',{className:'btn-secondary',style:{display:'flex',alignItems:'center',gap:6},onClick:()=>{
        const lines=(fr.audit_log||[]).map(l=>`[${l.timestamp}] ${l.message}`).join('\n');
        const blob=new Blob([`BANKGUARD AUDIT LOG\nREF: ${fr.reference_id}\n\n${lines}`],{type:'text/plain'});
        const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`BankGuard_${fr.reference_id}.txt`;a.click();
      }},React.createElement(Icon,{name:'download',size:13,color:'currentColor'}),'Export Audit Log')
    )
  );
};

// ─── PIPELINE VIEW ───────────────────────────────────────────────────────────
const PipelineView=({stage,form,startTime})=>{
  const [elapsed,setElapsed]=useState(0);
  useEffect(()=>{
    const id=setInterval(()=>setElapsed(Date.now()-startTime),100);
    return()=>clearInterval(id);
  },[startTime]);
  return React.createElement('div',{className:'fade-in',style:{display:'flex',flexDirection:'column',gap:20}},
    // Header
    React.createElement('div',{style:{textAlign:'center',padding:'32px 0'}},
      React.createElement('div',{style:{width:64,height:64,borderRadius:'50%',background:'rgba(59,130,246,0.1)',border:'1px solid rgba(59,130,246,0.3)',display:'flex',alignItems:'center',justifyContent:'center',margin:'0 auto 16px',boxShadow:'0 0 30px rgba(59,130,246,0.3)'}},
        React.createElement('div',{className:'spinner',style:{width:28,height:28}})
      ),
      React.createElement('h2',{style:{fontSize:22,fontWeight:700,color:'#E2E8F0',marginBottom:6}},'Neural Assessment Running'),
      React.createElement('div',{style:{fontSize:13,color:'rgba(255,255,255,0.4)'}},form.biz+' · '+((elapsed/1000).toFixed(1))+'s elapsed'),
    ),
    // Agents
    React.createElement('div',{className:'metric-card'},
      React.createElement('div',{style:{fontSize:11,fontWeight:600,color:'rgba(255,255,255,0.4)',letterSpacing:'0.1em',marginBottom:20,textTransform:'uppercase'}},'⬡ Agent Pipeline — Live'),
      React.createElement(AgentTimeline,{stage,results:Array(stage).fill(1)})
    )
  );
};

// ─── SIDEBAR ─────────────────────────────────────────────────────────────────
const Sidebar=({active,onNav,screen,isConnected})=>{
  // Only 4 real, implemented nav items
  const mainItems=[
    {id:'dashboard',icon:'dashboard',label:'Dashboard',desc:'Overview & assessment'},
    {id:'applications',icon:'apps',label:'Applications',desc:'Submit loan application'},
  ];
  const extraItems=[
    {id:'demo',icon:'play',label:'Demo Cases',desc:'Preloaded hackathon demos'},
    {id:'about',icon:'info',label:'About BankGuard',desc:'Platform information'},
  ];
  const statusRows=[
    {dot:isConnected?'#10B981':'#EF4444',label:isConnected?'SYSTEM ONLINE':'SYSTEM OFFLINE',sub:null,pulse:!!isConnected},
    {dot:isConnected?'#10B981':'#EF4444',label:isConnected?'MongoDB Connected':'MongoDB Disconnected',sub:null},
    {dot:isConnected?'#3B82F6':'#6B7280',label:isConnected?'MCP Active':'MCP Inactive',sub:null},
    {dot:isConnected?'#818CF8':'#6B7280',label:isConnected?'5 Agents Ready':'Agents Offline',sub:null},
  ];
  const NavItem=({item})=>React.createElement('div',{
    className:`sidebar-item ${active===item.id?'active':''}`,
    onClick:()=>onNav(item.id),
    title:item.desc
  },
    React.createElement('div',{className:'sidebar-icon-wrap'},
      React.createElement(Icon,{name:item.icon,size:15,color:active===item.id?'#60A5FA':'#6B7280'})
    ),
    React.createElement('span',null,item.label)
  );
  return React.createElement('div',{style:{width:230,flexShrink:0,height:'100vh',position:'sticky',top:0,display:'flex',flexDirection:'column',padding:'24px 14px 20px',background:'rgba(3,7,18,0.75)',backdropFilter:'blur(24px)',borderRight:'1px solid rgba(255,255,255,0.06)'}},
    // ── Logo ──────────────────────────────────────────────────────────────
    React.createElement('div',{style:{display:'flex',alignItems:'center',gap:12,padding:'4px 8px',marginBottom:36}},
      React.createElement('div',{style:{width:40,height:40,borderRadius:12,background:'linear-gradient(135deg,#2563EB,#7C3AED)',display:'flex',alignItems:'center',justifyContent:'center',boxShadow:'0 0 24px rgba(37,99,235,0.5)',flexShrink:0}},
        React.createElement('span',{style:{fontSize:15,fontWeight:800,color:'#fff',letterSpacing:'0.05em'}},'BG')
      ),
      React.createElement('div',null,
        React.createElement('div',{style:{fontSize:15,fontWeight:700,color:'#F1F5F9',letterSpacing:'0.02em'}},'BankGuard'),
        React.createElement('div',{style:{fontSize:9,color:'rgba(255,255,255,0.28)',letterSpacing:'0.12em',marginTop:1}},'NEURAL CREDIT v2.4')
      )
    ),
    // ── Main nav ──────────────────────────────────────────────────────────
    React.createElement('nav',{style:{flex:1}},
      React.createElement('div',{className:'sidebar-section-label'},'Main'),
      mainItems.map(item=>React.createElement(NavItem,{key:item.id,item})),
      React.createElement('div',{className:'sidebar-divider'}),
      React.createElement('div',{className:'sidebar-section-label'},'Explore'),
      extraItems.map(item=>React.createElement(NavItem,{key:item.id,item}))
    ),
    // ── Status card ───────────────────────────────────────────────────────
    React.createElement('div',{style:{borderRadius:14,background:'rgba(3,7,18,0.6)',border:'1px solid rgba(255,255,255,0.07)',padding:'14px 16px',boxShadow:'inset 0 1px 0 rgba(255,255,255,0.04)'}},
      statusRows.map((r,i)=>React.createElement('div',{key:i,style:{display:'flex',alignItems:'center',gap:8,marginBottom:i<statusRows.length-1?10:0}},
        React.createElement('div',{style:{position:'relative',flexShrink:0}},
          React.createElement('div',{style:{width:7,height:7,borderRadius:'50%',background:r.dot,boxShadow:`0 0 6px ${r.dot}`,className:r.pulse?'status-dot-pulse':undefined}}),
          r.pulse&&React.createElement('div',{style:{position:'absolute',inset:-2,borderRadius:'50%',border:`1px solid ${r.dot}`,animation:'pulseRing 2s ease-in-out infinite',opacity:0.5}})
        ),
        React.createElement('div',null,
          React.createElement('div',{style:{fontSize:10,fontWeight:600,color:r.dot==='#10B981'?'#34D399':r.dot==='#3B82F6'?'#60A5FA':r.dot==='#818CF8'?'#A5B4FC':'#E2E8F0',letterSpacing:'0.06em'}},r.label)
        )
      ))
    )
  );
};

// ─── TOPBAR ───────────────────────────────────────────────────────────────────
const TopBar=({isConnected})=>{
  const now=new Date();
  const dateStr=now.toLocaleDateString('en-IN',{weekday:'long',day:'2-digit',month:'long',year:'numeric'});
  const timeStr=now.toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit',hour12:true});
  return React.createElement('div',{style:{display:'flex',alignItems:'center',gap:16,padding:'16px 28px',borderBottom:'1px solid rgba(255,255,255,0.06)',background:'rgba(3,7,18,0.5)',backdropFilter:'blur(12px)'}},
    // Welcome
    React.createElement('div',{style:{flex:1}},
      React.createElement('h1',{style:{fontSize:18,fontWeight:700,color:'#E2E8F0',marginBottom:2}},
        'Welcome to ',React.createElement('span',{className:'gradient-text'},'BankGuard')
      ),
      React.createElement('div',{style:{fontSize:11,color:'rgba(255,255,255,0.35)'}},dateStr+' · '+timeStr)
    ),
    // Search (cosmetic)
    React.createElement('div',{style:{display:'flex',alignItems:'center',gap:8,background:'rgba(255,255,255,0.04)',border:'1px solid rgba(255,255,255,0.08)',borderRadius:10,padding:'8px 14px',width:220}},
      React.createElement(Icon,{name:'search',size:14,color:'rgba(255,255,255,0.25)'}),
      React.createElement('span',{style:{fontSize:12,color:'rgba(255,255,255,0.2)'}}, 'Search applications…')
    ),
    // Connection status
    React.createElement('div',{style:{display:'flex',alignItems:'center',gap:6,padding:'6px 14px',borderRadius:10,background:isConnected?'rgba(16,185,129,0.08)':'rgba(239,68,68,0.08)',border:`1px solid ${isConnected?'rgba(16,185,129,0.25)':'rgba(239,68,68,0.25)'}`}},
      React.createElement('div',{style:{width:7,height:7,borderRadius:'50%',background:isConnected?'#10B981':'#EF4444',boxShadow:`0 0 6px ${isConnected?'#10B981':'#EF4444'}`}}),
      React.createElement('span',{style:{fontSize:11,fontWeight:600,color:isConnected?'#34D399':'#FCA5A5',letterSpacing:'0.06em'}},isConnected?'ONLINE':'OFFLINE')
    ),
    React.createElement('button',{style:{width:36,height:36,borderRadius:10,background:'rgba(255,255,255,0.05)',border:'1px solid rgba(255,255,255,0.08)',display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer'}},
      React.createElement(Icon,{name:'bell',size:15,color:'rgba(255,255,255,0.4)'})
    )
  );
};

// ─── ROOT APP ────────────────────────────────────────────────────────────────
const App=()=>{
  const [nav,setNav]=useState('dashboard');
  const [screen,setScreen]=useState('form'); // form | pipeline | results
  const [loading,setLoading]=useState(false);
  const [pipelineStage,setPipelineStage]=useState(0);
  const [apiData,setApiData]=useState(null);
  const [formData,setFormData]=useState({});
  const [startTime,setStartTime]=useState(null);
  const [elapsed,setElapsed]=useState(0);
  const [isConnected,setIsConnected]=useState(null);

  // Connection check
  useEffect(()=>{
    fetch(BACKEND+'/health')
      .then(r=>{
        if(!r.ok) throw new Error('Response status: '+r.status);
        return r.json();
      })
      .then(data=>{
        setIsConnected(data.status==='online');
      })
      .catch(err=>{
        console.error('Connection check failed:', err);
        setIsConnected(false);
      });
  },[]);

  const handleSubmit=async(form)=>{
    setFormData(form);
    setLoading(true);
    setScreen('pipeline');
    setPipelineStage(0);
    const t0=Date.now();
    setStartTime(t0);
    // Animate agents
    const runAgents=async()=>{
      for(let i=0;i<5;i++){
        setPipelineStage(i);
        await new Promise(r=>setTimeout(r,600));
      }
    };
    runAgents();
    try{
      const payload={business_name:form.biz,owner_name:form.owner,loan_amount:+form.amount,monthly_revenue:+form.revenue,industry:form.industry||'General Trade',loan_purpose:form.purpose||'Working capital'};
      const res=await fetch(BACKEND+'/analyze-loan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      if(!res.ok)throw new Error('API error '+res.status);
      const data=await res.json();
      setPipelineStage(5);
      await new Promise(r=>setTimeout(r,600));
      setApiData(data);
      setElapsed(Date.now()-t0);
      setScreen('results');
    }catch(e){
      console.error(e);
      alert('Backend error: '+e.message);
      setScreen('form');
    }finally{
      setLoading(false);
    }
  };

  const handleReset=()=>{
    setScreen('form');setApiData(null);setPipelineStage(0);setElapsed(0);
  };

  // Nav handler — only switches between real screens
  const handleNav=id=>{
    setNav(id);
    if(id==='dashboard'||id==='applications'){
      setScreen('form');setApiData(null);setPipelineStage(0);setElapsed(0);
    } else if(id==='demo'){
      setScreen('form');setApiData(null);setPipelineStage(0);setElapsed(0);
      // signal LoanForm to open demo panel
      setNav('demo');
    } else if(id==='about'){
      setScreen('about');
    }
  };

  return React.createElement('div',{style:{display:'flex',minHeight:'100vh',background:'#070B1F'}},
    // Sidebar
    React.createElement(Sidebar,{active:nav,onNav:handleNav,screen,isConnected}),
    // Main content
    React.createElement('div',{style:{flex:1,display:'flex',flexDirection:'column',minHeight:'100vh',overflow:'auto'}},
      React.createElement(TopBar,{isConnected}),
      // Page content
      React.createElement('div',{style:{flex:1,padding:28}},
        // Form screen
        screen==='form'&&React.createElement('div',{style:{maxWidth:900,margin:'0 auto'}},
          // Hero card
          React.createElement('div',{className:'metric-card',style:{background:'linear-gradient(135deg,rgba(37,99,235,0.12),rgba(124,58,237,0.08))',border:'1px solid rgba(59,130,246,0.2)',marginBottom:24,padding:28}},
            React.createElement('div',{style:{display:'grid',gridTemplateColumns:'1fr auto',gap:24,alignItems:'center'}},
              React.createElement('div',null,
                React.createElement('div',{style:{fontSize:10,letterSpacing:'0.2em',color:'rgba(59,130,246,0.8)',marginBottom:8,textTransform:'uppercase',fontFamily:'JetBrains Mono, monospace'}},'// MULTI-AGENT AI PLATFORM'),
                React.createElement('h2',{style:{fontSize:28,fontWeight:800,lineHeight:1.2,marginBottom:10}},
                  React.createElement('span',{className:'gradient-text'},'SME Loan Intelligence'),
                  React.createElement('br'),React.createElement('span',{style:{color:'#E2E8F0'}},'Assessment System')
                ),
                React.createElement('div',{style:{fontSize:13,color:'rgba(255,255,255,0.4)',lineHeight:1.6,maxWidth:420}},'5-agent neural pipeline · 40+ risk signals · Real-time MongoDB fraud detection · Full audit trail')
              ),
              React.createElement('div',{style:{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,minWidth:240}},
                [['< 4s','Decision SLA'],['5','AI Agents'],['40+','Data Signals'],['100%','Audit Trail']].map(([v,l],i)=>
                  React.createElement('div',{key:i,style:{background:'rgba(255,255,255,0.04)',border:'1px solid rgba(255,255,255,0.07)',borderRadius:12,padding:'12px 14px',textAlign:'center'}},
                    React.createElement('div',{className:'gradient-text',style:{fontSize:20,fontWeight:700,marginBottom:2}},v),
                    React.createElement('div',{style:{fontSize:9,color:'rgba(255,255,255,0.3)',letterSpacing:'0.1em',textTransform:'uppercase'}},l)
                  )
                )
              )
            )
          ),
          // Form card
          React.createElement('div',{className:'metric-card',style:{padding:28}},
            React.createElement('div',{style:{fontSize:11,fontWeight:600,color:'rgba(255,255,255,0.4)',letterSpacing:'0.12em',marginBottom:20,textTransform:'uppercase',display:'flex',alignItems:'center',gap:8}},
              React.createElement(Icon,{name:'apps',size:13,color:'rgba(255,255,255,0.3)'}),'Application Input Module'
            ),
            React.createElement(LoanForm,{onSubmit:handleSubmit,loading})
          )
        ),
        // Pipeline screen
        screen==='pipeline'&&React.createElement('div',{style:{maxWidth:700,margin:'0 auto'}},
          React.createElement(PipelineView,{stage:pipelineStage,form:formData,startTime})
        ),
        // Results screen
        screen==='results'&&apiData&&React.createElement('div',{style:{maxWidth:1100,margin:'0 auto'}},
          React.createElement(ResultsDashboard,{data:apiData,form:formData,elapsed,onReset:handleReset})
        ),
        // About screen
        screen==='about'&&React.createElement('div',{style:{maxWidth:700,margin:'0 auto'},className:'fade-in'},
          React.createElement('div',{className:'metric-card',style:{padding:36,textAlign:'center'}},
            React.createElement('div',{style:{width:64,height:64,borderRadius:18,background:'linear-gradient(135deg,#2563EB,#7C3AED)',display:'flex',alignItems:'center',justifyContent:'center',margin:'0 auto 20px',boxShadow:'0 0 30px rgba(37,99,235,0.5)'}},
              React.createElement('span',{style:{fontSize:24,fontWeight:800,color:'#fff'}},'BG')
            ),
            React.createElement('h2',{style:{fontSize:26,fontWeight:800,marginBottom:8}},React.createElement('span',{className:'gradient-text'},'BankGuard')),
            React.createElement('div',{style:{fontSize:12,color:'rgba(255,255,255,0.4)',letterSpacing:'0.15em',marginBottom:24}},'NEURAL CREDIT SYSTEM v2.4'),
            React.createElement('div',{style:{fontSize:14,color:'rgba(255,255,255,0.5)',lineHeight:1.8,maxWidth:480,margin:'0 auto',marginBottom:28}},
              'BankGuard is a multi-agent AI platform for SME loan decisioning. It runs 5 specialized agents in sequence — intake, document verification, fraud intelligence, business validation, and risk scoring — to produce a fully auditable credit decision in under 4 seconds.'
            ),
            React.createElement('div',{style:{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:12,marginBottom:28}},
              [['5','AI Agents'],['40+','Risk Signals'],['< 4s','Decision Time'],['100%','Audit Trail']].map(([v,l],i)=>
                React.createElement('div',{key:i,style:{background:'rgba(255,255,255,0.04)',border:'1px solid rgba(255,255,255,0.07)',borderRadius:14,padding:'16px 12px',textAlign:'center'}},
                  React.createElement('div',{className:'gradient-text',style:{fontSize:22,fontWeight:700,marginBottom:4}},v),
                  React.createElement('div',{style:{fontSize:10,color:'rgba(255,255,255,0.3)',letterSpacing:'0.1em',textTransform:'uppercase'}},l)
                )
              )
            ),
            React.createElement('div',{style:{display:'flex',gap:10,justifyContent:'center',flexWrap:'wrap'}},
              [['MongoDB Atlas','#10B981'],['FastAPI Backend','#3B82F6'],['React 18 UI','#818CF8'],['MCP Tools','#F59E0B'],['5-Agent Pipeline','#EF4444']].map(([t,c],i)=>
                React.createElement('span',{key:i,style:{padding:'5px 14px',borderRadius:100,fontSize:11,fontWeight:600,background:`${c}18`,color:c,border:`1px solid ${c}33`}},t)
              )
            ),
            React.createElement('div',{style:{marginTop:28,fontSize:11,color:'rgba(255,255,255,0.2)',fontFamily:'JetBrains Mono, monospace'}},
              `API: http://127.0.0.1:8006 · Frontend: http://localhost:3000`
            )
          )
        )
      )
    )
  );
};

// Mount
const root=ReactDOM.createRoot(document.getElementById('app'));
root.render(React.createElement(App));
