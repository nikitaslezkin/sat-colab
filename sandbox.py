from circuit import Circuit
from circuit_search import find_circuit, CircuitFinder
from itertools import product

def sum7():
    n = 7
    tt = [
        ''.join(str(sum(x) & 1) for x in product(range(2), repeat=n)),
        ''.join(str((sum(x) >> 1) & 1) for x in product(range(2), repeat=n)),
        ''.join(str((sum(x) >> 2) & 1) for x in product(range(2), repeat=n))
    ]

    circuit_finder = CircuitFinder(7, None, None, 19, tt)
    circuit_finder.fix_gate(7, 0, 1, '0110')
    circuit_finder.fix_gate(8, 2, 7, '0110')
    circuit_finder.fix_gate(9, 3, 8, '0110')
    circuit_finder.fix_gate(10, 4, 9, '0110')
    circuit_finder.fix_gate(11, 5, 10, '0110')
    circuit_finder.fix_gate(12, 6, 11, '0110')

    circuit_finder.fix_gate(13, 0, 8, '0110')
    circuit_finder.fix_gate(14, 8, 10, '0110')
    circuit_finder.fix_gate(15, 10, 12, '0110')

    circuit_finder.fix_gate(16, 7, 13, '0111')
    circuit_finder.fix_gate(17, 9, 14, '0111')

    circuit_finder.fix_gate(18, 8, 16, '0110')
    circuit_finder.fix_gate(19, 10, 17, '0110')

    for gate in range(20, 25):
        circuit_finder.forbid_wire(0, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(1, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(2, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(3, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(4, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(5, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(6, gate)

    for gate in range(20, 25):
        circuit_finder.forbid_wire(7, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(8, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(9, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(10, gate)

    for gate in range(20, 25):
        circuit_finder.forbid_wire(13, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(14, gate)
    for gate in range(20, 25):
        circuit_finder.forbid_wire(16, gate)

    circuit_finder.fix_gate(20, 18, 19)
    circuit_finder.fix_gate(21, 11, 15)
    circuit_finder.fix_gate(22, 17, 21)

    return circuit_finder.solve_cnf_formula()


def sum9():
    n = 9
    tt = [
        ''.join(str(sum(x) & 1) for x in product(range(2), repeat=n)),
        ''.join(str((sum(x) >> 1) & 1) for x in product(range(2), repeat=n)),
        ''.join(str((sum(x) >> 2) & 1) for x in product(range(2), repeat=n)),
        ''.join(str((sum(x) >> 3) & 1) for x in product(range(2), repeat=n))
    ]

    circuit_finder = CircuitFinder(9, None, None, 27, tt)
    circuit_finder.fix_gate(9, 0, 1, '0110')
    circuit_finder.fix_gate(10, 2, 9, '0110')
    circuit_finder.fix_gate(11, 3, 10, '0110')
    circuit_finder.fix_gate(12, 4, 11, '0110')
    circuit_finder.fix_gate(13, 5, 12, '0110')
    circuit_finder.fix_gate(14, 6, 13, '0110')
    circuit_finder.fix_gate(15, 7, 14, '0110')
    circuit_finder.fix_gate(16, 8, 15, '0110')

    circuit_finder.fix_gate(17, 0, 10, '0110')
    circuit_finder.fix_gate(18, 10, 12, '0110')
    circuit_finder.fix_gate(19, 12, 14, '0110')
    circuit_finder.fix_gate(20, 14, 16, '0110')

    circuit_finder.fix_gate(21, 9, 17, '0111')
    circuit_finder.fix_gate(22, 11, 18, '0111')
    circuit_finder.fix_gate(23, 13, 19, '0111')
    circuit_finder.fix_gate(24, 15, 20, '0010')

    circuit_finder.fix_gate(25, 10, 21, '0110')
    circuit_finder.fix_gate(26, 12, 22, '0110')
    circuit_finder.fix_gate(27, 14, 23, '0110')

    for gate in range(28, 35):
        circuit_finder.forbid_wire(0, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(1, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(2, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(3, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(4, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(5, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(6, gate)

    for gate in range(28, 35):
        circuit_finder.forbid_wire(7, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(8, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(9, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(10, gate)

    for gate in range(28, 35):
        circuit_finder.forbid_wire(13, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(14, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(16, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(17, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(18, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(19, gate)
    for gate in range(28, 35):
        circuit_finder.forbid_wire(20, gate)

    return circuit_finder.solve_cnf_formula()

def newmdfa():
    n = 5
    tt = [
        '00110011110011001100110000110011',
        #'01101001101001010101101001101001',
        '01101111110101110111110110011111'
    ]
    k = 7
    circuit_finder = CircuitFinder(n, None, None, k, tt)
    return circuit_finder.solve_cnf_formula()


def lol():
    n = 3
    tt = [
        ''.join(str(sum(x) & 1) for x in product(range(2), repeat=n)),
        ''.join(str((sum(x) >> 1) & 1) for x in product(range(2), repeat=n))
    ]
    circuit = find_circuit(n, None, None, 5, tt)
    print(circuit)

def add_sum3(circuit, input_labels):
    assert len(input_labels) == 3
    for input_label in input_labels:
        assert input_label in circuit.input_labels or input_label in circuit.gates

    [x1, x2, x3] = input_labels

    g1 = circuit.add_gate(x1, x2, '0110')
    g2 = circuit.add_gate(x2, x3, '0110')
    g3 = circuit.add_gate(g1, g2, '0111')
    g4 = circuit.add_gate(g1, x3, '0110')
    g5 = circuit.add_gate(g3, g4, '0110')

    return g4, g5

def lol2():
    circuit = Circuit(input_labels=['i1', 'i2', 'i3', 'i4', 'i5'])
    x1, x2, x3, x4, x5 = circuit.input_labels
    a0, a1 = add_sum3(circuit, [x1, x2, x3])
    b0, b1 = add_sum3(circuit, [a0, x4, x5])
    w1, w2 = add_sum2(circuit, [a1, b1])
    circuit.outputs = [b0, w1, w2]
    check_sum_circuit(circuit)
    print(circuit)

if __name__ == '__main__':

    # c = newmdfa()
    #
    # if c:
    #     print(c)
    #     c.draw('circuit')
    # else:
    #     print('There is no such circuit')
    lol2()
