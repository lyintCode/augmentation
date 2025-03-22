#!/bin/bash

echo -e "\e[42m\e[97m Запрос пароля sudo \e[0m"
sudo true && echo "Sudo доступ получен" || exit

echo -e "\e[42m\e[97m Установка зависимостей для работы приложения \e[0m"
sudo apt update && sudo apt install -y jq python3-pip python3-venv python3-dev curl apt-transport-https ca-certificates software-properties-common

echo -e "\e[42m\e[97m Скачивание ключа docker repo \e[0m"
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && echo "OK"

echo -e "\e[42m\e[97m Включение docker repo \e[0m"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && echo "OK"

echo -e "\e[42m\e[97m Установка Docker \e[0m"
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io

echo -e "\e[42m\e[97m Включение службы docker \e[0m"
sudo systemctl start docker
sudo systemctl enable docker
sudo docker --version

echo -e "\e[42m\e[97m Добавление $USER в группу docker \e[0m"
sudo usermod -aG docker $USER 
echo -e "\n\nПожалуйста, выполните 'newgrp docker' вручную или перезапустите терминал\n\n"

echo -e "\e[42m\e[97m Скачивание docker compose \e[0m"
sudo curl -L "https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && echo "OK"
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
docker completion bash | sudo tee /etc/bash_completion.d/docker-compose
source /etc/bash_completion.d/docker-compose