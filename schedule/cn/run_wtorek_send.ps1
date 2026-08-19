# WTOREK — wysylka partia 2 (CN) 14:00
. "$PSScriptRoot\_common.ps1"
Enter-CnCampaign
$env:SCRAPER_TIMEZONE = "Asia/Shanghai"
Remove-Item Env:DISABLE_SEND_WINDOW -ErrorAction SilentlyContinue
Write-Host "[PL WT] Wysylka partia 2"
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --send-emails-only --ignore-send-window @args
