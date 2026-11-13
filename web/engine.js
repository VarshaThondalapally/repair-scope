// Mirrors finding_coder.matcher. No model, network calls, or automatic approval.
export const STOP = new Set(("a an and are as at be been but by for from had has have in is it its of on or " +
  "that the then there this to was were when with").split(" "));
const LOW = new Set("up out off down front rear left right near under over back around need needs".split(" "));
export function stem(w) {
  if (w.length > 4 && w.endsWith("ies")) w = w.slice(0,-3)+"y";
  else if (w.length > 4 && /(ches|shes|sses|xes|zes)$/.test(w)) w=w.slice(0,-2);
  else if (w.length > 3 && w.endsWith("s") && !/(ss|us|is)$/.test(w)) w=w.slice(0,-1);
  for (const s of ["ing","ed"]) {
    if (w.endsWith(s) && w.length-s.length>=3) {
      w=w.slice(0,-s.length);
      if (w.length>3 && w.at(-1)===w.at(-2) && !"ls".includes(w.at(-1))) w=w.slice(0,-1);
      break;
    }
  }
  if (w.length>4 && w.endsWith("e")) w=w.slice(0,-1);
  return w;
}
export function words(s) {
  return (s.toLowerCase().replace(/[’']/g,"").replace(/\b([a-z])\/([a-z])\b/g,"$1$2").match(/[a-z0-9]+/g)||[])
    .filter(w=>!STOP.has(w));
}
export const tokenize = s=>words(s).map(stem);
export function contains(tokens, phrase) {
  return phrase.length>0 && tokens.some((_,i)=>phrase.every((t,j)=>tokens[i+j]===t));
}
// Ratcliff/Obershelp matching-block ratio, matching SequenceMatcher for short words.
function ratio(a,b) {
  function blocks(al,ah,bl,bh) {
    let ai=al, bi=bl, size=0, prev=new Map();
    for (let i=al;i<ah;i++) {
      const next=new Map();
      for (let j=bl;j<bh;j++) if (a[i]===b[j]) {
        const n=(prev.get(j-1)||0)+1; next.set(j,n);
        if (n>size) {size=n;ai=i-n+1;bi=j-n+1;}
      }
      prev=next;
    }
    return size ? size+blocks(al,ai,bl,bi)+blocks(ai+size,ah,bi+size,bh):0;
  }
  return a.length+b.length ? 2*blocks(0,a.length,0,b.length)/(a.length+b.length):1;
}
export class Matcher {
  constructor(pack, strategy="hybrid") {
    this.pack=pack; this.strategy=strategy;
    this.tokens=pack.catalog.map(r=>tokenize(r.description+" "+r.section));
    this.docs=this.tokens.map(t=>{const d={};for(const w of t)d[w]=(d[w]||0)+1;return d;});
    this.lengths=this.tokens.map(t=>t.length);
    this.avg=this.lengths.reduce((a,b)=>a+b,0)/this.lengths.length || 1;
    const df={};
    this.docs.forEach(d=>Object.keys(d).forEach(w=>df[w]=(df[w]||0)+1));
    this.idf=Object.fromEntries(Object.entries(df).map(([t,n])=>[t,Math.log(1+(this.docs.length-n+.5)/(n+.5))]));
    this.groups=(pack.synonyms||[]).map(g=>g.map(phrase=>({phrase,tokens:tokenize(phrase)})));
  }
  rank(finding) {
    const surface=words(finding), tokens=surface.map(stem), query=new Map();
    surface.forEach((w,i)=>query.set(tokens[i],{term:tokens[i],word:w,source:w,via_synonym:false,via_typo:false}));
    const aliases=[];
    this.groups.forEach((g,group)=>{
      const present=g.filter(p=>contains(tokens,p.tokens));
      if (present.length) g.filter(p=>!contains(tokens,p.tokens)).forEach(p=>aliases.push({...p,group,source:present[0].phrase}));
    });
    const typos=new Map();
    if (this.strategy==="hybrid") surface.forEach((w,i)=>{
      const t=tokens[i];
      if(t.length>=5 && !(t in this.idf)){
        const near=Object.keys(this.idf).filter(v=>Math.abs(t.length-v.length)<=2)
          .map(v=>[ratio(t,v),v]).sort((a,b)=>b[0]-a[0]||a[1].localeCompare(b[1]));
        if(near.length && near[0][0]>=.8 && (near.length===1 || near[0][0]-near[1][0]>=.05))
          typos.set(near[0][1],{term:near[0][1],word:near[0][1],source:w,via_synonym:false,via_typo:true});
      }
    });
    const ranked=[];
    this.pack.catalog.forEach((row,i)=>{
      const doc=this.docs[i], dt=this.tokens[i], length=this.lengths[i];
      const weight=t=>doc[t] ? this.idf[t]*doc[t]*2.5/(doc[t]+1.5*(.25+.75*length/this.avg)):0;
      let score=0, matched=[];
      for(const [t,term] of query) if(doc[t]){
        score+=weight(t)*(LOW.has(t)?.1:1);matched.push(term);
      }
      const best=new Map();
      for(const alias of aliases) if(contains(dt,alias.tokens)){
        const value=.6*alias.tokens.reduce((s,t)=>s+weight(t),0);
        if(!best.has(alias.group)||value>best.get(alias.group).value)
          best.set(alias.group,{value,term:{term:alias.tokens.join(" "),word:alias.phrase,source:alias.source,via_synonym:true,via_typo:false}});
      }
      for(const {value,term} of best.values()){score+=value;matched.push(term);}
      for(const [t,term] of typos) if(doc[t]&&!query.has(t)){score+=.45*weight(t);matched.push(term);}
      if(this.strategy==="hybrid") for(let j=0;j<tokens.length-1;j++)
        if(contains(dt,[tokens[j],tokens[j+1]])) score+=.15*((this.idf[tokens[j]]||0)+(this.idf[tokens[j+1]]||0));
      if(matched.some(t=>!LOW.has(t.term)))ranked.push({row,score,matched});
    });
    return ranked.sort((a,b)=>b.score-a.score||(a.row.code<b.row.code?-1:a.row.code>b.row.code?1:0));
  }
  match(finding, k=8) {
    const ranked=this.rank(finding), top=ranked[0], rival=ranked[1];
    const sources=new Set((top?.matched||[]).filter(t=>!t.via_typo).map(t=>tokenize(t.source).join(" ")));
    const clear=!!top && sources.size>=2 && (!rival || top.score>=1.2*rival.score);
    return {candidates:ranked.slice(0,k),clear,questions:guidance(finding,ranked),
      reason:!top?"No matching catalog evidence.":clear?"Clearer textual match. Review still required.":"Several interpretations remain. Review the evidence."};
  }
}
export function guidance(finding,candidates) {
  if(!candidates.length)return ["No supported candidate. Search the catalog manually or gather more evidence."];
  const text=finding.toLowerCase(), top=candidates[0].row.description.toLowerCase(), result=[];
  const confirmed=/\b(confirm\w*|replac\w*|broken|cracked|failed|stripped|torn|seized)\b/.test(text)&&!/\b(not confirmed|unconfirmed|not diagnosed)\b/.test(text);
  if(/\b(replace|remove|repair)\b/.test(top)&&!confirmed)
    result.push("Has the failed component and repair scope been confirmed? A symptom alone does not establish a repair.");
  if(/\b(no|not|without|never|isnt|isn't|doesnt|doesn't)\b/.test(text))
    result.push("Check negative statements against the proposed action. Text matching does not establish what has been ruled out.");
  if(candidates[0].matched.some(t=>t.via_typo))result.push("Confirm the suggested spelling before selecting this line.");
  if(/\b(and|also|plus)\b/.test(text))result.push("Does this note describe more than one issue? Add a separate finding for each distinct problem.");
  return result;
}
export function conditionMatches(row,c) {
  if(c.codes.length&&!c.codes.includes(row.code))return false;
  if(c.sections.length&&!c.sections.includes(row.section.toLowerCase()))return false;
  const tokens=tokenize(row.description);
  if(c.description_any.length&&!c.description_any.some(p=>contains(tokens,p)))return false;
  return !c.description_none.some(p=>contains(tokens,p));
}
export function check(pack,codes) {
  const lookup=new Map(pack.catalog.map(r=>[r.code,r]));
  const unknown=codes.filter(c=>!lookup.has(c));
  const selected=[...new Set(codes)].filter(c=>lookup.has(c)).map(c=>lookup.get(c));
  const missing=[];
  for(const rule of pack.rules||[]){
    const triggers=selected.filter(r=>conditionMatches(r,rule.when));
    if(triggers.length&&!selected.some(r=>conditionMatches(r,rule.require)))
      missing.push({rule,triggered_by:triggers.map(r=>r.code),satisfied_by:pack.catalog.filter(r=>conditionMatches(r,rule.require))});
  }
  return {selected,unknown,missing,has_rules_file:pack.has_rules_file};
}
export function safeCell(value) {
  const s=String(value??"");
  return /^[\t\r\n]/.test(s)||/^[\s]*[=+\-@]/.test(s)?"'"+s:s;
}
export function csvText(rows) {
  return rows.map(row=>row.map(v=>'"'+safeCell(v).replace(/"/g,'""')+'"').join(",")).join("\r\n")+"\r\n";
}
export function parseCatalog(text) {
  if(text.length>1_000_000)throw Error("Catalog exceeds 1 MB.");
  text=text.replace(/^\uFEFF/,"");
  let rows=[],row=[],field="",quoted=false,closed=false,line=1,start=1;
  const push=()=>{
    row.push(field);field="";closed=false;
    if(row.some(x=>x.trim())&&!row[0].trimStart().startsWith("#"))rows.push({values:row,line:start});
    row=[];start=line+1;
  };
  for(let i=0;i<text.length;i++){
    const ch=text[i];
    if(quoted){
      if(ch==='"'&&text[i+1]==='"'){field+='"';i++;}
      else if(ch==='"'){quoted=false;closed=true;}
      else {field+=ch;if(ch==="\n")line++;}
    }else if(ch==='"'){
      if(field)throw Error("Unexpected quote at line "+line+".");
      quoted=true;
    }else if(ch===","){row.push(field);field="";closed=false;}
    else if(ch==="\n"){push();line++;}
    else if(ch==="\r"&&text[i+1]==="\n"){}
    else if(ch==="\r"){push();line++;}
    else if(closed&&!/\s/.test(ch))throw Error("Unexpected text after quote at line "+line+".");
    else field+=ch;
  }
  if(quoted)throw Error("Unclosed quoted field.");
  if(field||row.length)push();
  if(!rows.length)throw Error("Catalog is empty.");
  const header=rows.shift().values.map(h=>h.trim().toLowerCase());
  for(const required of ["code","section","description","hours"])if(!header.includes(required))throw Error("Missing column: "+required);
  if(new Set(header).size!==header.length)throw Error("Duplicate column names.");
  if(!rows.length||rows.length>1000)throw Error("Use 1 to 1,000 catalog rows.");
  const seen=new Set();
  return rows.map(({values,line})=>{
    if(values.length!==header.length)throw Error("Wrong column count at line "+line+".");
    const r=Object.fromEntries(header.map((h,i)=>[h,values[i].trim()]));
    for(const key of ["code","section","description","hours"])if(!r[key])throw Error("Empty "+key+" at line "+line+".");
    if(seen.has(r.code))throw Error("Duplicate code "+r.code+" at line "+line+".");
    seen.add(r.code);
    if(!/^\+?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i.test(r.hours)||!Number.isFinite(Number(r.hours)))throw Error("Invalid hours at line "+line+".");
    return {code:r.code,section:r.section,description:r.description,hours:Number(r.hours)};
  });
}
export function canApprove(pack,item,reviewer,confirmed,overrideReason=""){
  const report=check(pack,item.codes);
  if(!item.finding.trim()||!report.selected.length||report.unknown.length)return false;
  if(!reviewer.trim()||!confirmed)return false;
  return !report.missing.length||overrideReason.trim().length>=10;
}
export function approve(pack,item,reviewer,confirmed,overrideReason="",now=new Date().toISOString(),jobReference="") {
  if(!canApprove(pack,item,reviewer,confirmed,overrideReason))throw Error("Review the finding, selected codes, and completeness warnings before approval.");
  return {finding_id:item.id,finding:item.finding,codes:[...item.codes],rows:check(pack,item.codes).selected.map(row=>({...row})),
    reviewer:reviewer.trim(),approved_at:now,catalog_id:pack.catalog_id,catalog_version:pack.version,
    job_reference:jobReference,override_reason:overrideReason.trim(),missing_rules:check(pack,item.codes).missing.map(g=>g.rule.name)};
}
