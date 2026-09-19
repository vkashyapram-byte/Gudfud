#!/bin/bash
set -e

PRODUCTION_DOMAIN=${CUSTOM_DOMAIN:-"www.gudfud.com"}
SITE_URL="https://${PRODUCTION_DOMAIN}"

echo "Starting strict Vercel deployment for ${SITE_URL}..."

# Unconditionally link the project (assumes VERCEL_ORG_ID and VERCEL_PROJECT_ID are set in env)
vercel link --yes

# Set NEXT_PUBLIC_SITE_URL environment variable to the production domain
echo -n "${SITE_URL}" | vercel env add NEXT_PUBLIC_SITE_URL production || true

# Add the custom domain using vercel domains add
vercel domains add "${PRODUCTION_DOMAIN}"

# Trigger a production build using vercel deploy --prod --yes
vercel deploy --prod --yes

echo "Frontend successfully deployed."
