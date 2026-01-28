#!/bin/bash

# Разрешаем X11
xhost +local:docker

# Запускаем контейнер
docker-compose up --build

# Закрываем X11
xhost -local:docker
