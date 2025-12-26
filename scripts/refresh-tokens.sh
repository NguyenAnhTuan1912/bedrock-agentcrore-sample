#!/bin/bash

# Import env here
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup-env.sh"

aws cognito-idp initiate-auth \
  --client-id "$CLIENT_ID" \
  --auth-flow REFRESH_TOKEN_AUTH \
  --auth-parameters REFRESH_TOKEN="$REFRESH_TOKEN" \
  --profile $AWS_PROFILE | jq
