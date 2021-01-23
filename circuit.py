from itertools import product
import networkx as nx

class Circuit:
    gate_types = {
        # constants
        '0000': '0',
        '1111': '1',
        # degenerate
        '0011': 'x',
        '1100': 'not(x)',
        '0101': 'y',
        '1010': 'not(y)',
        # xor-type
        '0110': '+',
        '1001': '=',
        # and-type
        '0001': 'and',
        '1110': 'nand',
        '0111': 'or',
        '1000': 'nor',
        '0010': '>',
        '0100': '<',
        '1011': '>=',
        '1101': '<=',
    }

    def __init__(self, input_labels=None, gates=None, outputs=None, fn=None):
        self.input_labels = input_labels
        self.gates = gates
        self.outputs = outputs
        if fn is not None:
            self.load_from_file(fn)

    def __str__(self):
        s = ''
        s += 'Inputs: ' + ' '.join(map(str, self.input_labels)) + '\n'
        for gate in self.gates:
            s += f'{gate}: ({self.gates[gate][0]} {self.gate_types[self.gates[gate][2]]} {self.gates[gate][1]})\n'
        s += 'Outputs: ' + ' '.join(map(str, self.outputs))
        return s

    def load_from_string(self, string):
        lines = string.splitlines()
        number_of_inputs, number_of_gates, number_of_outputs = \
            list(map(int, lines[0].strip().split()))
        self.input_labels = lines[1].strip().split()
        assert len(self.input_labels) == number_of_inputs

        self.gates = {}
        for i in range(number_of_gates):
            gate, first, second, gate_type = lines[i + 2].strip().split()
            # assert first in self.gates or first in self.input_labels
            # assert second in self.gates or second in self.input_labels
            self.gates[gate] = (first, second, gate_type)

        self.outputs = lines[number_of_gates + 2].strip().split()
        assert len(self.outputs) == number_of_outputs

    def load_from_file(self, file_name):
        with open(file_name + '.ckt') as circuit_file:
            self.load_from_string(circuit_file.read())

    def save_to_file_verilog(self, file_name):
        with open(file_name, 'w') as circuit_file:
            gate_list = ', '.join(list(self.gates))
            input_labels_list = ', '.join(self.input_labels)
            output_labels_list = ', '.join(self.outputs)

            circuit_file.write(f'module circuit('
                               f'{input_labels_list}, '
                               f'{output_labels_list});\n')
            circuit_file.write(f'  input {input_labels_list};\n')
            circuit_file.write(f'  output {output_labels_list};\n')
            circuit_file.write(f'  wire {gate_list};\n')

            for gate in self.gates:
                circuit_file.write(f'\n  assign {gate} = ')
                first, second, gate_type = self.gates[gate]
                if gate_type == '0001':
                    circuit_file.write(f'{first} & {second}')
                elif gate_type == '0111':
                    circuit_file.write(f'{first} | {second}')
                elif gate_type == '0110':
                    circuit_file.write(f'{first} ^ {second}')
                else:
                    assert False, 'not yet implemented'

            circuit_file.write('\nendmodule')

    def save_to_file(self, file_name):
        print(file_name)
        with open(file_name, 'w') as circuit_file:
            circuit_file.write(f'{len(self.input_labels)} {len(self.gates)} {len(self.outputs)}\n')
            circuit_file.write(' '.join(self.input_labels))
            for gate in self.gates:
                first, second, gate_type = self.gates[gate]
                circuit_file.write(f'\n{gate} {first} {second} {gate_type}')
            circuit_file.write('\n' + ' '.join(self.outputs))

    def construct_graph(self):
        circuit_graph = nx.DiGraph()
        for input_label in self.input_labels:
            circuit_graph.add_node(input_label)

        for gate in self.gates:
            circuit_graph.add_node(gate, label=f'{gate}: {self.gates[gate][0]} {self.gate_types[self.gates[gate][2]]} {self.gates[gate][1]}')
            circuit_graph.add_edge(self.gates[gate][0], gate)
            circuit_graph.add_edge(self.gates[gate][1], gate)

        return circuit_graph

    @staticmethod
    def make_circuit(graph, input_gates, output_gates):
        circuit = Circuit(input_labels=input_gates, gates={}, outputs=list(output_gates))
        for gate in graph.pred:
            if gate in input_gates:
                continue
            operation = (graph.nodes[gate]['label']).split()[2]
            bit_operation = list(circuit.gate_types.keys())[list(circuit.gate_types.values()).index(operation)]
            circuit.gates[gate] = ((graph.nodes[gate]['label']).split()[1], (graph.nodes[gate]['label']).split()[3], bit_operation)

        return circuit

    @staticmethod
    def make_code(filename_in, filename_out):
        result = ''
        with open(filename_in) as circuit_file:
            number_of_inputs, number_of_gates, number_of_outputs = \
                list(map(int, circuit_file.readline().strip().split()))

            input_labels = circuit_file.readline().strip().split()
            result += f'['
            for i in range(number_of_inputs):
                result += f'{input_labels[i]}'
                if i != number_of_inputs - 1:
                    result += ', '
            result += '] = input_labels\n'
            for _ in range(number_of_gates):
                gate, first, second, gate_type = circuit_file.readline().strip().split()
                result += f"{gate} = circuit.add_gate({first}, {second}, '{gate_type}')\n"

            outputs = circuit_file.readline().strip().split()
            result += f'\nreturn '
            for i in range(number_of_outputs):
                result += f'{outputs[i]}'
                if i != number_of_outputs - 1:
                    result += ', '
            result += '\n'

        with open(filename_out + '.ckt', 'w') as file:
            file.write(result)

    def draw(self, file_name='circuit'):
        a = nx.nx_agraph.to_agraph(self.construct_graph())
        for gate in self.input_labels:
            a.get_node(gate).attr['shape'] = 'box'
        if isinstance(self.outputs, str):
            self.outputs = [self.outputs]
        for output in self.outputs:
            a.get_node(output).attr['shape'] = 'box'
        a.layout(prog='dot')
        a.draw(file_name)

    def get_truth_tables(self):
        truth_tables = {}

        for gate in self.input_labels:
            truth_tables[gate] = []
        for gate in self.gates:
            truth_tables[gate] = []

        topological_ordering = list(nx.topological_sort(self.construct_graph()))

        for assignment in product(range(2), repeat=len(self.input_labels)):
            for i in range(len(self.input_labels)):
                truth_tables[self.input_labels[i]].append(assignment[i])

            for gate in topological_ordering:
                if gate in self.input_labels:
                    continue
                assert gate in self.gates
                f, s = self.gates[gate][0], self.gates[gate][1]
                assert len(truth_tables[f]) > len(truth_tables[gate]) and len(truth_tables[s]) > len(truth_tables[gate])
                fv, sv = truth_tables[f][-1], truth_tables[s][-1]
                truth_tables[gate].append(int(self.gates[gate][2][sv + 2 * fv]))

        return truth_tables

    def add_gate(self, first_predecessor, second_predecessor, operation, gate_label=None):
        if not gate_label:
            gate_label = f'z{len(self.gates)}'
        assert gate_label not in self.gates and gate_label not in self.input_labels

        self.gates[gate_label] = (first_predecessor, second_predecessor, operation)

        return gate_label
