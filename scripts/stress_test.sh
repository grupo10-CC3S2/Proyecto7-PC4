#!/usr/bin/env bash

BASE_URL="http://localhost:8080"
TOTAL_REQUESTS=100

for i in $(seq 1 $TOTAL_REQUESTS); do

    # se obtiene tipo de request y tiempo de espera aleatorio
    request_type=$(( ( RANDOM % 4 ) + 1 ))
    sleep_time_ms=$(( ( RANDOM % 500 ) + 100 ))

    echo -n "request #$i: "

    # se hacen requests a distintas rutas
    case $request_type in
        [1])
        echo "OK -> GET /"
        curl -s -o /dev/null "$BASE_URL/"
        ;;
        [2])
        echo "OK -> GET /health"
        curl -s -o /dev/null "$BASE_URL/health"
        ;;
        [3])
        echo "SERVER_ERROR -> GET /error"
        curl -s -o /dev/null "$BASE_URL/error"
        ;;
        [4])
        echo "BAD_REQUEST -> GET /no"
        curl -s -o /dev/null "$BASE_URL/no"
        ;;
    esac

    sleep "0.${sleep_time_ms}"
done