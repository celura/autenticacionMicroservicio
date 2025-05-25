Write-Host "Iniciando softwareMicroservicio..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "softwareMicroservicio/main.py"

Write-Host "Iniciando autenticacionMicroservicio..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "autenticacionMicroservicio/main.py"

Write-Host "Iniciando modeloCalidadMicroservicio..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "modeloCalidadMicroservicio/main.py"

Write-Host "Iniciando evaluacionMicroservicio..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "evaluacionMicroservicio/main.py"

Write-Host "Iniciando riesgoMicroservicio..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "riesgoMicroservicio/main.py"

Write-Host "Todos los microservicios han sido iniciados."
