# PONIEDZIALEK — discovery czesc 1 (CN), +5h wzgledem UA.
. "$PSScriptRoot\_common.ps1"
Enter-CnCampaign
$env:SCRAPER_TIMEZONE = "Asia/Shanghai"
Remove-Item Env:DISABLE_SEND_WINDOW -ErrorAction SilentlyContinue
Write-Host "[PL PON] Discovery czesc 1 (serper-only) 22:00"
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --serper-only-discovery --no-auto-email --rotate-province @args
