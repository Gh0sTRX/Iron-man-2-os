#!/bin/bash
set -euo pipefail
im2_repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
im2_python=${IM2_OWNER_PYTHON:-python3}
im2_ipa=
im2_assets=
im2_link=
while (($#)); do
  case "$1" in
    --ipa) im2_ipa=$2; shift 2 ;;
    --asset-root) im2_assets=$2; shift 2 ;;
    --drive-link-file) im2_link=$2; shift 2 ;;
    *) echo 'Usage: refresh_owner_audio.sh --ipa /external/owner.ipa --asset-root /external/assets [--drive-link-file /external/link.txt]' >&2; exit 2 ;;
  esac
done
test -n "$im2_ipa" && test -n "$im2_assets"
cd "$im2_repo"
if [[ ! -f "$im2_ipa" ]]; then
  test -n "$im2_link"
  "$im2_python" tools/fetch_owner_ipa.py --drive-link-file "$im2_link" --output "$im2_ipa"
fi
"$im2_python" tools/prepare_audio_assets.py --ipa "$im2_ipa" --asset-root "$im2_assets"
IM2_ASSET_ROOT="$im2_assets" bash tools/test_host.sh
IM2_HOST_BUILD=build-sanitized IM2_SANITIZERS=ON IM2_ASSET_ROOT="$im2_assets" bash tools/test_host.sh
bash tools/build_vita.sh
# No package, upload or device installation step.
