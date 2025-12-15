# Write-up – TryHackMe **Anthem**

**Nom de la room :** Anthem  
**Lien :** [https://tryhackme.com/room/anthem](https://tryhackme.com/room/anthem)  
**Niveau :** Facile  
**OS cible :** Windows  
**Description :** Exploit a Windows machine in this beginner level challenge.  

---

## 🎯 Objectif général

* Identifier les services exposés
* Explorer le site web
* Collecter des informations sensibles
* Trouver les flags web
* Accéder à la machine via RDP
* Obtenir `user.txt` et `root.txt`

---

# Part 1 – Reconnaissance

## Test de connectivité

```bash
ping -c 4 10.80.183.26
```

La machine ne répond pas au protocole ICMP.
On utilisera l’option `-Pn` avec Nmap.

---

## Scan Nmap

```bash
nmap -A -p- -T4 -Pn 10.80.183.26
```

### Résultats

* **80/tcp** → HTTP (Microsoft HTTPAPI 2.0)
* **3389/tcp** → RDP
* **OS détecté :** Windows Server / Windows 10

---

## Résolution DNS locale

Ajout dans `/etc/hosts` :

```
10.80.183.26    WIN-LU09299160F anthem.com
```

---

## Accès au site web

```
http://anthem.com
```

Le site affiche plusieurs articles publics.

---

## robots.txt

Contenu intéressant :

```txt
Disallow: /bin/
Disallow: /config/
Disallow: /umbraco/
Disallow: /umbraco_client/
```

Une chaîne ressemblant à un mot de passe est également présente mais **volontairement masquée** dans ce write-up.

---

## CMS utilisé

Les répertoires découverts indiquent l’utilisation du CMS **Umbraco**.

---

## Nom de domaine

**anthem.com**

---

## Nom de l’administrateur

L’article *“A cheers to our IT department”* contient un poème connu permettant d’identifier l’administrateur du site.

**Administrateur :** Solomon Grundy

---

## Email de l’administrateur

Un article fournit un exemple d’adresse email :

```
JD@anthem.com
```

Par déduction, l'email de l'administrateur est :

```
sg@anthem.com
```

---

# Part 2 – Flags Web

> ⚠️ Les flags sont volontairement masqués.

---

## Flag 1

Trouvé dans le code source de l’article **We are hiring**.

**Flag 1 :** `THM{REDACTED}`

---

## Flag 2

Trouvé dans le code source de la page principale.

**Flag 2 :** `THM{REDACTED}`

---

## Flag 3

Trouvé dans le code source de la page auteur **Jane Doe**.

**Flag 3 :** `THM{REDACTED}`

---

## Flag 4

Trouvé dans le code source de l’article **A cheers to our IT department**.

**Flag 4 :** `THM{REDACTED}`

---

# Part 3 – Accès à la machine

## Accès au panel Umbraco

```
http://anthem.com/umbraco/
```

Une page de connexion Umbraco est accessible.

Les identifiants utilisés sont **intentionnellement masqués** dans ce write-up.

Connexion réussie au panneau d’administration.

---

## Version du CMS

```
Umbraco version 7.15.4
```

---

## Connexion RDP

Connexion RDP effectuée avec les identifiants précédemment découverts
(**adresse IP, utilisateur et mot de passe masqués**).

```shell
xfreerdp3 /v:IP_CIBLE /u:NOM_UTILISATEUR /p:MOT_DE_PASSE
```

---

## user.txt

Le fichier `user.txt` est présent sur le bureau de l’utilisateur standard.

**Flag user.txt récupéré** (`THM{REDACTED}`)

---

## Élévation de privilèges

Un dossier caché `backup` est présent à la racine de `C:\`.

Après modification des permissions, un fichier contenant des informations sensibles est lisible.

Le mot de passe administrateur est récupéré

---

## Accès administrateur

Accès au profil :

```
C:\Users\Administrator
```

Le fichier `root.txt` est présent sur le bureau.

**Flag root.txt récupéré** (`THM{REDACTED}`)

---

# Conclusion

Cette room met en pratique :
* Analyse web et OSINT
* Lecture de code source HTML
* Identification de CMS
* Accès RDP
* Gestion des permissions Windows
