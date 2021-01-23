from circuit import Circuit
from itertools import combinations, product
import os
import pycosat
import sys
from timeit import default_timer as timer


class CircuitFinder:
    def __init__(self, dimension, input_labels, input_truth_tables, number_of_gates, output_truth_tables):
        self.dimension = dimension

        if input_truth_tables is not None:
            assert input_labels is not None
            assert len(input_labels) == len(input_truth_tables)
            assert all(len(table) == 1 << dimension for table in input_truth_tables)
            assert all(all(symbol in '01' for symbol in table) for table in input_truth_tables)
        else:
            if input_labels is None:
                input_labels = list(range(dimension))
            input_truth_tables = [[] for _ in range(dimension)]
            for t in range(1 << dimension):
                for i in range(dimension):
                    input_truth_tables[i].append((t >> (dimension - 1 - i)) & 1)
            input_truth_tables = [''.join(map(str, t)) for t in input_truth_tables]

        self.input_labels = input_labels
        self.input_truth_tables = input_truth_tables
        self.number_of_gates = number_of_gates
        self.output_truth_tables = output_truth_tables
        self.is_normal = all(table[0] != '1' for table in output_truth_tables)

        assert all(len(table) == 1 << dimension for table in output_truth_tables)
        assert all(all(symbol in "01*" for symbol in table) for table in output_truth_tables)

        number_of_input_gates = len(self.input_truth_tables)
        number_of_outputs = len(self.output_truth_tables)

        self.input_gates = list(range(number_of_input_gates))
        self.internal_gates = list(range(number_of_input_gates, number_of_input_gates + number_of_gates))
        self.gates = list(range(number_of_input_gates + number_of_gates))
        self.outputs = list(range(number_of_outputs))

        assert all(str(gate) not in self.input_labels for gate in self.internal_gates)

        self.clauses = []
        self.variables = {'dummy': 0}

        self.init_default_cnf_formula()

    def variable_number(self, name):
        if name in self.variables:
            return self.variables[name]

        self.variables[name] = len(self.variables) + 1
        return self.variables[name]

    # output of gate on inputs (p, q)
    def gate_type_variable(self, gate, p, q):
        assert 0 <= p <= 1 and 0 <= q <= 1
        assert gate in self.gates
        return self.variable_number(f'f_{gate}_{p}_{q}')

    # gate operates on gates first_pred and second_pred
    def predecessors_variable(self, gate, first_pred, second_pred):
        assert gate in self.internal_gates
        assert first_pred in self.gates and second_pred in self.gates
        assert first_pred < second_pred < gate
        return self.variable_number(f's_{gate}_{first_pred}_{second_pred}')

    # h-th output is computed at gate
    def output_gate_variable(self, h, gate):
        assert h in self.outputs
        assert gate in self.gates
        return self.variable_number(f'g_{h}_{gate}')

    # t-th bit of the truth table of gate
    def gate_value_variable(self, gate, t):
        assert gate in self.gates
        assert 0 <= t < 1 << self.dimension
        return self.variable_number(f'x_{gate}_{t}')

    def init_default_cnf_formula(self):
        def exactly_one_of(literals):
            return [list(literals)] + [[-a, -b] for (a, b) in combinations(literals, 2)]

        # gate operates on two gates predecessors
        for gate in self.internal_gates:
            self.clauses += exactly_one_of([self.predecessors_variable(gate, a, b) for (a, b) in combinations(range(gate), 2)])

        # each output is computed somewhere
        for h in range(len(self.outputs)):
            self.clauses += exactly_one_of([self.output_gate_variable(h, gate) for gate in self.internal_gates])

        # truth values for inputs
        for input_gate in self.input_gates:
            for t in range(1 << self.dimension):
                if self.input_truth_tables[input_gate][t] == '1':
                    self.clauses += [[self.gate_value_variable(input_gate, t)]]
                else:
                    assert self.input_truth_tables[input_gate][t] == '0'
                    self.clauses += [[-self.gate_value_variable(input_gate, t)]]

        # gate computes the right value
        for gate in self.internal_gates:
            for first_pred, second_pred in combinations(range(gate), 2):
                for a, b, c in product(range(2), repeat=3):
                    for t in range(1 << self.dimension):
                        self.clauses += [[
                            -self.predecessors_variable(gate, first_pred, second_pred),
                            (-1 if a else 1) * self.gate_value_variable(gate, t),
                            (-1 if b else 1) * self.gate_value_variable(first_pred, t),
                            (-1 if c else 1) * self.gate_value_variable(second_pred, t),
                            (1 if a else -1) * self.gate_type_variable(gate, b, c)
                        ]]

        # each output h computes the right value
        for h in self.outputs:
            for t in range(1 << self.dimension):
                if self.output_truth_tables[h][t] == '*':
                    continue

                for gate in self.internal_gates:
                    self.clauses += [[
                        -self.output_gate_variable(h, gate),
                        (1 if self.output_truth_tables[h][t] == '1' else -1) * self.gate_value_variable(gate, t)
                    ]]

        # each gate computes a non-degenerate function (0, 1, x, -x, y, -y)
        for gate in self.internal_gates:
            self.clauses += [[self.gate_type_variable(gate, 0, 0), self.gate_type_variable(gate, 0, 1), self.gate_type_variable(gate, 1, 0), self.gate_type_variable(gate, 1, 1)]]
            self.clauses += [[-self.gate_type_variable(gate, 0, 0), -self.gate_type_variable(gate, 0, 1), -self.gate_type_variable(gate, 1, 0), -self.gate_type_variable(gate, 1, 1)]]

            self.clauses += [[self.gate_type_variable(gate, 0, 0), self.gate_type_variable(gate, 0, 1), -self.gate_type_variable(gate, 1, 0), -self.gate_type_variable(gate, 1, 1)]]
            self.clauses += [[-self.gate_type_variable(gate, 0, 0), -self.gate_type_variable(gate, 0, 1), self.gate_type_variable(gate, 1, 0), self.gate_type_variable(gate, 1, 1)]]

            self.clauses += [[self.gate_type_variable(gate, 0, 0), -self.gate_type_variable(gate, 0, 1), self.gate_type_variable(gate, 1, 0), -self.gate_type_variable(gate, 1, 1)]]
            self.clauses += [[-self.gate_type_variable(gate, 0, 0), self.gate_type_variable(gate, 0, 1), -self.gate_type_variable(gate, 1, 0), self.gate_type_variable(gate, 1, 1)]]

        return self.clauses

    def save_cnf_formula_to_file(self, file_name):
        self.finalize_cnf_formula()

        with open(file_name, 'w') as file:
            file.write(f'p cnf {len(self.variables)} {len(self.clauses)}\n')
            for clause in self.clauses:
                file.write(f'{" ".join(map(str, clause))} 0\n')
            for v in self.variables:
                file.write(f'c {v} {self.variables[v]}\n')

    def solve_cnf_formula(self, solver=None, verbose=1):
        self.finalize_cnf_formula()

        if solver is None:
            result = pycosat.solve(self.clauses, verbose=verbose)
        elif solver == 'minisat':
            cnf_file_name = 'tmp.cnf'
            self.save_cnf_formula_to_file(cnf_file_name)
            # TODO: complete
            assert False
        else:
            assert False

        if result == 'UNSAT':
            return False

        gate_descriptions = {}
        for gate in self.internal_gates:
            first_predecessor, second_predecessor = None, None
            for f, s in combinations(range(gate), 2):
                if self.predecessors_variable(gate, f, s) in result:
                    first_predecessor, second_predecessor = f, s
                else:
                    assert -self.predecessors_variable(gate, f, s) in result

            gate_type = []
            for p, q in product(range(2), repeat=2):
                if self.gate_type_variable(gate, p, q) in result:
                    gate_type.append(1)
                else:
                    assert -self.gate_type_variable(gate, p, q) in result
                    gate_type.append(0)

            first_predecessor = self.input_labels[first_predecessor] if first_predecessor in self.input_gates else first_predecessor
            second_predecessor = self.input_labels[second_predecessor] if second_predecessor in self.input_gates else second_predecessor
            gate_descriptions[gate] = (first_predecessor, second_predecessor, ''.join(map(str, gate_type)))

        output_gates = []
        for h in self.outputs:
            for gate in self.gates:
                if self.output_gate_variable(h, gate) in result:
                    output_gates.append(gate)

        return Circuit(self.input_labels, gate_descriptions, output_gates)

    def finalize_cnf_formula(self):
        if self.is_normal:
            for gate in self.internal_gates:
                self.clauses += [[-self.gate_type_variable(gate, 0, 0)]]

    # The following method allows to further restrict the internal structure of a circuit.
    # Only use it if you know what you are doing.
    # The parameters gate, first_predecessor, second_predecessor are gate indices
    # (rather than labels).
    def fix_gate(self, gate, first_predecessor=None, second_predecessor=None, gate_type=None):
        assert gate in self.internal_gates

        if first_predecessor is not None and second_predecessor is not None:
            assert first_predecessor in self.gates
            assert second_predecessor in self.gates
            self.clauses += [[self.predecessors_variable(gate, first_predecessor, second_predecessor)]]
        else:
            if first_predecessor is not None:
                assert first_predecessor in self.gates
                assert not second_predecessor
                for a, b in combinations(gate, 2):
                    if a != first_predecessor and b != first_predecessor:
                        self.clauses += [[-self.predecessors_variable(gate, a, b)]]

        if gate_type:
            assert isinstance(gate_type, str) and len(gate_type) == 4

            if gate_type[0] != '0':
                self.is_normal = False

            for a, b in product(range(2), repeat=2):
                bit = int(gate_type[2 * a + b])
                assert bit in range(2)
                self.clauses += [[(1 if bit else -1) * self.gate_type_variable(gate, a, b)]]

    def forbid_wire(self, from_gate, to_gate):
        assert from_gate in self.gates
        assert to_gate in self.internal_gates
        assert from_gate < to_gate

        for other in self.gates:
            if other < to_gate and other != from_gate:
                self.clauses += [[-self.predecessors_variable(to_gate, min(other, from_gate), max(other, from_gate))]]


def find_circuit(dimension, input_labels, input_truth_tables, number_of_gates, output_truth_tables):
    circuit_finder = CircuitFinder(dimension, input_labels, input_truth_tables, number_of_gates, output_truth_tables)
    return circuit_finder.solve_cnf_formula(verbose=0)


if __name__ == '__main__':
    # if len(sys.argv) <= 1:
    #     print('Usage:', sys.argv[0], 'n r truthtable1 ... truthtablem')
    #     print('(n is the number of inputs, r is the number of gates, m is the number of outputs)')
    #     sys.exit(0)
    #
    # number_of_inputs = int(sys.argv[1])
    # number_of_gates = int(sys.argv[2])
    # output_truth_tables = sys.argv[3:]
    number_of_inputs = 5
    number_of_gates = 11
    output_truth_tables = ['01101001100101101001011001101001', '00010111011111100111111011101000', '00000000000000010000000100010111']

    start = timer()
    circuit = find_circuit(number_of_inputs, None, None, number_of_gates, output_truth_tables)
    end = timer()

    if not circuit:
        print('There is no such circuit, sorry')
    else:
        print('Circuit found!\n')
        print(circuit)
    print('Time (sec):', end - start)
