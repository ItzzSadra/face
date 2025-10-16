#!/bin/bash
# ----------------------------
# Run "production-like" attendance system
# ----------------------------

GREEN="\033[0;32m"
RESET="\033[0m"

# Start backend
echo -e "${GREEN}Starting backend...${RESET}"
cd backend || exit
python3 main.py &
BACKEND_PID=$!
cd ..

sleep 2  # small delay to let backend start

# Start frontend (Vite)
echo -e "${GREEN}Starting frontend ...${RESET}"
cd frontend || exit
pnpm install --frozen-lockfile
pnpm dev &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}All services are running.${RESET}"
echo -e "${GREEN}Backend PID: $BACKEND_PID${RESET}"
echo -e "${GREEN}Frontend PID: $FRONTEND_PID${RESET}"

# Cleanup on Ctrl+C
cleanup() {
    echo -e "\n${GREEN}Stopping services...${RESET}"
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

trap cleanup SIGINT

# Keep script alive
wait
