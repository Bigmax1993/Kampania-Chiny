# PIATEK — discovery czesc 5 (CN) 21:00
. "$PSScriptRoot\_common.ps1"
Enter-CnCampaign
$env:SCRAPER_TIMEZONE = "Asia/Shanghai"
Remove-Item Env:DISABLE_SEND_WINDOW -ErrorAction SilentlyContinue
Write-Host "[PL PT] Discovery czesc 5"
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --serper-only-discovery --no-auto-email --rotate-province --respect-cache @args
