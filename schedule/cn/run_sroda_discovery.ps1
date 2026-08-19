# SRODA — discovery czesc 3 (CN) 00:00 (czwartek noc)
. "$PSScriptRoot\_common.ps1"
Enter-CnCampaign
$env:SCRAPER_TIMEZONE = "Asia/Shanghai"
Remove-Item Env:DISABLE_SEND_WINDOW -ErrorAction SilentlyContinue
Write-Host "[PL SR] Discovery czesc 3"
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --serper-only-discovery --no-auto-email --rotate-province --respect-cache @args
