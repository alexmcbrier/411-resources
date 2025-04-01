#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5010/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


###############################################
#
# Boxer Management
#
###############################################

add_boxer1() {
  echo "Adding boxer (Boxer1)..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d '{"name": "Boxer1", "weight": 200, "height": 190, "reach": 76.5, "age": 30}')
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer1 added successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to add Boxer1."
    exit 1
  fi
}

add_boxer2() {
  echo "Adding boxer (Boxer2)..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d '{"name": "Boxer2", "weight": 210, "height": 185, "reach": 75.0, "age": 29}')
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer2 added successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to add Boxer2."
    exit 1
  fi
}

get_boxer_by_name() {
  echo "Getting boxer by name (Boxer1)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/Boxer1")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer1 retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to get Boxer1 by name."
    exit 1
  fi
}

get_boxer_by_id() {
  echo "Getting boxer by ID (1)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/1")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID."
  fi
}

delete_boxer() {
  echo "Deleting boxer by ID (1)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/1")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully."
  else
    echo "Failed to delete boxer by ID."
  fi
}


###############################################
#
# Ring Management
#
###############################################

enter_ring_boxer1() {
  echo "Entering Boxer1 into ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d '{"name": "Boxer1"}')
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer1 entered the ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to enter Boxer1 into ring."
    exit 1
  fi
}

enter_ring_boxer2() {
  echo "Entering Boxer2 into ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d '{"name": "Boxer2"}')
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer2 entered the ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to enter Boxer2 into ring."
    exit 1
  fi
}

get_boxers_in_ring() {
  echo "Getting boxers in ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers retrieved from ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxers in ring."
    exit 1
  fi
}

clear_ring() {
  echo "Clearing boxers from ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully."
  else
    echo "Failed to clear ring."
    exit 1
  fi
}


###############################################
#
# Fight
#
###############################################

fight_boxers() {
  echo "Triggering fight..."
  response=$(curl -s -X GET "$BASE_URL/fight")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Fight triggered successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  elif echo "$response" | grep -q '"status": "error"'; then
    echo "Fight could not be triggered (expected if <2 boxers)."
  else
    echo "Unexpected response from fight endpoint."
    exit 1
  fi
}


###############################################
#
# Leaderboard
#
###############################################

get_leaderboard() {
  echo "Getting leaderboard (sorted by wins)..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard."
    exit 1
  fi
}


###############################################
#
# Run all smoketests
#
###############################################

check_health
check_db

add_boxer1
add_boxer2

get_boxer_by_name
get_boxer_by_id

enter_ring_boxer1
enter_ring_boxer2

get_boxers_in_ring
fight_boxers
clear_ring

get_leaderboard
delete_boxer

echo "All tests passed successfully."
