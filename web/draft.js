// Scope changes revoke decisions; exported records must match the reviewed scope.
export function revokeApproval(item,scopeChanged=false){
  item.approval=null;
  if(scopeChanged)item.override="";
}
export function hasDraftWork(items){
  return items.some(i=>i.finding.trim()||i.codes.length||i.approval);
}
export function changeJobReference(state,reference){
  if(state.jobReference===reference)return 0;
  const count=state.items.filter(i=>i.approval).length;
  state.jobReference=reference;
  state.items.forEach(i=>revokeApproval(i,true));
  return count;
}
export function approvalIsCurrent(pack,item,jobReference){
  const a=item.approval;
  return !!a && a.finding===item.finding && a.catalog_id===pack.catalog_id
    && a.job_reference===jobReference
    && JSON.stringify([...a.codes].sort())===JSON.stringify([...item.codes].sort())
    && a.override_reason===item.override.trim();
}
export function reviewRecord(pack,items,jobReference,now=new Date().toISOString()){
  const approved=items.filter(i=>approvalIsCurrent(pack,i,jobReference));
  return {schema_version:"2.1",created_at:now,job_reference:jobReference,
    catalog_name:pack.name,catalog_id:pack.catalog_id,sample_data:!!pack.sample_data,
    unapproved_findings:items.filter(i=>!approvalIsCurrent(pack,i,jobReference)).map(i=>i.id),
    approvals:approved.map(i=>({...i.approval,retrieval:i.retrieval||"manual",
      evidence:i.result?.candidates.filter(c=>i.codes.includes(c.row.code)).map(c=>({code:c.row.code,score:c.score,matched:c.matched}))||[]}))};
}
