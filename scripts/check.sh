#!/bin/bash

echo " Démarrage des vérifications "


echo -n "Vérification des conteneurs... "
if [ $(docker compose ps -q | wc -l) -eq 4 ]; then
    echo "[OK]"
else
    echo "[KO] Tous les conteneurs ne sont pas lancés"
fi

echo -n "Vérification du port 80 (Apache)... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
    echo "[OK] Apache répond"
else
    echo "[KO] Apache injoignable"
fi

echo -n "Vérification de /api/health... "
if curl -s http://localhost/api/health | grep -q '"status":"ok"'; then
    echo "[OK] Backend health endpoint reachable"
else
    echo "[KO] Backend health error"
fi

echo -n "Vérification de /api/db-check... "
if curl -s http://localhost/api/db-check | grep -q '"database":"connected"'; then
    echo "[OK] Database connection successful"
else
    echo "[KO] Database connection failed"
fi

echo "Fin des vérifications"