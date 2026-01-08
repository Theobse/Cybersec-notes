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

# Reconnaissance (Recon)

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
Ports ouverts principaux :
| Port    | Service   | Intérêt |
|---------|-----------|---------|
| 22      | SSH       | Accès distant (post-exploitation) |
| 80     | HTTP   | Site web nginx 1.14.0 potiellement vulnérable |