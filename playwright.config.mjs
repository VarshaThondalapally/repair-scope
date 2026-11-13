import {defineConfig} from "@playwright/test";
export default defineConfig({
  testDir:"./tests/browser",
  fullyParallel:false,
  retries:0,
  reporter:[["list"],["html",{open:"never"}]],
  use:{baseURL:"http://127.0.0.1:8765",browserName:"chromium",trace:"retain-on-failure",screenshot:"only-on-failure"},
  webServer:{command:"python -m http.server 8765 --bind 127.0.0.1 --directory dist",url:"http://127.0.0.1:8765",reuseExistingServer:false,timeout:15000},
});
