#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
echo "=========================================================="
echo "Публикация проекта ClothesHelper на GitHub"
echo "Репозиторий: https://github.com/dashando/GlothesHelper.git"
echo "=========================================================="
echo ""
echo "Если запросит пароль (Password), вставьте ваш GitHub Personal Access Token (PAT)."
echo ""
git push -u origin main
echo ""
echo "=========================================================="
echo "Готово! Нажмите любую клавишу для закрытия окна..."
read -n 1 -s
