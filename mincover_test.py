import pytest
import time
import random
import networkx as nx
from mincover import mincover
from testcases import parse_testcases

testcases = parse_testcases("testcases.txt")

def run_testcase(input:str):
    graph = nx.Graph(input)
    cover = mincover(graph)
    return len(cover)

@pytest.mark.parametrize("testcase", testcases, ids=[testcase["name"] for testcase in testcases])
def test_cases(testcase):
    actual_output = run_testcase(testcase["input"])
    assert actual_output == testcase["output"], f"Expected {testcase['output']}, got {actual_output}"


def is_valid_cover(graph, cover):
    """Every edge must have at least one endpoint in the cover."""
    return all(u in cover or v in cover for u, v in graph.edges)


def test_new_cases():
    # Empty graph
    g = nx.Graph()
    assert mincover(g) == set()

    # Single node, no edges
    g = nx.Graph()
    g.add_node(0)
    cover = mincover(g)
    assert is_valid_cover(g, cover)
    assert len(cover) == 0

    # Single edge
    g = nx.Graph([(0, 1)])
    cover = mincover(g)
    assert is_valid_cover(g, cover)
    assert len(cover) == 1

    # Path graph P_n: cover = ceil(n/2) - 1 = floor(n/2)
    for n in [4, 6, 8, 10]:
        g = nx.path_graph(n)
        cover = mincover(g)
        assert is_valid_cover(g, cover)
        assert len(cover) == n // 2

    # Complete graph K_n: cover = n-1
    for n in [3, 4, 5, 6]:
        g = nx.complete_graph(n)
        cover = mincover(g)
        assert is_valid_cover(g, cover)
        assert len(cover) == n - 1

    # Complete bipartite K_{m,n}: cover = min(m,n)
    for m, n in [(2, 3), (3, 4), (4, 4)]:
        g = nx.complete_bipartite_graph(m, n)
        cover = mincover(g)
        assert is_valid_cover(g, cover)
        assert len(cover) == min(m, n)

    # Star graph S_n (one hub, n leaves): cover = {hub} = 1
    for n in [5, 10, 20]:
        g = nx.star_graph(n)
        cover = mincover(g)
        assert is_valid_cover(g, cover)
        assert len(cover) == 1

    # Cycle graph C_n: even -> n//2, odd -> (n+1)//2
    for n in [4, 5, 6, 7, 8]:
        g = nx.cycle_graph(n)
        cover = mincover(g)
        assert is_valid_cover(g, cover)
        assert len(cover) == (n + 1) // 2

    # Petersen graph: known min cover = 6
    g = nx.petersen_graph()
    cover = mincover(g)
    assert is_valid_cover(g, cover)
    assert len(cover) == 6

    # Random graphs: verify cover validity and optimality via König's theorem on bipartite
    rng = random.Random(123)
    for _ in range(10):
        n = rng.randint(5, 20)
        p = rng.uniform(0.2, 0.7)
        g = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10**6))
        cover = mincover(g)
        assert is_valid_cover(g, cover), "Cover invalid on random graph"

    # Bipartite random: verify König's theorem (|min cover| == |max matching|)
    for _ in range(10):
        n1 = rng.randint(3, 15)
        n2 = rng.randint(3, 15)
        p = rng.uniform(0.2, 0.8)
        g = nx.bipartite.random_graph(n1, n2, p, seed=rng.randint(0, 10**6))
        cover = mincover(g)
        assert is_valid_cover(g, cover)
        max_matching = nx.max_weight_matching(g, maxcardinality=True)
        assert len(cover) == len(max_matching), (
            f"König violated: cover={len(cover)}, matching={len(max_matching)}"
        )

    # Performance: 50 nodes, 1000 edges must finish in 1 second
    g = nx.gnm_random_graph(50, 1000, seed=42)
    t0 = time.time()
    cover = mincover(g)
    elapsed = time.time() - t0
    assert is_valid_cover(g, cover)
    assert elapsed < 1.0, f"Too slow: {elapsed:.2f}s on 50-node/1000-edge graph"

    # Disconnected graph: cover = union of covers of components
    g = nx.Graph()
    g.add_edges_from([(0, 1), (2, 3), (4, 5)])
    cover = mincover(g)
    assert is_valid_cover(g, cover)
    assert len(cover) == 3
