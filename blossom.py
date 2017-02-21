import fractions

vertices = {}
filled_edges = set()
case_1 = set()
not_yet_full = set()

INF = float("Inf")


class Edge(object):
    def __init__(self, _v1, _v2, _w):
        self.v1 = _v1
        self.v2 = _v2
        self.w = fractions.Fraction(_w)
        self.selected = False
        self.v1.add_edge(self)
        self.v2.add_edge(self)
        not_yet_full.add(self)

    def other_vertex(self, v):
        if v == self.v1:
            return self.v2
        else:
            return self.v1

    def compute_charge(self):
        charge = 0
        for v in (self.v1, self.v2):
            charge = charge + v.compute_charge(self)
        return charge

    def remaining_charge(self):
        remaining = self.w - self.compute_charge()
        return remaining

    def is_selected(self):
        return self.selected

    def toogle(self):
        self.selected = not self.selected
        if self.selected:
            print("+ " + self.__str__())
        else:
            print("- " + self.__str__())

    def filled(self):
        print("Naplnila sa hrana " + self.__str__())
        filled_edges.add(self)
        not_yet_full.discard(self)
        bl1 = self.v1.get_outer_most()
        bl2 = self.v2.get_outer_most()
        if (not bl1.active):
            if (not bl2.active):
                print("Cinky predsa nespajam")
            else:
                if(not bl2.even):
                    print("Problem: Naplnila sa hrana odcitovanim s neaktivnym blossomom")
                else:
                    bl2.append_dumbbell(bl1, self)
                    print("Pripajam cinku v blossome " + bl1.__str__())
        elif (not bl2.active):
            if (not bl1.even):
                print("Problem: Naplnila sa hrana odcitovanim s neaktivnym blossomom")
            else:
                bl1.append_dumbbell(bl2, self)
                print("Pripajam cinku v blossome " + bl2.__str__())
        elif bl1.get_root() == bl2.get_root():
            if (not bl1.even) or not bl2.even:
                print("Problem: Naplnila sa hrana odcitovanim v jednom strome")
            else:
                print("riesim case 3")
                bl1.solve_case_3(bl2, self)
        else:
            if (not bl1.even) or not bl2.even:
                print("Problem: Naplnila sa hrana odcitovanim medzi dvoma stromami")
            print("riesim case 4")
            bl1.solve_case_4(bl2, self)

    def __str__(self):
        return "<{}, {}>".format(str(self.v1), str(self.v2))

    def __repr__(self):
        if self.selected:
            return "({}, {})".format(repr(self.v1), repr(self.v2))
        else:
            return "({}, {})".format(repr(self.v1), repr(self.v2))


def check_parent_edge(blossom, self, edge):
    #if
    pass


