from circuit_improvement import *

command = 'r'

if command == 'r':
    start = timer()
    run(add_sum5_suboptimal, 5, subcircuit_size=5, connected=True)
    end = timer()
    print('Time (sec):', end - start)
elif command == 'rf':
    # run_file_shuffle('circuit_improved', subcircuit_size=5, connected=True)
    run_file('sum/sum7_sub', subcircuit_size=5, connected=True)
elif command == 'mc':
    Circuit.make_code('ex/ex2_over1_size13', 'code')
elif command == 'd':
    c = Circuit(fn='op6_size14').draw('op6_size14')
