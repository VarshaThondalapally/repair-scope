import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import packs from "../web/data.js";
import {Matcher,parseCatalog,check,canApprove,approve,csvText,safeCell} from "../web/engine.js";

test("browser and Python agree across 150 development queries",()=>{
  const fixtures=JSON.parse(fs.readFileSync(new URL("../reports/parity.json",import.meta.url)));
  const matchers={};
  for(const f of fixtures){
    const key=f.domain+f.strategy;
    matchers[key]??=new Matcher(packs[f.domain],f.strategy);
    const ranked=matchers[key].rank(f.finding);
    assert.deepEqual(ranked.map(c=>c.row.code),f.codes,f.finding+" / "+f.strategy);
    ranked.forEach((c,i)=>assert.ok(Math.abs(c.score-f.scores[i])<1e-9,"score parity"));
  }
});
test("phrase aliases cannot match unrelated isolated words",()=>{
  const pack={catalog:[{code:"A",section:"Equipment",description:"Set air mover",hours:1},{code:"B",section:"Equipment",description:"Replace air filter",hours:1}],synonyms:[["blower","air mover"]]};
  assert.deepEqual(new Matcher(pack).rank("blower").map(c=>c.row.code),["A"]);
});
test("typo repair is visible and one source is not a clear result",()=>{
  const pack={catalog:[{code:"A",section:"Equipment",description:"Replace furnace igniter",hours:1}],synonyms:[]};
  const result=new Matcher(pack).match("furnase");
  assert.equal(result.candidates[0].row.code,"A");
  assert.ok(result.candidates[0].matched[0].via_typo);
  assert.equal(result.clear,false);
});
test("CSV handles BOM, multiline fields, comments and quoted commas",()=>{
  const rows=parseCatalog('\uFEFF# sample\ncode,section,description,hours\nA,S,"One,\n two",1.5\n');
  assert.equal(rows[0].description,"One,\n two");
  assert.equal(rows[0].hours,1.5);
});
for(const [name,csv]of Object.entries({
  duplicate:"code,section,description,hours\nA,S,D,1\nA,S,X,1",
  badHours:"code,section,description,hours\nA,S,D,NaN",
  emptyHours:"code,section,description,hours\nA,S,D,",
  negative:"code,section,description,hours\nA,S,D,-1",
  malformed:'code,section,description,hours\nA,S,"unclosed,1',
  duplicateHeader:"code,section,description,hours,hours\nA,S,D,1,2"
}))test("reject "+name,()=>assert.throws(()=>parseCatalog(csv)));
test("unknown codes and incomplete sets cannot be approved silently",()=>{
  const pack=packs.rv_service;
  assert.deepEqual(check(pack,["UNKNOWN"]).unknown,["UNKNOWN"]);
  const item={id:"F-1",finding:"Replace confirmed failed LP regulator",codes:["RVS-0202"]};
  assert.ok(check(pack,item.codes).missing.length);
  assert.equal(canApprove(pack,item,"Varsha",true),false);
  assert.equal(canApprove(pack,item,"",true,"Reviewed example rule; not applicable"),false);
  assert.equal(canApprove(pack,item,"Varsha",false,"Reviewed example rule; not applicable"),false);
  const approval=approve(pack,item,"Varsha",true,"Reviewed example rule; not applicable","2026-11-12T20:00:00Z");
  assert.equal(approval.reviewer,"Varsha");
  assert.equal(approval.catalog_id,pack.catalog_id);
  assert.ok(approval.missing_rules.length);
  item.codes.push("RVS-0201");
  assert.equal(canApprove(pack,item,"Varsha",true),true);
  assert.deepEqual(approval.codes,["RVS-0202"],"approval is a snapshot");
});
test("custom catalogs without rules do not claim completeness",()=>{
  assert.equal(check({catalog:[{code:"A",section:"S",description:"D",hours:0}],rules:[],has_rules_file:false},["A"]).has_rules_file,false);
});
test("negative statements trigger a review question",()=>{
  assert.ok(new Matcher(packs.rv_service).match("water beneath sink, source not confirmed").questions.some(q=>q.includes("negative")));
});
test("spreadsheet fields are formula-safe",()=>{
  for(const value of ["=1+1","+cmd","-cmd","@SUM(A1)","  =1","\tX","\rX"])assert.ok(safeCell(value).startsWith("'"));
  assert.equal(safeCell("RVS-0201"),"RVS-0201");
  assert.ok(csvText([['a"b',"=1"]]).includes('"a""b","\'=1"'));
});
