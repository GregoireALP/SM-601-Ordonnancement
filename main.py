import sys
from collections import deque

class Ordonnancement:
    def __init__(self):
        self.tasks = {}  # Dictionnaire des tâches: {num: (durée, [prédécesseurs])}
        self.matrix = None  # Matrice d'adjacence du graphe
        self.n = 0  # Nombre de tâches réelles
        self.alpha = 0  # Tâche fictive début (0)
        self.omega = 0  # Tâche fictive fin (n+1)
        
    def lire_fichier(self, filename):
        """Lit un fichier texte contenant le tableau de contraintes"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            self.tasks = {}
            for line in lines:
                parts = list(map(int, line.strip().split()))
                task_num = parts[0]
                duration = parts[1]
                predecessors = parts[2:] if len(parts) > 2 else []
                self.tasks[task_num] = (duration, predecessors)
            
            self.n = len(self.tasks)
            self.omega = self.n + 1
            return True
        except FileNotFoundError:
            print(f"Erreur: Fichier {filename} non trouvé.")
            return False
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {e}")
            return False
    
    def construire_graphe(self):
        """Construit la matrice d'adjacence du graphe avec α et ω"""
        size = self.n + 2  # 0 à n+1
        self.matrix = [[None for _ in range(size)] for _ in range(size)]
        
        # Initialiser tous les arcs comme inexistants (None)
        for i in range(size):
            for j in range(size):
                self.matrix[i][j] = None
        
        # Ajouter les arcs depuis α (0) vers les tâches sans prédécesseurs
        for task in self.tasks:
            if not self.tasks[task][1]:  # Pas de prédécesseurs
                self.matrix[self.alpha][task] = 0
        
        # Ajouter les arcs entre les tâches
        for task in self.tasks:
            duration, predecessors = self.tasks[task]
            for pred in predecessors:
                self.matrix[pred][task] = self.tasks[pred][0]  # Durée de la tâche prédécesseur
        
        # Ajouter les arcs vers ω (n+1) depuis les tâches sans successeurs
        for i in range(size):
            has_successor = any(self.matrix[i][j] is not None for j in range(size))
            if i != self.omega and not has_successor and i in self.tasks:
                self.matrix[i][self.omega] = self.tasks[i][0]
    
    def afficher_graphe(self):
        """Affiche le graphe sous forme de triplets et la matrice"""
        if not self.matrix:
            print("Le graphe n'a pas encore été construit.")
            return
        
        print("\n*** Graphe d'ordonnancement ***")
        print(f"{self.n + 2} sommets (0 à {self.omega})")
        
        # Compter le nombre d'arcs
        arcs = []
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix)):
                if self.matrix[i][j] is not None:
                    arcs.append((i, j, self.matrix[i][j]))
        
        print(f"{len(arcs)} arcs")
        print("\nListe des arcs (triplets):")
        for arc in arcs:
            print(f"{arc[0]} -> {arc[1]} = {arc[2]}")
        
        # Afficher la matrice
        print("\nMatrice des valeurs:")
        size = len(self.matrix)
        
        # En-tête des colonnes
        print("   ", end="")
        for j in range(size):
            print(f"{j:4}", end="")
        print()
        
        # Lignes de la matrice
        for i in range(size):
            print(f"{i:2} ", end="")
            for j in range(size):
                val = self.matrix[i][j]
                print(f"{'   *' if val is None else val:4}", end="")
            print()
    
    def verifier_proprietes(self):
        """Vérifie si le graphe est un graphe d'ordonnancement"""
        if not self.matrix:
            print("Le graphe n'a pas encore été construit.")
            return False
        
        print("\n*** Vérification des propriétés ***")
        
        # 1. Vérifier les arcs négatifs
        has_negative = False
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix)):
                if self.matrix[i][j] is not None and self.matrix[i][j] < 0:
                    has_negative = True
                    break
        
        if has_negative:
            print("- Le graphe contient des arcs avec des valeurs négatives.")
        else:
            print("- Aucun arc avec valeur négative trouvé.")
        
        # 2. Vérifier les circuits
        circuit = self.detecter_circuit()
        if circuit:
            print(f"- Circuit détecté: {circuit}")
        else:
            print("- Aucun circuit détecté.")
        
        return not has_negative and not circuit
    
    def detecter_circuit(self):
        """Détecte un circuit dans le graphe en utilisant l'algorithme de Kahn"""
        print("\nDétection de circuit (méthode d'élimination des points d'entrée):")
        
        # Créer une copie du graphe pour travailler
        size = len(self.matrix)
        in_degree = [0] * size
        adj = [[] for _ in range(size)]
        
        # Calculer le degré entrant et la liste d'adjacence
        for i in range(size):
            for j in range(size):
                if self.matrix[i][j] is not None:
                    adj[i].append(j)
                    in_degree[j] += 1
        
        # File des sommets avec degré entrant 0
        queue = deque([i for i in range(size) if in_degree[i] == 0])
        count = 0
        topo_order = []
        
        while queue:
            print(f"\nPoints d'entrée: {list(queue)}")
            u = queue.popleft()
            topo_order.append(u)
            
            print(f"Suppression du point d'entrée {u}")
            
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
            
            count += 1
            
            remaining = [i for i in range(size) if in_degree[i] > 0]
            print(f"Sommets restants: {remaining if remaining else 'Aucun'}")
        
        if count != size:
            # Il y a un circuit, trouvons-le
            visited = [False] * size
            on_stack = [False] * size
            path = []
            
            def dfs(node):
                visited[node] = True
                on_stack[node] = True
                path.append(node)
                
                for neighbor in adj[node]:
                    if not visited[neighbor]:
                        if dfs(neighbor):
                            return True
                    elif on_stack[neighbor]:
                        # Trouvé un circuit
                        circuit_start = path.index(neighbor)
                        return path[circuit_start:] + [neighbor]
                
                on_stack[node] = False
                path.pop()
                return False
            
            for node in range(size):
                if not visited[node]:
                    circuit = dfs(node)
                    if circuit:
                        return circuit
            
            return []  # Ne devrait pas arriver si count != size
        else:
            print("\n-> Il n'y a pas de circuit")
            return None
    
    def calculer_rangs(self):
        """Calcule les rangs des sommets du graphe"""
        if not self.matrix:
            print("Le graphe n'a pas encore été construit.")
            return None
        
        print("\n*** Calcul des rangs ***")
        
        size = len(self.matrix)
        ranks = [0] * size
        
        # Tri topologique
        in_degree = [0] * size
        adj = [[] for _ in range(size)]
        
        for i in range(size):
            for j in range(size):
                if self.matrix[i][j] is not None:
                    adj[i].append(j)
                    in_degree[j] += 1
        
        queue = deque([i for i in range(size) if in_degree[i] == 0])
        
        while queue:
            u = queue.popleft()
            
            for v in adj[u]:
                if ranks[v] < ranks[u] + 1:
                    ranks[v] = ranks[u] + 1
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        
        print("Rangs des sommets:")
        for i in range(size):
            print(f"Sommet {i}: rang {ranks[i]}")
        
        return ranks
    
    def calculer_calendriers(self):
        """Calcule les calendriers au plus tôt et au plus tard"""
        if not self.matrix:
            print("Le graphe n'a pas encore été construit.")
            return None, None, None
        
        print("\n*** Calcul des calendriers ***")
        
        size = len(self.matrix)
        early = [0] * size
        late = [float('inf')] * size
        
        # Calendrier au plus tôt (parcours dans l'ordre topologique)
        in_degree = [0] * size
        adj = [[] for _ in range(size)]
        
        for i in range(size):
            for j in range(size):
                if self.matrix[i][j] is not None:
                    adj[i].append(j)
                    in_degree[j] += 1
        
        queue = deque([i for i in range(size) if in_degree[i] == 0])
        
        while queue:
            u = queue.popleft()
            
            for v in adj[u]:
                if early[v] < early[u] + (self.matrix[u][v] if self.matrix[u][v] is not None else 0):
                    early[v] = early[u] + (self.matrix[u][v] if self.matrix[u][v] is not None else 0)
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        
        # Durée totale du projet
        total_duration = early[self.omega]
        print(f"\nDurée totale du projet: {total_duration}")
        
        # Calendrier au plus tard (parcours inverse)
        late[self.omega] = total_duration
        
        # Inverser le graphe
        rev_adj = [[] for _ in range(size)]
        rev_in_degree = [0] * size
        
        for i in range(size):
            for j in range(size):
                if self.matrix[i][j] is not None:
                    rev_adj[j].append(i)
                    rev_in_degree[i] += 1
        
        queue = deque([i for i in range(size) if rev_in_degree[i] == 0])
        
        while queue:
            u = queue.popleft()
            
            for v in rev_adj[u]:
                if late[v] > late[u] - (self.matrix[v][u] if self.matrix[v][u] is not None else 0):
                    late[v] = late[u] - (self.matrix[v][u] if self.matrix[v][u] is not None else 0)
                rev_in_degree[v] -= 1
                if rev_in_degree[v] == 0:
                    queue.append(v)
        
        print("\nCalendrier au plus tôt:")
        for i in range(size):
            print(f"Sommet {i}: {early[i]}")
        
        print("\nCalendrier au plus tard:")
        for i in range(size):
            print(f"Sommet {i}: {late[i]}")
        
        # Calcul des marges
        margins = [late[i] - early[i] for i in range(size)]
        print("\nMarges:")
        for i in range(size):
            print(f"Sommet {i}: {margins[i]}")
        
        return early, late, margins
    
    def trouver_chemins_critiques(self, early, late):
        """Trouve les chemins critiques du graphe"""
        if not self.matrix or early is None or late is None:
            print("Les calendriers n'ont pas encore été calculés.")
            return None
        
        print("\n*** Recherche des chemins critiques ***")
        
        size = len(self.matrix)
        critical_paths = []
        
        # Trouver tous les arcs critiques (marge = 0)
        critical_edges = []
        for i in range(size):
            for j in range(size):
                if self.matrix[i][j] is not None and late[j] - early[i] - (self.matrix[i][j] if self.matrix[i][j] is not None else 0) == 0:
                    critical_edges.append((i, j))
        
        # Construire le graphe des arcs critiques
        adj = [[] for _ in range(size)]
        for u, v in critical_edges:
            adj[u].append(v)
        
        # Trouver tous les chemins de α à ω dans ce graphe
        def dfs(node, path, paths):
            path.append(node)
            
            if node == self.omega:
                paths.append(path.copy())
            else:
                for neighbor in adj[node]:
                    dfs(neighbor, path, paths)
            
            path.pop()
        
        paths = []
        dfs(self.alpha, [], paths)
        
        if paths:
            print("\nChemin(s) critique(s) trouvé(s):")
            for path in paths:
                print(" -> ".join(map(str, path)))
        else:
            print("\nAucun chemin critique trouvé.")
        
        return paths

