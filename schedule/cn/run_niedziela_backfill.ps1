# NIEDZIELA — backfill (CN) 10:30
. "$PSScriptRoot\_common.ps1"
Enter-CnCampaign
$env:SCRAPER_TIMEZONE = "Asia/Shanghai"
Remove-Item Env:DISABLE_SEND_WINDOW -ErrorAction SilentlyContinue
Write-Host "[PL ND] Weryfikacja www..."
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --verify-pending-contacts
Write-Host "[PL ND] Backfill e-maili..."
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --backfill-emails-from-cache
Write-Host "[PL ND] Rebuild Excel..."
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --rebuild-from-cache
