import {test,expect} from "@playwright/test";
import fs from "node:fs/promises";

test.beforeEach(async({page})=>{await page.goto("/");});
async function clearMatch(page){
  await page.locator("#job").fill("Unit 42");
  await page.getByRole("button",{name:"Clear match",exact:true}).click();
  await page.getByRole("checkbox",{name:"Select RVS-0904",exact:true}).check();
  await page.getByLabel("Reviewer name",{exact:true}).fill("Demo reviewer");
  await page.locator("#confirmed").check();
  await page.getByRole("button",{name:"Approve this finding",exact:true}).click();
}
async function downloadText(page,button){
  const waiting=page.waitForEvent("download");
  await page.locator(button).click();
  const download=await waiting;
  return fs.readFile(await download.path(),"utf8");
}
test("a visitor can approve a finding and download actual CSV and JSON",async({page})=>{
  const errors=[];page.on("pageerror",e=>errors.push(e.message));
  await clearMatch(page);
  await expect(page.locator("#approvedCount")).toHaveText("1 of 1 findings approved");
  const csv=await downloadText(page,"#exportCsv");
  expect(csv).toContain('"Unit 42"');expect(csv).toContain('"RVS-0904"');
  expect(csv).toContain('"Demo reviewer"');
  const audit=JSON.parse(await downloadText(page,"#exportAudit"));
  expect(audit.approvals).toHaveLength(1);
  expect(audit.approvals[0].codes).toEqual(["RVS-0904"]);
  expect(audit.approvals[0].job_reference).toBe("Unit 42");
  expect(audit.approvals[0].catalog_id).toBeTruthy();
  expect(errors).toEqual([]);
});
test("an uncertain symptom asks questions and selects nothing",async({page})=>{
  await page.getByRole("button",{name:"Unclear symptom",exact:true}).click();
  await expect(page.locator(".question").first()).toBeVisible();
  await expect(page.locator("#selectedCount")).toHaveText("0 lines selected");
  await expect(page.locator("#exportCsv")).toBeDisabled();
});
test("spelling evidence is shown as a possible correction",async({page})=>{
  await page.getByRole("button",{name:"Spelling variant",exact:true}).click();
  await expect(page.locator(".evidence .typo").first()).toBeVisible();
  await expect(page.locator("#exportCsv")).toBeDisabled();
});
test("companion work is a visible review decision and gates approval",async({page})=>{
  await page.getByRole("button",{name:"Companion work",exact:true}).click();
  await page.getByRole("checkbox",{name:"Select RVS-0202",exact:true}).check();
  await expect(page.locator(".gap").first()).toContainText("leak-down");
  await page.locator("#reviewer").fill("Demo reviewer");await page.locator("#confirmed").check();
  await expect(page.locator("#approveBtn")).toBeDisabled();
  await page.locator(".gap").getByRole("button",{name:/Select RVS-0201/}).click();
  await expect(page.locator("#confirmed")).not.toBeChecked();
  await page.locator("#confirmed").check();await page.locator("#approveBtn").click();
  const audit=JSON.parse(await downloadText(page,"#exportAudit"));
  expect(audit.approvals[0].codes.sort()).toEqual(["RVS-0201","RVS-0202"]);
});
test("an override cannot silently apply to a changed selection",async({page})=>{
  await page.locator("#finding").fill("Replace confirmed failed LP regulator");
  await page.locator("#matchBtn").click();
  await page.getByRole("checkbox",{name:"Select RVS-0202",exact:true}).check();
  await page.locator("#overrideReason").fill("Example rule reviewed; intentionally incomplete draft");
  await page.locator("#reviewer").fill("Demo reviewer");await page.locator("#confirmed").check();
  await page.locator("#approveBtn").click();
  await page.getByRole("checkbox",{name:"Select RVS-0202",exact:true}).uncheck();
  await page.getByRole("checkbox",{name:"Select RVS-0202",exact:true}).check();
  await expect(page.locator("#overrideReason")).toHaveValue("");
  await expect(page.locator("#exportCsv")).toBeDisabled();
});
test("editing the finding or unit invalidates its approval",async({page})=>{
  await clearMatch(page);await page.locator("#job").fill("Different unit");
  await expect(page.locator("#exportCsv")).toBeDisabled();
  await expect(page.locator("#approvedCount")).toHaveText("0 of 1 findings approved");
  await page.locator("#confirmed").check();await page.locator("#approveBtn").click();
  await page.locator("#finding").fill("A different problem");
  await expect(page.locator("#exportCsv")).toBeDisabled();
  await expect(page.locator("#selectedCount")).toHaveText("0 lines selected");
});
test("catalog changes can be cancelled before the draft is cleared",async({page})=>{
  await clearMatch(page);
  await page.locator("#domain").selectOption("property_restoration");
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByRole("button",{name:"Keep current draft",exact:true}).click();
  await expect(page.locator("#domain")).toHaveValue("rv_service");
  await expect(page.locator("#exportCsv")).toBeEnabled();
  await page.locator("#domain").selectOption("property_restoration");
  await page.getByRole("button",{name:"Start new draft",exact:true}).click();
  await expect(page.locator("#domain")).toHaveValue("property_restoration");
  await expect(page.locator("#finding")).toHaveValue("");
  await expect(page.locator("#exportCsv")).toBeDisabled();
});
test("valid custom upload works and invalid upload preserves the draft",async({page})=>{
  await page.locator("#upload").setInputFiles({name:"shop.csv",mimeType:"text/csv",buffer:Buffer.from("code,section,description,hours\nTEST-1,Water,Replace faucet,1\n")});
  await expect(page.locator("#domain")).toHaveValue("uploaded");
  await expect(page.locator("#catalogInfo")).toContainText("no companion rules");
  await page.locator("#finding").fill("Replace failed faucet");
  await page.locator("#matchBtn").click();
  await page.getByRole("checkbox",{name:"Select TEST-1",exact:true}).check();
  await expect(page.locator("#completeness")).toContainText("not checked");
  await page.locator("#upload").setInputFiles({name:"bad.csv",mimeType:"text/csv",buffer:Buffer.from("code,section,description,hours\nBAD,S,D,NaN\n")});
  await expect(page.locator("#messages")).toContainText("Catalog not loaded");
  await expect(page.locator("#selected")).toContainText("TEST-1");
  await expect(page.locator("#domain")).toHaveValue("uploaded");
});
test("manual search cannot select an unknown code",async({page})=>{
  await page.locator(".manual-details summary").click();
  await page.locator("#manualSearch").fill("NOT-A-CODE");
  await expect(page.locator("#manualResults")).toContainText("No catalog code matches");
  await expect(page.locator("#selectedCount")).toHaveText("0 lines selected");
});
test("phone width has no horizontal page overflow",async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.getByRole("button",{name:"Clear match",exact:true}).click();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1)).toBe(true);
  await page.screenshot({path:"test-results/mobile-demo.png",fullPage:true});
});