def main():
    ordonnancement = Ordonnancement()
    
    print("=== Programme d'ordonnancement ===")
    
    while True:
        print("\nOptions:")
        print("1. Charger un fichier de contraintes")
        print("2. Afficher le graphe")
        print("3. Vérifier les propriétés du graphe")
        print("4. Calculer les rangs")
        print("5. Calculer les calendriers et marges")
        print("6. Trouver les chemins critiques")
        print("7. Exécuter toutes les étapes")
        print("8. Quitter")
        
        choix = input("Votre choix (1-8): ")
        
        if choix == "1":
            filename = input("Nom du fichier à charger: ")
            if ordonnancement.lire_fichier(filename):
                ordonnancement.construire_graphe()
        elif choix == "2":
            ordonnancement.afficher_graphe()
        elif choix == "3":
            if ordonnancement.verifier_proprietes():
                print("\n-> Le graphe peut être utilisé pour l'ordonnancement")
            else:
                print("\n-> Le graphe NE peut PAS être utilisé pour l'ordonnancement")
        elif choix == "4":
            ordonnancement.calculer_rangs()
        elif choix == "5":
            early, late, margins = ordonnancement.calculer_calendriers()
        elif choix == "6":
            early, late, _ = ordonnancement.calculer_calendriers()
            ordonnancement.trouver_chemins_critiques(early, late)
        elif choix == "7":
            # Exécution complète
            if not ordonnancement.tasks:
                print("Veuillez d'abord charger un fichier de contraintes.")
                continue
            
            ordonnancement.afficher_graphe()
            
            if ordonnancement.verifier_proprietes():
                ordonnancement.calculer_rangs()
                early, late, margins = ordonnancement.calculer_calendriers()
                ordonnancement.trouver_chemins_critiques(early, late)
        elif choix == "8":
            print("Fin du programme.")
            break
        else:
            print("Choix invalide. Veuillez sélectionner une option entre 1 et 8.")

if __name__ == "__main__":
    main()