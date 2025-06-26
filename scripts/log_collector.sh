#!/bin/bash

namespace=${1:-default}

mkdir -p logs

pods=$(kubectl get pods -n "$namespace" -o name | sed 's|pod/||')

for pod in $pods; do
    echo "=================== Logs del pod: $pod ===================" >> "logs/all_pods.log"
    kubectl logs "$pod" -n "$namespace" | tee -a "logs/$(echo "$pod" | sed 's|timeserver-7c9445b569-||').log" >> "logs/all_pods.log"
    echo "====== Recolleción de logs del pod $pod completada =======" >> "logs/all_pods.log"
    echo "----------------------------------------------------------" >> "logs/all_pods.log"
    echo "Logs del pod $pod guardados en logs/$(echo "$pod" | sed 's|timeserver-||').log"
done

echo "Todos los logs han sido guardados en logs/all_pods.log"

echo "===================== Eventos del Cluster =====================" >> "logs/all_pods.log"
kubectl get events -n "$namespace" >> "logs/all_events.log"

echo "Eventos del cluster guardados en logs/all_events.log"
