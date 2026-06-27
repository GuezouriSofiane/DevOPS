# Guide de Dépannage (Troubleshooting)

Ce document décrit les principaux incidents pouvant être rencontrés lors du déploiement de l'application ainsi que les étapes de diagnostic et de résolution.

---

##  Cas particulier rencontré sous Windows (Docker Desktop)

### Symptôme

Les modifications apportées à la configuration Apache (`vhost.conf`) ne sont pas prises en compte ou les routes `/api/*` retournent une erreur **404**, malgré un redémarrage des conteneurs.

### Cause possible

Sous Windows (Docker Desktop et Git Bash/MSYS), le montage des volumes peut parfois être mal interprété ou mis en cache, empêchant Apache de charger la dernière version de la configuration.

### Vérifications

1. Vérifier les logs Apache :

```bash
docker compose logs apache
```

2. Reconstruire complètement les conteneurs :

```bash
docker compose down
docker compose up -d --build
```

3. Vérifier que le fichier `apache/vhost.conf` est bien monté dans le conteneur.

---

#  Cas 1 — Le frontend fonctionne mais `/api/health` retourne une erreur

## Symptôme

Le frontend est accessible via :

```text
http://localhost/
```

mais l'API retourne une erreur **404**, **502** ou **503**.

## Vérifications

### 1. Vérifier les logs Apache

```bash
docker compose logs apache
```

Rechercher les erreurs liées au reverse proxy.

### 2. Vérifier les logs du Backend

```bash
docker compose logs backend
```

Vérifier que l'application Flask est bien démarrée.

### 3. Vérifier la configuration du Reverse Proxy

Contrôler le fichier :

```text
apache/vhost.conf
```

Les directives suivantes doivent être présentes :

```apache
ProxyPass /api/ http://backend:8000/
ProxyPassReverse /api/ http://backend:8000/
```

### 4. Vérifier les modules Apache

Les modules suivants doivent être activés :

* `mod_proxy`
* `mod_proxy_http`

### 5. Vérifier le nom du service Backend

Dans `docker-compose.yml`, le service doit s'appeler :

```yaml
backend:
```

Apache utilise ce nom pour communiquer avec le conteneur.

### 6. Vérifier le port interne du Backend

Le backend doit écouter sur :

```text
0.0.0.0:8000
```

---

#  Cas 2 — `/api/db-check` ne fonctionne pas

## Symptôme

Le backend est accessible, mais la connexion à PostgreSQL échoue.

## Vérifications

### 1. Vérifier les variables d'environnement

Les variables suivantes doivent être correctement définies :

* `POSTGRES_DB`
* `POSTGRES_USER`
* `POSTGRES_PASSWORD`
* `POSTGRES_HOST`

Le nom de l'hôte doit être :

```text
postgres
```

et non :

```text
localhost
```

### 2. Vérifier que PostgreSQL est démarré

```bash
docker compose ps
docker compose logs postgres
```

### 3. Vérifier le nom DNS du service PostgreSQL

Dans `docker-compose.yml`, le service doit être nommé :

```yaml
postgres:
```

### 4. Tester la communication réseau

Depuis le conteneur Backend :

```bash
docker compose exec backend ping postgres
```

### 5. Tester la connexion depuis le Backend

```bash
docker compose exec backend sh
```

---

#  Cas 3 — L'application fonctionne localement mais pas depuis une autre machine

## Symptôme

L'application fonctionne sur le serveur, mais elle est inaccessible depuis un autre ordinateur.

## Vérifications

### 1. Vérifier le port exposé

Seul Apache doit exposer le port :

```yaml
ports:
  - "80:80"
```

### 2. Vérifier le binding réseau

Apache doit écouter sur :

```text
0.0.0.0:80
```

et non :

```text
127.0.0.1:80
```

### 3. Vérifier le pare-feu

Autoriser le trafic entrant sur le port TCP 80.

**Windows**

* Windows Defender Firewall

**Linux**

```bash
sudo ufw allow 80/tcp
```

### 4. Vérifier la configuration Apache

Contrôler le fichier :

```text
apache/vhost.conf
```

et vérifier les directives `ProxyPass` et `ProxyPassReverse`.

### 5. Tester la connectivité

Depuis une autre machine :

```bash
curl http://<IP_DU_SERVEUR>/
```

ou

