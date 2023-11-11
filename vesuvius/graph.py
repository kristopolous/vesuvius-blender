import subprocess
import math
from collections import defaultdict


class Graph:
  def __init__(self, vertices, edges):
    self.vertices = vertices
    self._from = defaultdict(list)
    self._into = defaultdict(list)
    for (v, w, m) in edges:
      assert v in vertices and w in vertices, "bad edge"
      self._from[v].append((w, m))
      self._into[w].append((v, m))

  def copy(self):
    return Graph(self.vertices.copy(), [(v, w, m) for (w, m) in self._from[v] for v in self.vertices])

  def _remove(self, l, v):
    for i in range(len(l)-1, -1, -1):
      if l[i][0] == v:
        del l[i]

  def remove(self, v):
    for (w, _) in self._from[v]: self._remove(self._into[w], v)
    for (w, _) in self._into[v]: self._remove(self._from[w], v)
    del self._from[v]
    del self._into[v]
    self.vertices.remove(v)


  def weight_from(self, v): return sum(m for (_, m) in self._from[v])
  def weight_into(self, v): return sum(m for (_, m) in self._into[v])

  def edges_from(self, v): return [(v, w, m) for (w, m) in self._from[v]]
  def edges_into(self, v): return [(w, v, m) for (w, m) in self._into[v]]

  def sink(self):
    for v in self.vertices:
      if len(self._from[v]) == 0:
        return v

  def sinks(self):
    sinks = []
    for v in self.vertices:
      if len(self._from[v]) == 0:
        sinks.append(v)
    return sinks

  def source(self):
    for v in self.vertices:
      if len(self._into[v]) == 0:
        return v

  def isolated(self):
    for v in self.vertices:
      if len(self._from[v]) == 0 and len(self._into[v]) == 0:
        return v

  def __str__(self):
    s = "digraph {\n"
    for v in self.vertices:
      s += f"  \"{v}\";\n"
    for v in self._from:
      for w, m in self._from[v]:
        s += f"  \"{v}\" -> \"{w}\" [weight={m:0}, label=\"{m}\"];\n"
    s += "}\n"
    return s

  def vis(self, path):
    with open(f"/tmp/{path}.dot", "w+") as f:
      print(str(self), file=f)
    return subprocess.run(["dot", "-Tpng", f"{path}.dot", "-o", f"{path}.png"], cwd="/tmp")


def break_cycles(g: Graph):
  vertices = g.vertices.copy()
  edges = []
  edges_cut = []
  while len(g.vertices) > 0:
    v = g.sink()
    while v:
      edges += g.edges_into(v)
      g.remove(v)
      v = g.sink()

    v = g.isolated()
    while v:
      g.remove(v)
      v = g.isolated()

    v = g.source()
    while v:
      edges += g.edges_from(v)
      g.remove(v)
      v = g.source()

    if len(g.vertices) == 0:
      break

    v_max = g.vertices[0]
    d_max = g.weight_from(v_max) - g.weight_into(v_max)
    for v in g.vertices:
      d_v = g.weight_from(v) - g.weight_into(v)
      if d_v > d_max:
        d_max = d_v
        v_max = v
    edges += g.edges_from(v_max)
    edges_cut += g.edges_into(v_max)
    g.remove(v_max)

  return Graph(vertices, edges), edges_cut


def sort_by_distance_with_constraints(g, distances, delta=0.001):
  levels = []
  while g.vertices:
    vs_available = g.sinks()
    v = vs_available[0]
    d = distances[v]
    for w in vs_available:
      if distances[w] < d:
        d = distances[w]
        v = w
    level = [v]
    g.remove(v)
    for w in vs_available:
      if w != v:
        if distances[w] < distances[v] + delta:
          level.append(w)
          g.remove(w)
    levels.append(level)
  return levels
