# PONIEDZIALEK — prep (CN) 12:00
. "$PSScriptRoot\_common.ps1"
Enter-CnCampaign
$env:SCRAPER_TIMEZONE = "Asia/Shanghai"
Write-Host "[PL PON] Prep rebuild Excel"
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --rebuild-from-cache @args
