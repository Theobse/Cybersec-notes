# Write-up – TryHackMe **Whiterose**

**Nom de la room :** Whiterose  
**Lien :** 
**Niveau :** Facile  
**Description :** Yet another Mr. Robot themed challenge.  

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
