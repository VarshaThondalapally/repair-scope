import packs from "./data.js";
import {Matcher,check,parseCatalog,stem,approve,canApprove,csvText} from "./engine.js";
import {revokeApproval,hasDraftWork,changeJobReference,approvalIsCurrent,reviewRecord} from "./draft.js";

const $=id=>document.getElementById(id);
const state={pack:packs.rv_service,matcher:null,items:[],active:0,nextId:1,reviewer:"",jobReference:"",pendingPack:null,uploadGeneration:0};
function node(tag,attrs={},...children){
  const n=document.createElement(tag);
  for(const [k,v]of Object.entries(attrs)){
    if(k==="class")n.className=v;
    else if(k.startsWith("on"))n.addEventListener(k.slice(2),v);
    else n.setAttribute(k,v);
  }
  for(const child of children)if(child!==null&&child!==undefined)n.append(child);
  return n;
}
const current=()=>state.items[state.active];
function message(text,tone="error"){
  $("messages").replaceChildren(text?node("div",{class:tone+"-message"},text):"");
}
function invalidate(item,scopeChanged=false){
  revokeApproval(item,scopeChanged);
  if(scopeChanged)$("overrideReason").value="";
  $("confirmed").checked=false;
}
function newFinding(){
  if(state.items.length>=50){message("This demo supports 50 findings per draft. Export your reviewed work before starting a new session.");return;}
  state.items.push({id:"F-"+String(state.nextId++).padStart(3,"0"),finding:"",codes:[],result:null,approval:null,override:""});
  state.active=state.items.length-1;showCurrent();
}
function renderList(){
  $("findingList").replaceChildren(...state.items.map((item,i)=>{
    const button=node("button",{class:"finding-tab"+(i===state.active?" active":""),onclick:()=>{state.active=i;showCurrent();},"aria-label":"Open "+item.id});
    button.append(node("span",{class:"finding-number"},item.id.slice(2)),node("span",{},node("span",{class:"finding-name"},item.finding?item.finding.slice(0,60):"New finding"),node("span",{class:"finding-status"},item.approval?"✓ Approved":item.codes.length?"Awaiting approval":"Draft")));
    return button;
  }));
  const approved=state.items.filter(i=>approvalIsCurrent(state.pack,i,state.jobReference));
  $("approvedCount").textContent=approved.length+" of "+state.items.length+" findings approved";
  $("exportCsv").disabled=$("exportAudit").disabled=!approved.length;
  $("itemStatus").textContent=current().approval?"Approved":"Draft";
  $("itemStatus").className="badge"+(current().approval?" approved":"");
}
function showCurrent(){
  const item=current();
  $("finding").value=item.finding;
  $("overrideReason").value=item.override;
  $("confirmed").checked=!!item.approval;
  if(item.approval)$("reviewer").value=item.approval.reviewer;
  renderCandidates();renderReview();renderList();message("");
}
function setPack(pack){
  state.pack=pack;state.matcher=new Matcher(pack,$("strategy").value);
  const info=pack.catalog.length+" codes · "+(pack.has_rules_file?pack.rules.length+" example rules":"no companion rules")+
    "\nCatalog "+pack.catalog_id+" · "+pack.version;
  $("catalogInfo").textContent=info;
  $("manualSearch").value="";$("manualResults").replaceChildren();
  state.items=[];state.active=0;state.nextId=1;newFinding();
  $("scenarioHint").hidden=true;
  syncCatalogSelect();
}
function syncCatalogSelect(){
  const bundled=!!packs[state.pack.name];
  $("uploadedOption").hidden=bundled;
  if(!bundled)$("uploadedOption").textContent="Uploaded: "+state.pack.name;
  $("domain").value=bundled?state.pack.name:"uploaded";
}
function requestPack(pack){
  syncCatalogSelect();
  if(!hasDraftWork(state.items)){setPack(pack);return;}
  state.pendingPack=pack;
  if(!$("catalogDialog").open)$("catalogDialog").showModal();
}
function highlighted(text,terms){
  const result=node("span");
  for(const p of text.split(/([A-Za-z0-9]+)/))result.append(terms.has(stem(p.toLowerCase()))?node("mark",{},p):p);
  return result;
}
function renderCandidates(){
  const item=current(), table=$("candidates");
  $("questions").replaceChildren();$("verdict").textContent="";$("timing").textContent="";
  if(!item.result){
    table.replaceChildren(node("div",{class:"empty"},node("span",{class:"empty-icon"},"⌕"),node("h2",{},"Your findings, grounded in a catalog."),node("p",{},"Choose a sample case or enter a finding to see suggested lines and the words behind them.")));return;
  }
  $("timing").textContent=item.elapsed.toFixed(1)+" ms · "+item.result.candidates.length+" suggestions";
  for(const q of item.result.questions)$("questions").append(node("div",{class:"question"},node("strong",{},"Review question"),q));
  $("verdict").textContent=item.result.reason+" Nothing is selected automatically.";
  table.replaceChildren(...item.result.candidates.map((c,index)=>{
    const selected=item.codes.includes(c.row.code);
    const box=node("input",{type:"checkbox","aria-label":"Select "+c.row.code,onchange:e=>toggle(c.row.code,e.target.checked)});
    box.checked=selected;
    const terms=new Set(c.matched.flatMap(t=>t.term.split(" ")));
    const evidence=node("div",{class:"evidence"});
    for(const t of c.matched){
      const label=t.via_typo?t.source+" → "+t.word:t.via_synonym?t.source+" → "+t.word:t.word;
      evidence.append(node("span",{class:t.via_typo?"typo":t.via_synonym?"alias":""},label));
    }
    return node("div",{class:"candidate"+(selected?" chosen":"")},box,node("div",{class:"candidate-body"},
      node("div",{class:"candidate-head"},node("span",{class:"code"},"#"+(index+1)+"  "+c.row.code),node("span",{class:"candidate-score"},"relevance "+c.score.toFixed(2))),
      node("h3",{},highlighted(c.row.description,terms)),node("div",{class:"candidate-section"},c.row.section+" · "+c.row.hours+" sample hours"),evidence));
  }));
  if(!item.result.candidates.length)table.append(node("div",{class:"empty"},node("h2",{},"No supported suggestion"),node("p",{},"Try a component name, add evidence, or search the catalog manually. The system will not invent a code.")));
}
function toggle(code,on){
  if(!state.pack.catalog.some(r=>r.code===code)){message("Blocked: this exact code is not in the selected catalog.");return;}
  const item=current();
  item.codes=item.codes.filter(c=>c!==code);if(on)item.codes.push(code);
  invalidate(item,true);renderCandidates();renderReview();renderList();message("");
}
function runMatch(){
  const item=current(),finding=$("finding").value.trim();
  if(!finding){message("Describe a finding before matching.");return;}
  item.finding=finding;item.codes=[];invalidate(item,true);
  const start=performance.now();item.result=state.matcher.match(finding);item.elapsed=performance.now()-start;
  renderCandidates();renderReview();renderList();message("");
}
function renderReview(){
  const item=current(),report=check(state.pack,item.codes);
  $("selectedCount").textContent=report.selected.length+" lines selected";
  $("selected").replaceChildren(...report.selected.map(row=>node("div",{class:"selected-line"},
    node("div",{},node("span",{class:"code"},row.code),row.description),
    node("button",{"aria-label":"Remove "+row.code,onclick:()=>toggle(row.code,false)},"Remove ×"))));
  const box=$("completeness");box.replaceChildren();
  if(!report.selected.length)box.append(node("p",{class:"small muted"},"No lines selected. Choose a supported suggestion or search the catalog."));
  else if(!state.pack.has_rules_file)box.append(node("p",{class:"small muted"},"Companion work is not checked: no rules are loaded for your custom catalog."));
  else if(!report.missing.length)box.append(node("div",{class:"complete-note"},"✓ No unmet example rules. Confirm actual requirements with the catalog owner."));
  else for(const gap of report.missing){
    const card=node("div",{class:"gap"},node("strong",{},"Companion check: "+gap.rule.name),node("p",{},gap.rule.reason),node("span",{class:"small muted"},"Example rule · triggered by "+gap.triggered_by.join(", ")));
    for(const row of gap.satisfied_by)card.append(node("button",{class:"secondary",onclick:()=>toggle(row.code,true)},"Select "+row.code+" · "+row.description));
    box.append(card);
  }
  $("overrideArea").hidden=!report.missing.length;
  updateApproval();
}
function updateApproval(){
  const item=current();
  $("approveBtn").disabled=!!item.approval||!canApprove(state.pack,item,$("reviewer").value,$("confirmed").checked,$("overrideReason").value);
  $("approvalNote").textContent=item.approval?
    "Approved by "+item.approval.reviewer+" · "+new Date(item.approval.approved_at).toLocaleString():
    item.codes.length?"Review the scope and companion work, then confirm approval.":"Select lines to prepare a reviewed draft.";
}
function approveCurrent(){
  const item=current();
  try{
    item.override=$("overrideReason").value;
    item.approval=approve(state.pack,item,$("reviewer").value,$("confirmed").checked,item.override,undefined,state.jobReference);
    updateApproval();renderList();message(item.id+" approved. It is now included in your downloadable draft.","success");
  }catch(e){message(e.message);}
}
function download(name,text,type){
  const url=URL.createObjectURL(new Blob([text],{type}));
  const a=node("a",{href:url,download:name});a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function record(){
  return reviewRecord(state.pack,state.items,state.jobReference);
}
function exportCsv(){
  const data=record(),rows=[["job_reference","finding_id","finding","code","section","description","hours","reviewer","approved_at","catalog_id","catalog_version","override_reason"]];
  for(const a of data.approvals)for(const row of a.rows)rows.push([data.job_reference,a.finding_id,a.finding,row.code,row.section,row.description,row.hours,a.reviewer,a.approved_at,a.catalog_id,a.catalog_version,a.override_reason]);
  download("repair-scope-reviewed-draft.csv",csvText(rows),"text/csv;charset=utf-8");
}
function manualSearch(){
  const q=$("manualSearch").value.trim().toLowerCase();
  const rows=q?state.pack.catalog.filter(r=>(r.code+" "+r.description+" "+r.section).toLowerCase().includes(q)).slice(0,12):[];
  $("manualResults").replaceChildren(...rows.map(row=>node("div",{class:"manual-row"},node("span",{},node("span",{class:"code"},row.code+" "),row.description),
    node("button",{class:"text-button",onclick:()=>toggle(row.code,true)},"Select"))));
  if(q&&!rows.length)$("manualResults").append(node("p",{},"No catalog code matches. Unknown codes cannot be selected."));
}
const examples={
  rv_service:{clear:"Roof vent lid cracked; replacement required.",unclear:"Water collecting beneath the kitchen sink. Source not confirmed.",companion:"Replace confirmed failed LP regulator",typo:"Replace failed furnase ignitor after diagnosis."},
  property_restoration:{clear:"Remove wet drywall from the bedroom wall.",unclear:"Room has an unusual smell. Source not confirmed.",companion:"Remove wet drywall from the bedroom wall.",typo:"Set up dehumidifer for drying."}
};
const scenarioHints={
  clear:"Inspect the catalog evidence, select a supported line, then review and approve the draft.",
  unclear:"Notice that no line is selected. Gather evidence about the cause before deciding what repair is justified.",
  companion:"Select the proposed repair and inspect the companion-rule warning below. The rule is an invented example; a reviewer decides whether it applies.",
  typo:"The evidence shows possible spelling corrections. They are suggestions to verify, not established facts."
};
$("matchBtn").addEventListener("click",()=>{runMatch();current().retrieval=$("strategy").value;});
$("finding").addEventListener("keydown",e=>{if(e.key==="Enter"&&(e.ctrlKey||e.metaKey)){e.preventDefault();runMatch();current().retrieval=$("strategy").value;}});
$("finding").addEventListener("input",()=>{
  const item=current();item.finding=$("finding").value;item.codes=[];item.result=null;invalidate(item,true);
  renderCandidates();renderReview();renderList();
});
$("newFinding").addEventListener("click",newFinding);
$("reviewer").addEventListener("input",()=>{invalidate(current());updateApproval();renderList();});
$("confirmed").addEventListener("change",()=>{if(!$("confirmed").checked)current().approval=null;updateApproval();renderList();});
$("overrideReason").addEventListener("input",()=>{current().override=$("overrideReason").value;invalidate(current());updateApproval();renderList();});
$("approveBtn").addEventListener("click",approveCurrent);
$("manualSearch").addEventListener("input",manualSearch);
$("strategy").addEventListener("change",()=>{
  state.matcher=new Matcher(state.pack,$("strategy").value);
  if(current().finding.trim()){runMatch();current().retrieval=$("strategy").value;}
});
$("job").addEventListener("input",()=>{
  const count=changeJobReference(state,$("job").value);
  $("confirmed").checked=false;$("overrideReason").value="";
  renderReview();renderList();
  if(count)message("The job reference changed. Review and approve the findings again.","success");
});
$("domain").addEventListener("change",()=>{
  state.uploadGeneration++;
  const pack=packs[$("domain").value];
  $("upload").value="";
  if(pack)requestPack(pack);
});
$("cancelCatalog").addEventListener("click",()=>{state.pendingPack=null;$("catalogDialog").close();syncCatalogSelect();$("upload").value="";});
$("catalogDialog").addEventListener("cancel",()=>{state.pendingPack=null;syncCatalogSelect();$("upload").value="";});
$("confirmCatalog").addEventListener("click",()=>{
  const pack=state.pendingPack;state.pendingPack=null;$("catalogDialog").close();
  if(pack)setPack(pack);
});
$("upload").addEventListener("change",async e=>{
  const file=e.target.files[0];if(!file)return;
  const generation=++state.uploadGeneration;
  try{
    if(file.size>1_000_000)throw Error("Catalog exceeds 1 MB.");
    const catalog=parseCatalog(await file.text());
    if(generation!==state.uploadGeneration)return;
    const digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(JSON.stringify(catalog)));
    const id=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,"0")).join("").slice(0,16);
    if(generation!==state.uploadGeneration)return;
    requestPack({name:file.name,version:"uploaded-snapshot",catalog,catalog_id:id,sample_data:false,has_rules_file:false,rules:[],synonyms:[]});
    if(!state.pendingPack)message("Loaded "+file.name+". Your catalog has no companion rules; completeness is not checked.","success");
  }catch(error){if(generation!==state.uploadGeneration)return;message("Catalog not loaded: "+error.message+" Your previous catalog is unchanged.");$("upload").value="";}
});
document.querySelectorAll("[data-example]").forEach(button=>button.addEventListener("click",()=>{
  const group=examples[state.pack.name];
  if(!group){message("Sample findings are available with bundled sample catalogs.");return;}
  $("finding").value=group[button.dataset.example];runMatch();current().retrieval=$("strategy").value;
  $("scenarioHint").textContent=scenarioHints[button.dataset.example];$("scenarioHint").hidden=false;
}));
$("exportCsv").addEventListener("click",exportCsv);
$("exportAudit").addEventListener("click",()=>download("repair-scope-review-record.json",JSON.stringify(record(),null,2),"application/json"));
window.addEventListener("beforeunload",event=>{if(hasDraftWork(state.items)){event.preventDefault();event.returnValue="";}});
setPack(packs.rv_service);
