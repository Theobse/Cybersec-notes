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

