#!/bin/bash

NODE01_LOG="node01.log"
LOCALDB_LOG="localdb.log"
BASH_LOG="bash_log.log"
CONTAINER_MONITOR_LOG="container_monitor.log"
START_TIME=$(date +"%Y-%m-%d %H:%M:%S,%3N")
PUMBA_LOG="pumba.log"
PUMBA_START_TIME=""
PUMBA_PERCENT=90
PUMBA_TIME=10   # minutos

rm -f $NODE01_LOG $LOCALDB_LOG $BASH_LOG $CONTAINER_MONITOR_LOG $PUMBA_LOG

echo "$START_TIME - INFO - Starting docker-compose build and up for node01" | tee -a $BASH_LOG

cd node01 || { echo "node01 folder not found"; exit 1; }
docker compose up --build -d --force-recreate
sleep 20
docker compose logs -f localdb > ../$LOCALDB_LOG 2>&1 &
docker compose logs -f node01 > ../$NODE01_LOG 2>&1 &
COMPOSE_PID=$!

# roda o monitor de bytes
echo "$(date +"%Y-%m-%d %H:%M:%S,%3N") - INFO - Starting container monitoring" | tee -a ../$BASH_LOG
python3 ../monitor_container.py > ../$CONTAINER_MONITOR_LOG 2>&1 &
MONITOR_PID=$!

# 10 min run = 600
sleep 120

# echo "$(date +"%Y-%m-%d %H:%M:%S,%3N") - INFO - Stopping node01 and localdb containers" | tee -a ../$BASH_LOG
# docker-compose down >> ../$BASH_LOG 2>&1

############ PUMBA TIME ############
cd ..   ## volta pro ~/pasta do proj
PUMBA_START_TIME=$(date +"%Y-%m-%d %H:%M:%S,%3N")
echo "$PUMBA_START_TIME - INFO - Running delay.sh to start pumba with 90% network loss" | tee -a $BASH_LOG

# muda a % do pumba
sed -i "s/--percent [0-9]* node01/--percent ${PUMBA_PERCENT} node01/" delay.sh
./delay.sh > $PUMBA_LOG 2>&1 &
PUMBA_PID=$!

# 10 min run
sleep 120

echo "$(date +"%Y-%m-%d %H:%M:%S,%3N") - INFO - Pumba finished" | tee -a $BASH_LOG

# +5 minutos com dados totais
sleep 120

echo "$(date +"%Y-%m-%d %H:%M:%S,%3N") - INFO - Stopping containers" | tee -a $BASH_LOG

# volta e desliga os containers
# e mata os processos velhos
cd node01 || { echo "node01 folder not found"; exit 1; }
docker compose down
sleep 5
kill -9 $COMPOSE_PID $MONITOR_PID $PUMBA_PID 2>/dev/null

echo "$(date +"%Y-%m-%d %H:%M:%S,%3N") - INFO - Script finished" | tee -a $BASH_LOG
