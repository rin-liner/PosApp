@echo off

REM Backend dependencies installation
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

REM Frontend dependencies installation
echo Installing frontend dependencies...
cd frontend/client/my-app
npm install socket.io-client
cd ..

echo All dependencies installed successfully!
pause
