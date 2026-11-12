#!/bin/bash
# Deploys the Telegram client's Lambda functions from THIS machine.
# Deployment is deliberately not automated in CI (see AGENTS.md, "Boundaries").
#
#   ./deploy_to_aws.sh                 package and update the three functions
#   ./deploy_to_aws.sh --store-token   first store the bot token in SSM (asks for it, input hidden)
#
# Uses your normal AWS CLI credentials/profile (AWS_PROFILE) and AWS_REGION (default us-east-1).
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
FUNCTIONS=(planespotter-webhook planespotter-radar planespotter-sync)
SSM_PARAM="plainspotter_api_key"
HERE="$(cd "$(dirname "$0")" && pwd)"

if [ "${1:-}" = "--store-token" ]; then
    # The token goes through a private temp file so it never appears on a command line or in shell history.
    read -r -s -p "Telegram bot token (input hidden): " BOT_TOKEN; echo
    TMP="$(umask 077 && mktemp)"; trap 'rm -f "$TMP"' EXIT
    printf '%s' "$BOT_TOKEN" > "$TMP"; unset BOT_TOKEN
    aws ssm put-parameter --name "$SSM_PARAM" --value "file://$TMP" --type SecureString --overwrite --region "$REGION" > /dev/null
    echo "Token stored in SSM parameter $SSM_PARAM"
fi

ZIP="$(mktemp -d)/lambda.zip"
echo "Packaging aws_lambda/ ..."
(cd "$HERE/aws_lambda" && zip -q -r "$ZIP" . -x "*__pycache__*" -x "*.DS_Store")

for FN in "${FUNCTIONS[@]}"; do
    echo "Updating $FN ..."
    aws lambda update-function-code --function-name "$FN" --zip-file "fileb://$ZIP" --region "$REGION" > /dev/null
done
echo "Done: ${#FUNCTIONS[@]} functions updated in $REGION."
