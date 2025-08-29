# GCP Logging Setup Guide

## Step 1 & 2: Enable APIs and Create Service Account

Run these commands (replace `YOUR_PROJECT_ID` with your actual project ID):

```bash
# Enable required APIs
gcloud services enable logging.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# Create service account
gcloud iam service-accounts create chatbot-logger \
    --display-name="Chatbot Logger Service Account" \
    --description="Service account for recruiter chatbot logging"

# Grant logging permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:chatbot-logger@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"

# Create credentials JSON file
gcloud iam service-accounts keys create chatbot-credentials.json \
    --iam-account=chatbot-logger@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## Step 3: Configure Credentials for Streamlit Cloud

### Option A: Using Streamlit Secrets (Recommended)

1. Open your `chatbot-credentials.json` file
2. Copy the entire JSON content
3. In Streamlit Cloud, go to your app settings → Secrets
4. Add this configuration:

```toml
[gcp_service_account]
# Paste the JSON content here, converting it to TOML format:
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "chatbot-logger@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robots/v1/metadata/x509/chatbot-logger%40your-project-id.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

### Option B: Using Environment Variable

In Streamlit Cloud app settings → Environment Variables:

```
GCP_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project-id",...}
```

Just paste the entire JSON content from `chatbot-credentials.json` as the value.

## Step 4: Enable GCP Logging

Update your `configs/config.yaml`:

```yaml
logging:
  use_gcp_logging: true
  log_level: "INFO"
  environment: "production"
  service_name: "recruiter-chatbot"
```

## Step 5: View Logs

Go to [Google Cloud Console → Logging](https://console.cloud.google.com/logs/query)

Use this filter to see your chatbot logs:
```
resource.type="global"
jsonPayload.service="recruiter-chatbot"
```

## Testing Locally

For local development:

```bash
# Option 1: Set environment variable with JSON content
export GCP_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'

# Option 2: Use the credentials file (traditional way)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/chatbot-credentials.json"

# Enable GCP logging
export USE_GCP_LOGGING=true
```

Then update your local `configs/config.yaml`:
```yaml
logging:
  use_gcp_logging: true
```

Run the integration test:
```bash
python test_integration.py
```

## Cost Information

- **Free tier**: 50 GiB per month
- **Your usage**: Likely <1 GiB/month = $0.00
- **Paid tier**: $0.50 per GiB after free tier

The chatbot generates approximately:
- ~2-5 KB per interaction
- ~1 KB per rate limit event
- ~500 bytes per system event

Even with 1000 interactions/day, you'll stay well within the free tier.