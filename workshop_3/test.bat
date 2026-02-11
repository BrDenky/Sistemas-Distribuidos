@echo off
echo ============================================================
echo Workshop 3 - Testing Script
echo ============================================================
echo.
echo This script will help you test all three parts of the workshop.
echo Make sure you have Python 3.x and pyzmq installed.
echo.
echo Checking Python installation...
python --version
echo.
echo Checking pyzmq installation...
python -c "import zmq; print('pyzmq version:', zmq.pyzmq_version())" 2>nul
if %errorlevel% neq 0 (
    echo pyzmq is NOT installed!
    echo Please run: pip install pyzmq
    pause
    exit /b 1
)
echo.
echo ============================================================
echo All dependencies are installed!
echo ============================================================
echo.
echo Choose a test to run:
echo.
echo 1. Part 1: RMI - Complex Number Manager
echo 2. Part 2: Publisher-Subscriber
echo 3. Part 3: Pipeline with Broker
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto part1
if "%choice%"=="2" goto part2
if "%choice%"=="3" goto part3
if "%choice%"=="4" goto end
echo Invalid choice!
pause
exit /b 1

:part1
echo.
echo ============================================================
echo Part 1: RMI - Complex Number Manager
echo ============================================================
echo.
echo Instructions:
echo 1. This window will start the SERVER
echo 2. Open a NEW terminal and run: python part1_rmi\client_complex.py
echo 3. Use the client menu to test operations
echo.
echo Starting server...
cd part1_rmi
python server_complex.py
goto end

:part2
echo.
echo ============================================================
echo Part 2: Publisher-Subscriber
echo ============================================================
echo.
echo Instructions:
echo 1. This window will start a WEATHER publisher
echo 2. Open NEW terminals for more publishers:
echo    - python part2_pubsub\publisher.py NEWS
echo    - python part2_pubsub\publisher.py SPORTS
echo    - python part2_pubsub\publisher.py FINANCE
echo 3. Open NEW terminals for subscribers:
echo    - python part2_pubsub\subscriber.py WEATHER
echo    - python part2_pubsub\subscriber.py NEWS SPORTS
echo    - python part2_pubsub\subscriber.py WEATHER NEWS SPORTS FINANCE
echo.
echo Starting WEATHER publisher...
cd part2_pubsub
python publisher.py WEATHER
goto end

:part3
echo.
echo ============================================================
echo Part 3: Pipeline with Broker
echo ============================================================
echo.
echo Instructions:
echo 1. This window will start the BROKER
echo 2. Open NEW terminals for workers:
echo    - python part3_pipeline\worker.py 1
echo    - python part3_pipeline\worker.py 2
echo    - python part3_pipeline\worker.py 3
echo 3. Open NEW terminals for sources:
echo    - python part3_pipeline\source.py 1
echo    - python part3_pipeline\source.py 2
echo    - python part3_pipeline\source.py 3
echo.
echo Starting broker...
cd part3_pipeline
python broker.py
goto end

:end
echo.
echo Exiting...
