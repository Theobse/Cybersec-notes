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
**Objectif**  
Identifier la surface d’attaque :
- ports ouverts
- services exposés
- système d’exploitation

Scan réseau :
'''bash
nmap -sC -sV -A -p- -T4 IP_CIBLE
'''