```bash
nc -zv <IP_DU_SERVEUR> 80
```

---

#  Commandes utiles

## Afficher les conteneurs

```bash
docker compose ps
```

## Afficher tous les logs

```bash
docker compose logs
```

## Afficher les logs d'un service

```bash
docker compose logs apache
docker compose logs backend
docker compose logs postgres
```

## Entrer dans un conteneur

```bash
docker compose exec backend sh
```

## Redémarrer l'environnement

```bash
docker compose down
docker compose up -d --build
```

## Vérifier les endpoints

```bash
curl http://localhost/
curl http://localhost/api/health
curl http://localhost/api/version
curl http://localhost/api/db-check
```

## Vérifier les ports ouverts

### Linux

```bash
ss -tulpn
```

### Windows

```powershell
netstat -ano
```
---

# Cas 4 — [Bonus / Sécurité] Le conteneur Backend s'exécute toujours en `root` ou ne démarre plus après le passage en utilisateur non-root

## Symptôme

Après avoir modifié le `Dockerfile` afin d'exécuter l'application avec un utilisateur non privilégié (`flaskuser`), le backend ne démarre plus ou le conteneur s'exécute toujours avec l'utilisateur `root`.

Le script `check.sh` peut également afficher :

```text
[KO] Backend health error
```

---

## Vérifications

### 1. Reconstruire complètement l'image sans utiliser le cache Docker

Sous Windows, Docker Desktop peut conserver une ancienne image en cache.

```bash
docker compose down
docker compose build --no-cache backend
docker compose up -d
```

---

### 2. Vérifier l'utilisateur exécutant l'application

Depuis le conteneur Backend :

```bash
docker compose exec backend whoami
```

Résultat attendu :

```text
flaskuser
```

Si le résultat est :

```text
root
```

cela signifie que l'instruction `USER flaskuser` n'est pas correctement appliquée dans le `Dockerfile`.

---

### 3. Vérifier les erreurs liées aux dépendances Python

Si les logs affichent une erreur du type :

```text
ModuleNotFoundError: No module named 'flask'
```

cela signifie généralement que les dépendances Python ne sont pas accessibles par l'utilisateur non privilégié.

Vérifier les logs :

```bash
docker compose logs backend
```

**Solution :**

Installer les dépendances avec `pip` avant de passer à l'utilisateur `flaskuser`, puis utiliser :

```dockerfile
USER flaskuser
```

uniquement à la fin du `Dockerfile`.

---

# Cas 5 — [Bonus / Kubernetes] Erreur `dial tcp [::1]:8080: connectex` lors des tests de la NetworkPolicy

## Symptôme

Lors de l'exécution d'une commande `kubectl`, le terminal affiche :

```text
Unable to connect to the server: dial tcp [::1]:8080: connectex:
No connection could be made because the target machine actively refused it.
```

---

## Cause possible

Cette erreur indique qu'aucun cluster Kubernetes n'est actuellement démarré.

Le projet fonctionne avec **Docker Compose**.

Le fichier :

```text
kubernetes/postgres-networkpolicy.yaml
```

est uniquement fourni comme **bonus**.

---

## Vérifications

### 1. Vérifier que Kubernetes est bien démarré

Si vous souhaitez tester la NetworkPolicy, démarrez un cluster Kubernetes (Minikube ou Kind) puis vérifiez :

```bash
kubectl cluster-info
```

Si aucun cluster n'est lancé, cette commande retournera une erreur.

---

### 2. Vérifier l'isolation réseau sous Docker Compose

Même sans Kubernetes, l'isolation est assurée grâce au réseau Docker privé :

```yaml
networks:
  app_net:
    driver: bridge
```

---

### 3. Vérifier que le Backend peut joindre PostgreSQL

Depuis le conteneur Backend :

```bash
docker compose exec backend nc -zv postgres 5432
```

Résultat attendu :

```text
postgres (172.x.x.x:5432) open
```

---

### 4. Vérifier que PostgreSQL n'est pas accessible depuis l'hôte

Depuis la machine locale :

```bash
curl http://localhost:5432
```

ou

```bash
nc -zv localhost 5432
```

Résultat attendu :

```text
Connection refused
```

ou

```text
Failed to connect
```

Cela confirme que PostgreSQL n'est pas exposé publiquement et que l'isolation réseau est correctement appliquée.

---


