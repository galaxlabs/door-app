#!/usr/bin/env bash
set -euo pipefail

WEB_ORIGIN="${WEB_ORIGIN:-http://127.0.0.1:3002}"
API_ORIGIN="${API_ORIGIN:-http://127.0.0.1:8010}"
MOBILE_ORIGIN="${MOBILE_ORIGIN:-http://127.0.0.1:8082}"

MAX_REDIRS="${MAX_REDIRS:-5}"

ok=0
fail=0

print_ok() {
  ok=$((ok + 1))
  printf "OK  %s\n" "$1"
}

print_fail() {
  fail=$((fail + 1))
  printf "ERR %s\n" "$1"
}

http_code() {
  local url="$1"
  local code=""
  if code="$(curl -sS -L --max-redirs "${MAX_REDIRS}" -o /dev/null -w "%{http_code}" "${url}" 2>/dev/null)"; then
    printf "%s" "${code}"
    return 0
  fi
  printf "000"
}

expect_one_of() {
  local label="$1"
  local url="$2"
  shift 2
  local expected=("$@")

  local code
  code="$(http_code "${url}")"

  for exp in "${expected[@]}"; do
    if [[ "${code}" == "${exp}" ]]; then
      print_ok "${label} (${code})"
      return 0
    fi
  done

  print_fail "${label} (${code}) ${url}"
  return 1
}

echo "Door App smoke check"
echo "- WEB_ORIGIN=${WEB_ORIGIN}"
echo "- API_ORIGIN=${API_ORIGIN}"
echo "- MOBILE_ORIGIN=${MOBILE_ORIGIN}"
echo

# Backend direct
expect_one_of "Backend docs" "${API_ORIGIN}/api/v1/docs/" 200
expect_one_of "Backend me (unauth ok)" "${API_ORIGIN}/api/v1/auth/me/" 401 403 200

# Web pages
expect_one_of "Web login page" "${WEB_ORIGIN}/auth/login" 200
expect_one_of "Web dashboard" "${WEB_ORIGIN}/dashboard" 200
expect_one_of "Web doors" "${WEB_ORIGIN}/dashboard/doors" 200
expect_one_of "Web profile" "${WEB_ORIGIN}/dashboard/profile" 200

# Web API proxy (same-origin) — important for public-host deployments
expect_one_of "Web→API proxy docs" "${WEB_ORIGIN}/api/v1/docs/" 200
expect_one_of "Web→API proxy codes (unauth ok)" "${WEB_ORIGIN}/api/v1/qr/codes/" 401 403 200

# Public meeting page (no auth required)
expect_one_of "Meet share page" "${WEB_ORIGIN}/meet?title=Gate%203&location=Parking%20A&note=Location:%2031.5204,%2074.3587&duration=2" 200

# Next.js static assets referenced by dashboard profile HTML.
# This catches common "_next/static/... 404" deployment issues.
tmp_html="$(mktemp)"
curl -sS -L --max-redirs "${MAX_REDIRS}" "${WEB_ORIGIN}/dashboard/profile" > "${tmp_html}" || true
mapfile -t next_assets < <(grep -o '/_next/static[^" ]*' "${tmp_html}" | sed 's/\\$//' | sort -u)
rm -f "${tmp_html}"

if [[ "${#next_assets[@]}" -eq 0 ]]; then
  print_fail "Web _next assets discovered from profile HTML (0 found)"
else
  asset_fail=0
  for asset in "${next_assets[@]}"; do
    code="$(http_code "${WEB_ORIGIN}${asset}")"
    if [[ "${code}" == "200" ]]; then
      print_ok "Web asset ${asset} (${code})"
    else
      print_fail "Web asset ${asset} (${code})"
      asset_fail=1
    fi
  done
  if [[ "${asset_fail}" -ne 0 ]]; then
    :
  fi
fi

# Mobile (optional; only checks if it is already running)
mobile_code="$(http_code "${MOBILE_ORIGIN}/")"
if [[ "${mobile_code}" == "200" ]]; then
  print_ok "Mobile web root (${mobile_code})"
else
  echo "SKIP Mobile web root (${mobile_code}) — start it with: cd door_mobile && flutter run -d web-server --web-port 8082 --web-hostname 127.0.0.1"
fi

echo
echo "Summary: ok=${ok} fail=${fail}"
if [[ "${fail}" -ne 0 ]]; then
  exit 1
fi
