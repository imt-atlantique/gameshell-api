#!/bin/bash

# Base URL of the FastAPI app
BASE_URL="http://localhost:8000"

# Create a session
SESSION_ID="Back%20to%20school%202024-2025"
curl -X POST "$BASE_URL/sessions" -H "Content-Type: application/json" -d "{\"id\": \"$SESSION_ID\"}"
curl -X 'POST' \
  "$BASE_URL/sessions?id=$SESSION_ID" \
  -H 'accept: application/json' \
  -d ''
# Add three rooms to the session
ROOM_NAMES=("A00-117A" "B00-133A" "E00-201A")
for ROOM_NAME in "${ROOM_NAMES[@]}"; do
  curl -X POST "$BASE_URL/sessions/$SESSION_ID/rooms" -H "Content-Type: application/json" -d "{\"name\": \"$ROOM_NAME\"}"
done

# Add two players to the first room
ROOM_NAME="A00-117A"
PLAYERS=("Pikachu" "Charizard" "Bulbasaur" "Squirtle" "Jigglypuff")
for PLAYER_NAME in "${PLAYERS[@]}"; do
  curl -X POST "$BASE_URL/sessions/$SESSION_ID/rooms/$ROOM_NAME/players" -H "Content-Type: application/json" -d "{\"name\": \"$PLAYER_NAME\", \"missions_passed\":12}"
done

ROOM_NAME="B00-133A"
PLAYERS=("Meowth" "Eevee" "Mewtwo" "Gengar" "Snorlax" "Lucario" "Greninja" "Gardevoir" "Dragonite" "Arcanine")
for PLAYER_NAME in "${PLAYERS[@]}"; do
  curl -X POST "$BASE_URL/sessions/$SESSION_ID/rooms/$ROOM_NAME/players" -H "Content-Type: application/json" -d "{\"name\": \"$PLAYER_NAME\", \"missions_passed\":14}"
done

ROOM_NAME="E00-201A"
PLAYERS=("Blastoise" "Venusaur" "Machamp" "Alakazam" "Lapras" "Psyduck" "Magikarp" "Umbreon" "Scyther" "Tyranitar" "Heracross" "Salamence" "Metagross" "Garchomp" "Infernape")
for PLAYER_NAME in "${PLAYERS[@]}"; do
  curl -X POST "$BASE_URL/sessions/$SESSION_ID/rooms/$ROOM_NAME/players" -H "Content-Type: application/json" -d "{\"name\": \"$PLAYER_NAME\", \"missions_passed\":14}"
done

echo "Setup complete."
