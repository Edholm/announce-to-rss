#!/usr/bin/bash
# Script to download a file on a user supplied interval. If the new file
# differs from the old, overwrite it, and run the supplied --cmd (if applicable)

while [[ $# > 1 ]]; do
  key="$1"

  case $key in
    -u|--url)
    URL="$2"
    shift
    ;;
    -i|--interval)
    INTERVAL="$2"
    shift
    ;;
    -d|--dest)
    DEST="$2"
    shift
    ;;
    -c|--cmd)
    CMD="$2"
    shift
    ;;
    *)
    echo "Unknown option: " "${key}"
    ;;
  esac
  shift
done

die() {
  echo "Error: $1"
  exit 1
}
info() {
  echo "Info: $1"
}

if [ -z "${INTERVAL}" ]; then
  # 30 min default value
  INTERVAL=1800
  info "using default interval of ${INTERVAL}s"
fi

if [ -z "${URL}" ] || [ -z "${DEST}" ]; then
  die "--url and --dest is required"
fi


while true; do
  tmpfile=$(mktemp)
  if wget "${URL}" -O "${tmpfile}" -nv; then
    if [ -f "${DEST}" ]; then
      # Check if different
      if ! cmp "${DEST}" "${tmpfile}" --silent; then
        different=true
      fi
    fi

    mv "${tmpfile}" "${DEST}"
    touch "${DEST}"
    chmod 644 "${DEST}"
    if [ "$different" = true ] && [ -n "${CMD}" ]; then
      info "New file is different, executing command"
      eval ${CMD}
    fi
  else
    info "wget failed..."
  fi
  sleep ${INTERVAL}
done
