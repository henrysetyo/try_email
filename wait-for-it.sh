#!/usr/bin/env bash
#   Use this script to test if a given TCP host/port are available

set -e

TIMEOUT=15
QUIET=0
HOST=""
PORT=""
WAITCMD=""

usage()
{
    cat << USAGE >&2
Usage:
    $0 host:port [-s] [-t timeout] [-- command args]
    -q | --quiet                        Do not output any status messages
    -s | --strict                       Only execute subcommand if the test succeeds
    -t TIMEOUT | --timeout=timeout      Timeout in seconds, zero for no timeout
    -- COMMAND ARGS                     Execute command with args after the test finishes
USAGE
    exit 1
}

wait_for()
{
    if ! command -v nc > /dev/null; then
        echo 'Error: "nc" command is required but not found'
        exit 1
    fi

    for i in `seq $TIMEOUT` ; do
        if echo > /dev/tcp/$HOST/$PORT ; then
            return 0
        fi
        sleep 1
    done
    return 1
}

wait_for_wrapper()
{
    if wait_for ; then
        if [ -n "$WAITCMD" ] ; then
            exec $WAITCMD
        fi
    else
        if [ "$QUIET" -ne 1 ] ; then echo "Timeout occurred after waiting $TIMEOUT seconds for $HOST:$PORT"; fi
        exit 1
    fi
}

while [ $# -gt 0 ]
do
    case "$1" in
        *:* )
        HOSTPORT=(${1//:/ })
        HOST=${HOSTPORT[0]}
        PORT=${HOSTPORT[1]}
        shift 1
        ;;
        -q | --quiet)
        QUIET=1
        shift 1
        ;;
        -s | --strict)
        STRICT=1
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        shift 2
        ;;
        --timeout=*)
        TIMEOUT="${1#*=}"
        shift 1
        ;;
        --)
        shift
        WAITCMD="$@"
        break
        ;;
        --help)
        usage
        ;;
        *)
        echo "Unknown argument: $1"
        usage
        ;;
    esac
done

if [ "$HOST" = "" -o "$PORT" = "" ]; then
    echo "Error: you need to provide a host and port to test."
    usage
fi

wait_for_wrapper
