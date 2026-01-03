# Write-up – TryHackMe **Whiterose**

**Nom de la room :** Whiterose  
**Lien :** [https://tryhackme.com/room/anthem](https://tryhackme.com/room/anthem)  
**Niveau :** Facile  
**Description :** Yet another Mr. Robot themed challenge.  

---

<img width="831" height="507" alt="image" src="https://github.com/user-attachments/assets/6f175acf-1064-4fba-8dec-4ef9ee972cd2" />

Sur le port 80, on a un site web.

Quand on visite la page web on est redirigé vers 'cyprusbank.thm'. On l'ajoute dans le fichier /etc/hosts et on rafraichit la page.
<img width="878" height="225" alt="image" src="https://github.com/user-attachments/assets/b5138eab-3ff2-4da3-b4bf-76b9c35f9e3e" />

Il est indiqué que le site en maintenance. Je me dis tout de suite qu'il peut y avoir un sous-domaine comme 'dev.cyprusbank.thm' ou autres, sur lequel il y aurait le site en phase de développement (avant mise en production). Avant cela, j'effectue une rapide énumération du site web avec les outils de développemnt du navigateur.

<img width="946" height="162" alt="image" src="https://github.com/user-attachments/assets/1df336a4-535e-41b3-9c4f-733efbdde6d1" />
Quand on ouvre le site, que 3 ressources sont chargés dont le html de la page d'accueil.

Le html du la page d'accueil ne contient aucun script js, aucune redirection vers une autre page du site web, aucun commentaires. Pas de fichier /robots.txt également.
<img width="958" height="254" alt="image" src="https://github.com/user-attachments/assets/f82e91f9-1568-41c0-859c-3abc9e3ffff9" />

Le scan rapide d'énumération web avec gobuster ne donne rien..
<img width="611" height="347" alt="image" src="https://github.com/user-attachments/assets/f9bfb674-7753-4481-9e4a-d9e9324bebfd" />

Je décide donc de chercher s'il y a pas un sous-domain avec un vhost:
<img width="1158" height="391" alt="image" src="https://github.com/user-attachments/assets/a3968b74-90c4-4fa5-8e24-3e210ca359f4" />

On trouve un vhost intéressant : admin. Ajoutons le au /etc/hosts puis rendant nous sur le site admin.cyprusbank.thm.
<img width="1913" height="595" alt="image" src="https://github.com/user-attachments/assets/b4c265e3-cdf4-499e-95bd-ed4e43cbc23d" />

On arrive sur une page de login. Dans l'énoncé du challenge on nous donne les credentials d'un utilisateur : 'Olivia Cortez:olivi8'. On peut mainteannt se connecter sur le site.
<img width="1317" height="764" alt="image" src="https://github.com/user-attachments/assets/dc8b1a78-cf81-46a8-9a09-a39e165b26e1" />

L'utilisateur Olivia Cortez a des droits limités sur le site car on ne peut pas accéder à la page /settings. 
<img width="1335" height="254" alt="image" src="https://github.com/user-attachments/assets/9ff1c639-4c06-4f7a-a766-c5745ea205c7" />

En se rendant sur /messages (http://admin.cyprusbank.thm/messages/?c=5), on peut observer qu'il y a un paramètre 'c' dans l'url. Peut-être qu'on a une IDOR si l'on peut changer la valeur du paramètre et accéder à de nouvelles information?

En mettant la valeur du paramètre c à 20, on peut afficher plus de messages. Cela permet aussi d'obtenir les credentials de l'utilisateur Gayle Bev (Gayle Bev:p~]P@5!6;rs558:q).
<img width="1306" height="763" alt="image" src="https://github.com/user-attachments/assets/58700f39-3a1c-4d07-a361-1ebd86364d0f" />

On peut maintenant se déconnecter et se connecter sur le compte de Gayle Bev. On a maintenantn accès au numéro de téléphone des utilisateurs et à l'endpoint 'settings' :
<img width="1314" height="387" alt="image" src="https://github.com/user-attachments/assets/f1857f7b-ad49-47a2-935d-9444978db317" />

Sur cette endpoint, nous pouvons y définir les mots de passe des clients. En effectuant un test, on remarque que les mots de passe sont affichés. Cela attire immédiatement l'attention sur les vulnérabilités XSS ou SSTI.
<img width="1302" height="270" alt="image" src="https://github.com/user-attachments/assets/8469acb1-dd86-441b-807c-0183bded15f0" />

Avec Burp Suite, j'intercèpte la requête de mise à jour de mot de passe et l'envoie la requête dans le repeater.
<img width="1248" height="339" alt="image" src="https://github.com/user-attachments/assets/edacb276-9c6d-4cbf-99d3-4f95f873bd86" />

Si on modifie la requête en retirant le paramètre password, on obtient un message d'erreur :
<img width="1249" height="510" alt="image" src="https://github.com/user-attachments/assets/38d92b8e-ac37-4116-876d-28deec32b163" />

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

<body>
<pre>ReferenceError: /home/web/app/views/settings.ejs:14<br> &nbsp; &nbsp;12| &nbsp; &nbsp; &nbsp; &nbsp; &lt;div class=&quot;alert alert-info mb-3&quot;&gt;&lt;%= message %&gt;&lt;/div&gt;<br> &nbsp; &nbsp;13| &nbsp; &nbsp; &nbsp; &lt;% } %&gt;<br> &gt;&gt; 14| &nbsp; &nbsp; &nbsp; &lt;% if (password != -1) { %&gt;<br> &nbsp; &nbsp;15| &nbsp; &nbsp; &nbsp; &nbsp; &lt;div class=&quot;alert alert-success mb-3&quot;&gt;Password updated to &#39;&lt;%= password %&gt;&#39;&lt;/div&gt;<br> &nbsp; &nbsp;16| &nbsp; &nbsp; &nbsp; &lt;% } %&gt;<br> &nbsp; &nbsp;17| &nbsp; &nbsp; &nbsp; &lt;% if (typeof error != &#39;undefined&#39;) { %&gt;<br><br>password is not defined<br> &nbsp; &nbsp;at eval (&quot;/home/web/app/views/settings.ejs&quot;:27:8)<br> &nbsp; &nbsp;at settings (/home/web/app/node_modules/ejs/lib/ejs.js:692:17)<br> &nbsp; &nbsp;at tryHandleCache (/home/web/app/node_modules/ejs/lib/ejs.js:272:36)<br> &nbsp; &nbsp;at View.exports.renderFile [as engine] (/home/web/app/node_modules/ejs/lib/ejs.js:489:10)<br> &nbsp; &nbsp;at View.render (/home/web/app/node_modules/express/lib/view.js:135:8)<br> &nbsp; &nbsp;at tryRender (/home/web/app/node_modules/express/lib/application.js:657:10)<br> &nbsp; &nbsp;at Function.render (/home/web/app/node_modules/express/lib/application.js:609:3)<br> &nbsp; &nbsp;at ServerResponse.render (/home/web/app/node_modules/express/lib/response.js:1039:7)<br> &nbsp; &nbsp;at /home/web/app/routes/settings.js:27:7<br> &nbsp; &nbsp;at runMicrotasks (&lt;anonymous&gt;)</pre>
</body>
</html>

L’application a crashé en traitant ta requête. Ici il ne s'agit pas d'un problème réseau ni d’authentification, mais un bug applicatif.  

En analysant les headers, on confirme que l’app utilise :
- Nginx 1.14.0 (reverse proxy)
- Node.js / Express
- Templates EJS
C’est une fuite de stack exploitable pour rechercher des CVE ou cibler des vulnérabilités spécifiques Node / Express / EJS.

L'erreur nous permet de savoir le templates utilisé par EJS (Embedded JavaScript) pour afficher le mot de passe sur la page après update grâce aux balises '<%  %>'. Sur internet on trouve facilement de nombreuses ressources sur la faille SSTI avec EJS, dont ces ressources parlant de la CVE-2022-29078 (ejs server side template injection rce) :
- https://github.com/mde/ejs/issues/720
- https://eslam.io/posts/ejs-server-side-template-injection-rce/

<img width="621" height="376" alt="image" src="https://github.com/user-attachments/assets/bb87c309-cb66-4ad6-ba3f-4cd645bdcf4e" />

<img width="531" height="90" alt="image" src="https://github.com/user-attachments/assets/325a006a-abb1-4804-a828-b8b84af44acb" />

