#!/bin/bash
python autenticacionMicroservicio/main.py &
python evaluacionMicroservicio/main.py &
python modeloCalidadMicroservicio/main.py &
python riesgoMicroservicio/main.py &
python softwareMicroservicio/main.py &
wait