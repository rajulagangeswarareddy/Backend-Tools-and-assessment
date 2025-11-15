from services.hubspot_api_service import HubSpotAPIService

# Replace with your token from .env
ACCESS_TOKEN = "YOUR_TOKEN_HERE"
service = HubSpotAPIService(
    access_token=ACCESS_TOKEN,
    base_url="https://api.hubapi.com",
    timeout=30
)

print("Testing HubSpot Deals API...\n")

try:
    deals = service.get_all_deals(limit=10)

    count = 0
    for deal in deals:
        print(deal.get("id"), deal["properties"].get("dealname"))
        count += 1

        if count >= 10:
            break

    print("\nSUCCESS: HubSpot connection working.")

except Exception as e:
    print("\nERROR:", str(e))
