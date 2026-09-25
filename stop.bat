@echo off
echo Stopping Karigar Connect servers...
powershell -Command "$ports = @(8000, 3000); foreach ($p in $ports) { $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue; foreach ($c in $conns) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } }"
echo Stopped all servers on ports 8000 and 3000.
pause
