# Application de Gestion de tâches - *Back-end Flask*
Ce script **python** est un back-end pour un site web de _gestion de tâches_.
Developpé avec le framework **Flask**, il implemente plusieurs APIs pour celui-ci.

Le script est lancé tout simplement et ne prend pas d'argument.
(*Ex: $ python main.py*)

**Rq**: Chaque route est prefixée de **http://{host}:{port}** avec {host} et {port} les hotes et ports ouverts pour le site.
        _Exp_: par défaut, le login est: [http://127.0.0.1:5000/api/login](http://127.0.0.1:5000/api/login)

# I - Login
- **methode :** POST

## Connexion:
- **Route :** _/api/login_
- **données attendus :** username, password
- **Réponses :**
  * **Succès:**
    ```
        {
          "message": "OK: Connected"
        }
    ```
      > Code : 200
  * **Echecs**:
      - _données recus vide_:
        ``` 
          {
            "error": "Bad Request: Invalid input"
          } 
        ```
          > Code : 400
      - _Un autre utilisateur est deja connecte_:
        ```
          {
            "error": "Forbidden: An user is already connected"
          }
        ```
          > Code: 403

      - _Utilisateur non trouve_:
        ```
          {
            "error" : "User not found"
          }
        ```
          > Code: 404

      - _Mot de passe incorrect_:
        ```
          {
            "error" : "Unauthorized: wrong password"
          }
        ```
          > Code: 401

## Deconnexion:
- **Route :** _/api/disconnection_
- **Réponses :**
  * **Succès:**
      *Aucun donnée renvoye*
      > Code: 200
  * **Echec**:
      - _Aucun utilisateur connecte_:
        ```
          {
            "error": "Forbidden: No user connected"
          }
        ```
          > Code: 403
      
-------------------------------------------------------------
# II - Gestion des utilisateurs
## 1 - Creation d'utilisateur:
- **Route :** _/api/users_
- **Methode :** POST
- - **données attendus :** username, password
- **Réponses :**
  * **Succès:**
    ```
      {
        "id" : new_id,
        "username" : username,
        "password" : password
      }
    ```
      > Code: 201
  * **Echecs**:
    - _donnée recu vide_:
        ```
          {
            "error": "Bad Request: Invalid input"
          }
        ```
          > Code : 400
    - _Username deja existant_:
        ```
          {
            "error": "Conflict: User already exists"
          }
        ```
          > Code: 409

## 2 - Acces aux données d'un utilisateur:
- **Route :** _/api/users/<user_id>_
- **Methode :** GET
- **Réponses :**
  * **Succès:**
    ```
      {
        "id" : user_id,
        "username" : username,
        "password" : password
      }
    ```
      > Code: 200
  * **Echec**: *Utilisateur non trouve*
    ```
      {
        "error": "User not found"
      }
    ```
      > Code: 404
## 2 - Acces aux données de tous les utilisateurs:
- **Route :** _/api/users/_
- **Methode :** GET
- - **Réponses :**
      ```
        Liste des données:
          {
            "id" : user_id,
            "username" : username,
            "password" : password
          }
      ```
          *Ps: Si aucun dans la base de données, alors vide*
        > Code: 200
    
## 3 - Mise a jour des données des utlisateurs:
- **Route :** _/api/users/<user_id>_
- **Methode :** PUT
- **données attendus**: "username" et/ou "password" (Seul les données recus sont changes)
- **Réponses :**
  * **Succès:**
        {
          "id" : user_id,
          "username" : new_username,
          "password" : new_password
        }
        > Code: 200
  * **Echecs**:
    - _Les données attendus sont tous vides_:
      ```
        {
          "error" : "Bad Request: Invalid input"
        }
      ```
      > Code: 400
    - _Utilisateur non trouve_:
      ```
        {
          "error" : "User not found"
        }
      ```
        > Code: 404

## 4 - Suppression d'un utilisateur:
- **Route :** _/api/users/<user_id>_
- **Methode :** DELETE
- **Réponses :**
  * **Succès:**
      *Aucun donnée renvoye*
      > Code: 204
  * **Echec :** *Utilisateur non trouve*
    ``` 
      {
        "error": "User not found"
      } 
    ```
    > Code: 404
-------------------------------------------------------------
# III - Gestion des tâches 
## 1 - Creation de tâche:
- **Route :** _/api/task/<user_id>_
- **Methode :** POST
- **données attendus :** "description" et "date"
- **Réponses :**
  * **Succès:**
    ```
      {
        "id" : task_id,
        "description" : task_desc,
        "date" : task_date,
        "user_id" : user_id
      }
    ```
    > Code: 201
  * **Echecs :**
    - _données recus vide_:
      ```
        {
          "error" : "Bad Request: Invalid input"
        }
      ```
      > Code: 400
    - _Utilisateur non trouve_:
      ```
      {
        "error" : "User not found"
      }
      ```
      > Code: 404

## 2 - Acces aux données d'une tâche specifique d'un utilisateur
- **Route :** /api/task/<user_id>/<task_id>
- **Methode :** GET
- **Réponses :**
  * **Succès:**
    ```
      {
        "id" : task_id,
        "description" : task_desc,
        "date" : task_date,
        "user_id" : user_id
      }
    ```
    > Code: 200
  * **Echecs :**
    - _Utilisateur non trouve_:
      ```
      {
        "error" : "User not found"
      }
      ```
      > Code: 404
    - _tâche non trouvee_:
      ```
      {
        "error" : "Task not found"
      }
      ```
      > Code: 404

## 2 - Acces aux données de toutes les tâches d'un utilisateur
- **Route :** /api/task/<user_id>
- **Methode :** GET
- **Réponses :**
  * **Succès:**
    ```
      Liste de :
      {
        "id" : task_id,
        "description" : task_desc,
        "date" : task_date,
        "user_id" : user_id
      }
      avec user_id: tous les memes.
    ```
    > Code: 200
  * **Echecs :**
    - _Utilisateur non trouve_:
      ```
      {
        "error" : "User not found"
      }
      ```
      > Code: 404

## 2 - Acces aux données de toutes les tâches
- **Route :** /api/task
- **Methode :** GET
- **Réponses :**
  * **Succès:**
    ```
      Liste de :
      {
        "id" : task_id,
        "description" : task_desc,
        "date" : task_date,
        "user_id" : user_id
      }
    ```
    *ps: Si la base de données est vide alors liste vide*
    > Code: 200

## 3 - Mis a jour des données d'une tâche specifique
- **Route :** /api/task/<user_id>/<task_id>
- **Methode :** PUT
- **données attendus :** "description" et/ou "date"
- **Réponses :**
  * **Succès :**
      ```
        {
          "id" : task_id,
          "description" : new_task_desc,
          "date" : new_task_date,
          "user_id" : user_id
        }
      ```
      > Code: 200
  * **Echecs :**
    - _données recus vide_:
      ```
        {
          "error" : "Bad Request: Invalid input"
        }
      ```
      > Code: 400
    - _Utilisateur non trouve_:
      ```
      {
        "error" : "User not found"
      }
      ```
      > Code: 404
    - _tâche non trouvee_
      ```
      {
        "error" : "Task not found"
      }
      ```
      > Code: 404

## 4 - Suppression de tâches specifiques
- **Route :** /api/task/<user_id>/<task_id>
- **Methode :** DELETE
- **Réponses**:
  * **Succès :**
    *Aucun donnée renvoye*
    > Code: 204
  * **Echecs**:
    - _Utilisateur non trouve_:
      ```
      {
        "error" : "User not found"
      }
      ```
      > Code: 404
    - _tâche non trouvee_
      ```
      {
        "error" : "Task not found"
      }
      ```
      > Code: 404

## 4 - Suppression de toutes les tâches d'un utilisateurs
- **Route :** /api/task/<user_id>
- **Methode :** DELETE
- **Réponses**:
  * **Succès :**
    *Aucun donnée renvoye*
    > Code: 204
  * **Echecs**:
    - _Utilisateur non trouve_:
      ```
      {
        "error" : "User not found"
      }
      ```
      > Code: 404


-------------------------------------------------------------------------------------------

## **_PS_:**
  - Tous les données attendus et envoyés sont tous sous formes de data *JSON*
  - Par défaut, le host est [http://localhost](http://127.0.0.1) et le port par defaut est **5000** .Mais pour changer celui-ci, changer seulement les valeurs des variables **host** et **port** du script _main.py_ (ces variables se trouvent au _7 et 8eme ligne_ du code. )
  - La *suppression d'un utilisateur _efface toutes ses tâches_* dans la base de données.
  - Certaines erreurs ne peuvent ne pas figurer dans la liste d'en haut mais generer par defaut par **Flask**.