class Blossom:
    min_charge = 0

    def __init__(self, _v, _w, inners, _vertex):
        self.active = True
        self.out = True
        self.vertex = _vertex
        self.even = True
        self.parent = None
        self.edge_to_parent = None
        self.outter_blossom = None
        self.suspended_blossoms = []
        self.v = _v
        self.charge = fractions.Fraction(_w)
        self.inner_blossoms = tuple(inners)
        self.vertices = set()
        if not self.vertex:
            for bl in self.inner_blossoms:
                self.vertices.update(bl.vertices)
            self.out_edges = self.compute_outgoing_edges()

    def contained_vertices(self):
        return self.vertices

    def compute_outgoing_edges(self):
        edges = set()
        result = set()
        for bl in self.inner_blossoms:
            edges.update(bl.outgoing_edges())
        for edge in edges:
            if (edge.v1 in self.vertices) and (edge.v2 in self.vertices):
                pass
            else:
                result.add(edge)
        return result

    def outgoing_edges(self):
        return self.out_edges

    def get_root(self):
        root = self
        while not root.parent == None:
            root = root.parent
        return root

    def get_outer_most(self):
        outter = self
        while not outter.out:
            outter = outter.outter_blossom
        return outter

    def compute_charge(self, edge):
        charge = 0
        if edge in self.out_edges:
            if not self.out:
                charge = charge + self.outter_blossom.compute_charge(edge)
            charge = charge + self.charge
        return charge

    def is_active(self):
        return self.active

    def this_blossom_max_delta(self):
        max_delta = float("Inf")
        if self.even:
            for edge in self.out_edges:
                remaining = edge.remaining_charge()
                if(not edge.v1.get_outer_most().active)and(not edge.v2.get_outer_most().active):
                       print("Problem: Non of outermost blossoms is active")
                outer1 = edge.v1.get_outer_most()
                outer2 = edge.v2.get_outer_most()
                if outer1.active and outer2.active:
                    if outer2.even and outer1.even:
                        max_delta = min(max_delta, remaining / 2)
                if outer1.active and not outer2.active:
                    if outer2.even and outer1.even:
                        max_delta = min(max_delta, remaining)
                if not outer1.active and outer2.active:
                    if outer2.even and outer1.even:
                        max_delta = min(max_delta, remaining)
        else:
            max_delta = self.charge - self.min_charge
        return max_delta

    def get_max_delta(self, c=0):
        if not(self.active) or not self.out:
            print("Problem: Checking delta for wrong blossom"+str(self)+" "+str(self.get_root()))
            input()
        max_delta = INF
        for bl in self.suspended_blossoms:
            max_delta = min(max_delta, bl.get_max_delta(c + 1))
        return min(max_delta, self.this_blossom_max_delta())

    def change_charge(self, delta):
        for bl in self.suspended_blossoms:
            bl.change_charge(delta)
        if self.even:
            self.charge = self.charge + delta
        else:
            self.charge = self.charge - delta
            if self.charge == self.min_charge:
                case_1.add(self)

    def edges_to_another_blossom(self, another_blossom):
        edges = set.intersection(self.out_edges, another_blossom.out_edges).copy()
        return edges

    def full_edges_to_a_b(self, another_blossom):
        edges = self.edges_to_another_blossom(another_blossom).copy()
        full_edges = set()
        for e in edges:
            if e.remaining_charge() == 0:
                full_edges.add(e)
        return full_edges.copy()

    def get_path_of_odd_length(self, entry, exit, blossoms_tuple):
        return self.split_in_paths(entry, exit, blossoms_tuple)[0]


    def split_in_paths(self, entry, exit, blossoms_tuple):
        i = min(blossoms_tuple.index(entry), blossoms_tuple.index(exit))
        j = max(blossoms_tuple.index(entry), blossoms_tuple.index(exit))
        p1 = tuple(blossoms_tuple[i + 1:j])
        p2 = tuple(blossoms_tuple[j + 1:]) + tuple(blossoms_tuple[:i])
        if i == j:
            odd = (blossoms_tuple[i],)
            if len(p1) != 0:
                even = p1
            else:
                even = p2
        else:
            if len(p1) % 2 == 0:
                even = p1
                odd = (blossoms_tuple[j],) + p2 + (blossoms_tuple[i],)
            else:
                even = p2
                odd = (blossoms_tuple[i],) + p1 + (blossoms_tuple[j],)
        return (odd, even)

    def solve_case_1(self):
        print("riesim case 1")
        entry_blossom = None
        exit_blossom = None
        if (len(self.suspended_blossoms) != 1):
            print("Problem: More than one suspended blossom")
        print("size je"+str(len(self.suspended_blossoms)))
        outgoing = self.full_edges_to_a_b(self.suspended_blossoms[0]).pop()
        print(outgoing)
        print(self.edge_to_parent)
        for bl in self.inner_blossoms:
            print(str(bl)+" "+str(bl.edge_to_parent)+" "+str(bl.out_edges))
            if self.edge_to_parent in bl.outgoing_edges():
                entry_blossom = bl
            if outgoing in bl.out_edges:
                exit_blossom = bl
        print(" connection between "+str(entry_blossom)+" "+str(exit_blossom)+" "+str(self.inner_blossoms))
        odd = self.get_path_of_odd_length(entry_blossom, exit_blossom, self.inner_blossoms)
        print(odd)
        if odd[0] != entry_blossom:
            odd = odd[::-1]
        length = len(self.inner_blossoms)
        print(odd)
        for i in range(0, length):
            bl = self.inner_blossoms[i]
            if not bl in odd:
                bl.active = False
                print("deaktivovany "+str(bl))
                bl.out = True
                bl.outter_blossom = None
                bl.parent = None
                bl.edge_to_parent = None
                for bl2 in (bl.suspended_blossoms, bl.parent):
                    if not bl.full_edges_to_a_b(bl2).is_selected():
                        bl.clear_connection(bl2)
                bl.suspended_blossoms = []
        parent = self.parent
        edge_t_p = self.edge_to_parent
        self.parent.suspended_blossoms.remove(self)
        self.parent.suspended_blossoms.append(odd[0])
        for i in range(0, len(odd)-1):
            bl = odd[i]
            bl.out = True
            bl.active = True
            print("aktivovany " + str(bl))
            bl.outter_blossom = None
            bl.parent = parent
            bl.edge_to_parent = edge_t_p
            if (bl.parent.parent == bl):
                print("cyklus, rubem " + self.inner_blossoms)
            bl.suspended_blossoms = [odd[i + 1]]
            if i % 2 == 0:
                bl.even = False
            else:
                bl.even = True
            parent = bl
            edge_t_p = bl.full_edges_to_a_b(odd[i + 1]).copy().pop()
        odd[-1].suspended_blossoms = self.suspended_blossoms.copy()
        odd[-1].parent = parent
        odd[-1].edge_to_parent = edge_t_p
        odd[-1].out = True
        odd[-1].active = True
        print("aktivovany " + str(odd[-1]))
        odd[-1].outter_blossom = None
        odd[-1].even = False
        if (odd[-1].parent.parent == odd[-1]):
            print("Problem: parent in cycle" + self.inner_blossoms)
        for bl in self.suspended_blossoms:
            bl.parent = odd[-1]

    def clear_connection(self, blossom):
        edges = self.edges_to_another_blossom(blossom)
        blossom.suspended_blossoms.remove(self)
        self.suspended_blossoms.remove(blossom)
        if self.parent == blossom:
            self.parent = None
            self.edge_to_parent = None
        if blossom.parent == self:
            blossom.parent = None
            blossom.edge_to_parent = None
        print(filled_edges.difference_update(edges))
        not_yet_full.update(edges)

    def append_dumbbell(self, blossom, edge):
        edges = blossom.outgoing_edges().copy()
        blossom2 = None
        edge2 = None
        for e in edges:
            if e.selected:
                edge2 = e
                for v in (e.v1, e.v2):
                    if v.get_outer_most() != blossom:
                        blossom2 = v.get_outer_most()
        edges.update(blossom2.outgoing_edges().copy())
        not_yet_full.update(edges)
        filled_edges.difference_update(edges)
        not_yet_full.discard(edge)
        not_yet_full.discard(edge2)
        filled_edges.add(edge)
        filled_edges.add(edge2)

        blossom.parent = self
        blossom.edge_to_parent = edge
        check_parent_edge(blossom,self,edge)
        blossom.active = True
        print("aktivovany " + str(blossom))
        blossom.even = False
        blossom.out = True
        blossom.outter_blossom = None
        blossom.suspended_blossoms = [blossom2]

        blossom2.parent = blossom
        blossom2.edge_to_parent = edge2
        blossom2.active = True
        print("aktivovany " + str(blossom2))
        blossom2.even = True
        blossom.out = True
        blossom.outter_blossom = None
        blossom2.suspended_blossoms = []

        self.suspended_blossoms.append(blossom)

    def solve_case_3(self, blossom, edge):
        chain1 = self.blossoms_to_root()
        chain2 = blossom.blossoms_to_root()
        for i in range(0, len(chain2)):
            if chain2[i] in chain1:
                Node = chain2[i]
                chain2 = chain2[:i + 1]
                break
        chain1 = chain1[:chain1.index(Node)]
        chain2 = chain2[::-1] + chain1
        wrap = Blossom(chain2[0].v, 0, chain2, False)
        wrap.parent = chain2[0].parent
        wrap.edge_to_parent = chain2[0].edge_to_parent
        if wrap.parent != None:
            wrap.parent.suspended_blossoms.append(wrap)
            wrap.parent.suspended_blossoms.remove(chain2[0])
        if(len(chain2)%2 != 1):
            print("Problem: wrong chain length")
        for bl in chain2:
            bl.active = False
            print("deaktivovany " + str(bl))
            bl.out = False
            bl.outter_blossom = wrap
            wrap.suspended_blossoms.extend(bl.suspended_blossoms)
        all_suspended = wrap.suspended_blossoms.copy()
        wrap.suspended_blossoms = []
        for s in all_suspended:
            if s not in chain2:
                s.parent = wrap
                wrap.suspended_blossoms.append(s)
        if wrap.parent == None:
            if vertices[wrap.v.number] != None:
                vertices[wrap.v.number] = wrap
            else:
                print("Problem: tree not mapped with right vertex")
        print("Nastal pripad 3, spolocny vrchol je: " + chain2[0].__str__())

    def blossoms_to_root(self):
        if self.parent == None:
            return (self,)
        else:
            return (self,) + self.parent.blossoms_to_root()

    def solve_case_4(self, blossom, edge):
        chain1 = edge.v1.blossoms_to_root()[::-1]
        chain2 = edge.v2.blossoms_to_root()[::-1]
        print(chain1)
        print(chain2)
        vertices.pop(chain1[0].v.number)
        vertices.pop(chain2[0].v.number)
        chain1[0].alter_path(chain1[0].v, edge.v1, chain1) #ked pri alternacii nezmenim v,tak to zakape ?
        edge.toogle()
        chain2[0].alter_path(chain2[0].v, edge.v2, chain2)
        chain1[0].deactivate()
        chain2[0].deactivate()
        # print("Alterujem cestu z vrcholu "+chain1[0].__str__()+" do "+str(edge.v1))
        # print("Alterujem cestu z vrcholu " + chain2[0].__str__() + " do " + str(edge.v2))
        print("Plne hrany: " + filled_edges.__str__())
        print()

    def all_important(self):
        edges = set()
        edges.update(self.outgoing_edges())
        for bl in self.suspended_blossoms:
            edges.update(bl.all_imortant())

    def alter_blossom(self, entry_v, exit_v):
        if not self.vertex:
            for bl in self.inner_blossoms:
                if entry_v in bl.vertices:
                    entry = bl
                if exit_v in bl.vertices:
                    exit_bl = bl
            path_to_alter = self.get_path_of_odd_length(entry, exit_bl, self.inner_blossoms)
            if path_to_alter[0] != entry:
                path_to_alter = path_to_alter[::-1]
            self.alter_path(entry_v, exit_v, path_to_alter)
            # jeden z dvoch koncov je stopka, druhy by mal byt stopkou po zaokruhleni
            if entry.v == self.v:
                self.v = exit_bl.v
                Node = exit_bl
            elif self.v == exit_bl.v:
                self.v = entry.v
                Node = entry
            else:
                print("Problem: chyba pri alternacii blossomu a zmene stopky"+str(self.v)+" "+str(exit_bl.v)+" "+str(entry.v)+" "+str(self.inner_blossoms))
            new_chain = self.inner_blossoms+self.inner_blossoms
            self.inner_blossoms = new_chain[self.inner_blossoms.index(Node):self.inner_blossoms.index(Node)+len(self.inner_blossoms)]

    def alter_path(self, entry_v, exit_v, chain):
        for i in range(0, len(chain) - 1):
            entry_bl = chain[i]
            exit_bl = chain[i + 1]
            edges = entry_bl.full_edges_to_a_b(exit_bl)
            if len(edges) != 1:
                print("Problem: zly pocet hran pri alteracii")
            edge = edges.copy().pop()
            edge.toogle()
            if edge.v1 in entry_bl.vertices:
                entry_bl.alter_blossom(entry_v, edge.v1)
                entry_v = edge.v2
            else:
                entry_bl.alter_blossom(entry_v, edge.v2)
                entry_v = edge.v1
        chain[-1].alter_blossom(entry_v, exit_v)

    def deactivate(self):
        self.active = False
        print("Deaktivovany "+str(self))
        for bl in self.suspended_blossoms:
            bl.deactivate()
        """
            edges = self.edges_to_another_blossom(bl)
            for e in edges:
                if not e.is_selected():
                    not_yet_full.add(e)
                    filled_edges.discard(e)
        """
        self.parent = None
        self.edge_to_parent = None
        self.suspended_blossoms = []
        #"""

    def __str__(self):
        return str(self.v.number)

    def __repr__(self):
        return str(self.v.number)


