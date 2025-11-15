/crm/v3/objects/deals
Authorization: Bearer <PRIVATE_APP_ACCESS_TOKEN>
Content-Type: application/json
GET https://api.hubapi.com/crm/v3/objects/deals?limit=100&after=XXXX
Authorization: Bearer <token>
Content-Type: application/json

Start Scan → Create Job → Fetch Deals in Batches → Store Results → Update Progress → Complete Scan

job_service.update_status("running")

hubspot_deals_extraction
after = None
GET /crm/v3/objects/deals?limit=100&after=<cursor>
processed_items += 1
total_items += batch_size
try:
    ...
except Exception as e:
    job_service.mark_failed(error_message=str(e))
