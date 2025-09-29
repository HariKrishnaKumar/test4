# Merchant Address Storage Fix

## 🐛 **Issue Identified**

The merchant detail API was not properly storing address components in the merchant_detail table. The issue was:

1. **Wrong API Endpoint**: The code was only calling `/v3/merchants/{merchant_id}/address` which only returns address data
2. **Missing Merchant Data**: It wasn't calling the main merchant endpoint to get name, email, currency, timezone
3. **Incorrect Field Mapping**: Address fields were being extracted from the wrong data source

## ✅ **Fixes Applied**

### 1. **Updated Merchant Details Endpoint** (`app/routes/clover_data.py`)

**Before:**
```python
# Only called address endpoint
url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant_id}/address"
merchant_data = r.json()
```

**After:**
```python
# Call both merchant and address endpoints
merchant_url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant_id}"
address_url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant_id}/address"

# Get main merchant data
merchant_response = await client.get(merchant_url, headers=_build_headers(access_token))
merchant_data = merchant_response.json()

# Get address data
address_response = await client.get(address_url, headers=_build_headers(access_token))
address_data = address_response.json()
```

### 2. **Fixed Address Field Extraction**

**Before:**
```python
# Trying to get address fields from merchant_data (which only had basic merchant info)
existing_merchant.address = str(merchant_data.get("address1", ""))
existing_merchant.city = str(merchant_data.get("city", ""))
```

**After:**
```python
# Get merchant info from merchant_data
existing_merchant.name = str(merchant_data.get("name", ""))
existing_merchant.email = str(merchant_data.get("email", ""))
existing_merchant.currency = str(merchant_data.get("currency", ""))
existing_merchant.timezone = str(merchant_data.get("timezone", ""))

# Get address info from address_data (proper source)
existing_merchant.address = str(address_data.get("address1", ""))
existing_merchant.city = str(address_data.get("city", ""))
existing_merchant.state = str(address_data.get("state", ""))
existing_merchant.country = str(address_data.get("country", ""))
existing_merchant.postal_code = str(address_data.get("zip", ""))
```

### 3. **Enhanced Geocoding Logic** (`helpers/merchant_helper.py`)

**Before:**
```python
# Only tried to get address from merchant_data
address = merchant_data.get("address1") or merchant_data.get("address")
```

**After:**
```python
# First try merchant_detail object (already stored), then merchant_data
address = merchant_detail.address
city = merchant_detail.city
state = merchant_detail.state
country = merchant_detail.country
postal_code = merchant_detail.postal_code

# Fallback to merchant_data if not available
if not address:
    address = merchant_data.get("address1") or merchant_data.get("address")
    # ... etc
```

### 4. **Added Verification Endpoint**

Created a new endpoint to verify stored address data:

```python
@merchant_router.get("/stored-details/{merchant_id}")
async def get_stored_merchant_details(merchant_id: str, db: Session = Depends(get_db)):
    """Get stored merchant details from database to verify address storage"""
```

## 🧪 **Testing the Fix**

### **1. Test Merchant Details Storage**
```bash
# Store merchant details (this will now properly store address components)
GET /merchant/details?merchant_id=4KE9A8XJVT821
```

### **2. Verify Stored Data**
```bash
# Check what was actually stored in the database
GET /merchant/stored-details/4KE9A8XJVT821
```

**Expected Response:**
```json
{
    "success": true,
    "message": "Stored merchant details retrieved successfully",
    "data": {
        "merchant_id": "4KE9A8XJVT821",
        "name": "Merchant Name",
        "address": "4329 Alpha Avenue",
        "city": "Winterhaven",
        "state": "California",
        "country": "US",
        "postal_code": "92283",
        "email": "merchant@example.com",
        "currency": "USD",
        "timezone": "America/Los_Angeles",
        "latitude": 32.7391,
        "longitude": -114.6472,
        "created_at": "2025-01-15T10:30:00",
        "updated_at": "2025-01-15T10:30:00"
    }
}
```

### **3. Test Geocoding**
```bash
# Test geocoding with the stored address
POST /merchant/geocode?address=4329 Alpha Avenue&city=Winterhaven&state=California&country=US&postal_code=92283
```

## 📊 **Database Schema Verification**

The merchant_detail table now properly stores:

| Column | Source | Example Value |
|--------|--------|---------------|
| `address` | `address_data.address1` | "4329 Alpha Avenue" |
| `city` | `address_data.city` | "Winterhaven" |
| `state` | `address_data.state` | "California" |
| `country` | `address_data.country` | "US" |
| `postal_code` | `address_data.zip` | "92283" |
| `name` | `merchant_data.name` | "Merchant Name" |
| `email` | `merchant_data.email` | "merchant@example.com" |
| `currency` | `merchant_data.currency` | "USD" |
| `timezone` | `merchant_data.timezone` | "America/Los_Angeles" |
| `latitude` | Geocoding result | 32.7391 |
| `longitude` | Geocoding result | -114.6472 |

## 🎯 **Benefits of the Fix**

1. **✅ Proper Address Storage**: Address components are now stored in their correct columns
2. **✅ Complete Merchant Data**: Both merchant info and address info are captured
3. **✅ Accurate Geocoding**: Geocoding uses the properly stored address data
4. **✅ Data Integrity**: All fields are populated from the correct API responses
5. **✅ Verification**: New endpoint allows checking what was actually stored

## 🚀 **Usage**

The merchant detail API now works correctly:

1. **Call the endpoint**: `GET /merchant/details?merchant_id=YOUR_MERCHANT_ID`
2. **Check stored data**: `GET /merchant/stored-details/YOUR_MERCHANT_ID`
3. **Verify geocoding**: Check that latitude/longitude are populated

The address components are now properly separated and stored in their respective database columns, and geocoding works with the complete address information!