class Vertex(Blossom):
    min_charge = - float("INF")

    def __init__(self, _v):
        self.number = _v
        self.edges = []
        super(Vertex, self).__init__(self, 0, (None,), True)
        self.vertices = [self]
        self.vertex = True
        self.out_edges = set()

    def add_edge(self, edge):
        self.edges.append(edge)
        self.out_edges.add(edge)


def load_graph(input_file, ):
    next(input_file)
    for line in input_file:
        v1, v2, w = [int(x) for x in line.split(" ")]
        for v in (v1, v2):
            if v not in vertices:
                vertices[v] = Vertex(v)
        Edge(vertices[v1], vertices[v2], w)


file = open("graph.txt", "r")
load_graph(file)
counter = 0
while len(vertices) != 0:
    print(counter)
    counter =counter+1
    if len(vertices) % 2 == 1:
        print("NO")
        break
    max_delta = INF
    for v in vertices:
        max_delta = min(max_delta, vertices[v].get_max_delta())
    print("Max delta is: " + max_delta.__str__())
    for v in vertices:
        vertices[v].change_charge(max_delta)
    if len(case_1) != 0:
        bl = case_1.pop()
        print("Blossom ma naboj 0, rozpadava sa:" + str(bl))
        bl.solve_case_1()
    else:
        check_edges = not_yet_full.copy()
        for edge in check_edges:
            if edge.remaining_charge() == 0:
                bl1 = edge.v1.get_outer_most()
                bl2 = edge.v2.get_outer_most()
                if bl1.active and bl2.active:
                    if bl1.even and bl2.even:
                        edge.filled()
                        break
                else:
                    edge.filled()
                    break
    print("Nenaplnene " + not_yet_full.__str__())
    print("Plne hrany: " + filled_edges.__str__())
    print("Vrcholy :" + str([str(s) for s in vertices]))
    # input()

cost = 0
solution = []
for edge in filled_edges:
    if edge.is_selected():
        cost = cost + edge.w
        solution.append(edge)
print("Cena: " + str(cost))
print("Hrany v rieseni: " + str([str(s) for s in filled_edges if s.is_selected()]))
