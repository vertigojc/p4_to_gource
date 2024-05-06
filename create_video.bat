setlocal EnableDelayedExpansion

REM Get the current date
for /F "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"

REM Combine to form the date string in the format YYYY-MM-DD
set "datestr=%YYYY%-%MM%-%DD%"

py src/p2g.py //Titan/Main/Content/... --exclude __External --logname gource_%datestr%.log --port ssl:54.153.125.13:1666 --user j.lindgren


REM Example command for running Gource on a custom log file.

gource --seconds-per-day 5 --auto-skip-seconds .5 --file-idle-time 0 --hide filenames,usernames --dir-name-depth 2 --title "Project Titan" --background-colour 000000 --bloom-multiplier 0.5 --bloom-intensity .5 --disable-bloom --max-file-lag .2 --max-user-speed 9999999 --user-friction 0.01 --start-date "2024-03-27 00:00:00" --disable-input -f -2560x1440 --output-framerate 30 --log-format custom gource_%datestr%.log --output-ppm-stream - | ffmpeg -y -r 30 -f image2pipe -vcodec ppm -i - -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart Project_Titan_%datestr%.mp4