import test from "node:test";
import assert from "node:assert/strict";
import packs from "../web/data.js";
import {approve} from "../web/engine.js";
import {revokeApproval,hasDraftWork,changeJobReference,approvalIsCurrent,reviewRecord} from "../web/draft.js";

function reviewed(){
  const pack=packs.rv_service;
  const item={id:"F-1",finding:"Replace cracked roof vent lid",codes:["RVS-0904"],override:"",retrieval:"hybrid"};
  item.approval=approve(pack,item,"Demo reviewer",true,"","2026-11-13T17:00:00Z","Unit 42");
  return {pack,item};
}
test("only the exact reviewed finding and unit can be exported",()=>{
  const {pack,item}=reviewed();
  assert.equal(approvalIsCurrent(pack,item,"Unit 42"),true);
  assert.equal(approvalIsCurrent(pack,item,"Unit 43"),false);
  item.finding+=" and another issue";
  assert.equal(reviewRecord(pack,[item],"Unit 42").approvals.length,0);
});
test("a selection change blocks a stale approval even if a UI event is missed",()=>{
  const {pack,item}=reviewed();item.codes.push("RVS-0703");
  assert.equal(approvalIsCurrent(pack,item,"Unit 42"),false);
  assert.deepEqual(reviewRecord(pack,[item],"Unit 42").unapproved_findings,["F-1"]);
});
test("a new catalog snapshot cannot reuse an old approval",()=>{
  const {pack,item}=reviewed();
  assert.equal(approvalIsCurrent({...pack,catalog_id:"new"},item,"Unit 42"),false);
});
test("scope changes clear approval and an old rule override",()=>{
  const {item}=reviewed();item.override="An old rule explanation";
  revokeApproval(item,true);
  assert.equal(item.approval,null);assert.equal(item.override,"");
});
test("changing reviewer clears approval while preserving current scope explanation",()=>{
  const {item}=reviewed();item.override="Current explanation";
  revokeApproval(item);
  assert.equal(item.override,"Current explanation");assert.equal(item.approval,null);
});
test("a changed job reference invalidates every finding, unchanged reference preserves them",()=>{
  const {item}=reviewed();
  const state={items:[item],jobReference:"Unit 42"};
  assert.equal(changeJobReference(state,"Unit 42"),0);assert.ok(item.approval);
  assert.equal(changeJobReference(state,"Unit 43"),1);assert.equal(item.approval,null);
});
test("review record includes approved snapshots and separates unapproved findings",()=>{
  const {pack,item}=reviewed();
  const record=reviewRecord(pack,[item,{id:"F-2",finding:"Unknown symptom",codes:[],override:""}],"Unit 42");
  assert.equal(record.approvals.length,1);
  assert.equal(record.approvals[0].reviewer,"Demo reviewer");
  assert.equal(record.approvals[0].catalog_id,pack.catalog_id);
  assert.equal(record.approvals[0].job_reference,"Unit 42");
  assert.deepEqual(record.unapproved_findings,["F-2"]);
});
test("snapshot rows are copied at approval time",()=>{
  const {pack,item}=reviewed(),source=pack.catalog.find(r=>r.code==="RVS-0904");
  assert.notEqual(item.approval.rows[0],source);
});
test("catalog replacement guard recognizes all meaningful work",()=>{
  assert.equal(hasDraftWork([{finding:"",codes:[],approval:null}]),false);
  assert.equal(hasDraftWork([{finding:"A note",codes:[],approval:null}]),true);
});
