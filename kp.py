#######################################################################################
###                                                                                 ###
###   An iterative approximation algorithm for KP and MKP                           ###
###                                                                                 ###
###   python kp.py example.dat (example usage)                                      ###
###   output-example.dat (example output, saved to same directory)                  ###
###                                                                                 ###
###                                                                                 ###
###   Student Info                                                                  ###
###                                                                                 ###
###   Name: Mustafa Zortul                                                          ###
###   No: 524118023                                                                 ###
###                                                                                 ###
#######################################################################################
###                                                                                 ###
###   IMPORTANT: This script should be in the SAME directory with the data file     ###
###                                                                                 ###
#######################################################################################

import sys
import time
from operator import itemgetter


def kp_cmdline(path, dbg=False):
    capacity = 0
    profit = []
    weight = []
    z = 0
    n = 0
    s = 0 # critical item (r[0 to s] are picked, r[s to end] are left)
    
    
    multiple = False
    
    iters = []  # max approx after one whole iteration
                # an iteration = removal of one item and seeking solutions in j0
                # elements of this array are used in updating over greedy approx
            
    # approx = [] # dict (z, remove(J1), add(J0)) (scalar, list, list) (dict)
                # z is new total profit, remove and add are changes from greedy approximation
    
    
    capacity_list = []
    m = 0
    
    with open(path, "r") as file:
        # determine if problem is multiple or not
        n, unknown_val = [int(c.strip()) for c in file.readline().split()]
        second_line = [int(c.strip()) for c in file.readline().split()]
        
        if len(second_line) is unknown_val:
            multiple = True
            m = unknown_val
            to_read = n
            for val in second_line:
                capacity_list.append(val)
        else:
            to_read = n-1
            capacity = unknown_val
            profit.append(second_line[0])
            weight.append(second_line[1])
        
        #read (profit, weight) pairs form file
        for i in range(to_read):
            line = file.readline()
            # p and w are temporary variables
            p, w = [int(c.strip()) for c in line.split()]
            profit.append(p)
            weight.append(w)
    
    if multiple:
        # If problem is MKP, we initially solve it as single KP
        # We will take sum of capacities for the capacity of the single knapsack
        capacity = sum(capacity_list)
        
    
    # picked is the list of binary chars
    picked = [0] * n
    # sorted list of ratios (i love python btw)
    r = sorted([list((profit[i]/weight[i], i)) for i in range(n)], key=itemgetter(0), reverse=True)
    
    z = 0 #  (total profit for current approx)
    c = capacity #  (capacity left for current approx)
    for i in range(n):
        ratio = r[i][0]
        ind = r[i][1]
        if weight[ind] <= c:
            c -= weight[ind]
            picked[ind] = 1
            z += profit[ind]
        else:
            s = i
            break
    
    pack = [list((profit[r_[1]], weight[r_[1]], picked[r_[1]], r_[1])) for r_ in r]
    
    j0 = sorted(pack[s:], key=itemgetter(1))
    j1 = sorted(pack[:s], key=itemgetter(1))
    
    greedy_approx = {'z': z, 'c': c, 'j0': j0, 'j1': j1}
    
    # greedy approximation is the first iteration
    iters.append(greedy_approx)
    
    while True:
        
        last_iter = dict(iters[-1])
        j0 = last_iter['j0']
        j1 = last_iter['j1']
        approx = []
        
        # len(j1) + 1, because we will apply an approximation without removing any picked element
        for i in range(len(j1) + 1):
            if i is 0:
                remove = []
                z_ = last_iter['z']
                c_ = last_iter['c']
            else:
                remove = [i-1]
                p_exc, w_exc, picked_exc, ind_exc = j1[i-1]
                z_ = last_iter['z'] - p_exc
                c_ = last_iter['c'] + w_exc
                
            # find the new critical item
            j0_bound = -1
            for k in range(len(j0)):
                if j0[k][1] > c_:
                    j0_bound = k
                    break

            # find possible solutions when i'th item is ignored
            for k in reversed(range(j0_bound)):
                temp_c = c_
                temp_z = z_
                add = []
                for q in reversed(range(k+1)):
                    if temp_c >= j0[q][1]:
                        temp_z += j0[q][0]
                        temp_c -= j0[q][1]
                        add.append(q)

                changes = {}
                changes['z'] = temp_z
                changes['c'] = temp_c
                changes['remove'] = remove
                changes['add'] = add
                approx.append(changes)


        
        if len(approx) > 0:
            # find closest approximation
            max_z = 0
            max_app_ind = 0
            for index in range(len(approx)):
                if approx[index]['z'] > max_z:
                    max_z = approx[index]['z']
                    max_app_ind = index

            max_c = approx[max_app_ind]['c']
            max_remove = approx[max_app_ind]['remove']
            max_add = approx[max_app_ind]['add']

            if max_z >= iters[-1]['z']:
                for index in max_remove:
                    remove_pack = last_iter['j1'][index]
                    remove_pack[2] = 0
                    last_iter['j0'].append(remove_pack)
                    del last_iter['j1'][index]

                for index in max_add:
                    add_pack = last_iter['j0'][index]
                    add_pack[2] = 1
                    last_iter['j1'].append(add_pack)
                    del last_iter['j0'][index]

                last_iter['z'] = max_z
                last_iter['c'] = max_c
                last_iter['j0'] = sorted(last_iter['j0'], key=itemgetter(1))
                last_iter['j1'] = sorted(last_iter['j1'], key=itemgetter(1))

            # if there is no improvement in an iteration stop the algorithm
            if dbg:
                print("iters j1 len", len(iters[-1]['j1']))
                print("iters j0 len", len(iters[-1]['j0']))
                print("iters c:", iters[-1]['c'])
                print("iters z:", iters[-1]['z'])
                print("last_iter z", last_iter['z'])
            if last_iter['z'] <= iters[-1]['z']:
                if dbg:
                    print("\nBreak with no improvement.\n")
                break
            else:
                if dbg:
                    print("\nADDED TO ITERS\n")
                iters.append(last_iter)
            
        else:
            if dbg:
                print("\nBreak with approx 0.\n")
            break
    
    j0 = list(iters[-1]['j0'])
    j1 = list(iters[-1]['j1'])
    
    if not multiple:    
        z = iters[-1]['z']
        res = []
        j_all = sorted(j0 + j1, key=itemgetter(3))
        for l in j_all:
            res.append(l[2])

        if dbg:
            return iters, res
        else:
            return z, res
    else:
        j0 = sorted(j0, key=itemgetter(1))
        j1 = sorted(j1, key=itemgetter(1))
        
        j1_list = []
        total_cost = 0
        
        for cap in capacity_list:
            min_cost_cut = [] # capacity_left, picked_j1, left_j1
            
            for i in reversed(range(len(j1))):
                temp_cap = cap # capacity_left
                current_j1 = [] # picked_j1
                temp_j1 = list(j1) # left_j1
                
                for q in reversed(range(i+1)):
                    if temp_cap >= temp_j1[q][1]:
                        temp_cap -= temp_j1[q][1]
                        current_j1.append(temp_j1[q])
                        del temp_j1[q]
                if len(min_cost_cut) is 0:
                    min_cost_cut.append(temp_cap)
                    min_cost_cut.append(current_j1)
                    min_cost_cut.append(temp_j1)
                else:
                    if temp_cap < min_cost_cut[0]:
                        min_cost_cut[0] = temp_cap
                        min_cost_cut[1] = current_j1
                        min_cost_cut[2] = temp_j1
            
            total_cost += min_cost_cut[0]
            j1_list.append(min_cost_cut[1])
            j1 = list(min_cost_cut[2])
            
        # If there is an item doesn't chosen for any of the knapsacks add it to j0
        
        for item in j1:
            item[2] = 0
            j0.append(item)
            
        # Sort j0 again
        j0_final = sorted(j0, key=itemgetter(1))
        
        results = []
        
        results_j1_final = []
        
        result_profit = 0
        
        # Now, we will run the single knapsack algorithm for each knapsack
        for t in range(len(j1_list)):
            
            iters = []
            
            j1 = list(j1_list[t])
            c = capacity_list[t]
            
            z = 0
            for k in range(len(j1)):
                z += j1[k][0]
                c -= j1[k][1]
            
            init_solution = {'z': z, 'c': c, 'j0': j0_final, 'j1': j1}
            iters.append(init_solution)
            
            
            while True:
                last_iter = dict(iters[-1])
                j0 = list(last_iter['j0'])
                j1 = list(last_iter['j1'])
                
                approx = []

                # len(j1) + 1, because we will apply an approximation without removing any picked element
                for i in range(len(j1) + 1):
                    if i is 0:
                        remove = []
                        z_ = last_iter['z']
                        c_ = last_iter['c']
                    else:
                        remove = [i-1]
                        p_exc, w_exc, picked_exc, ind_exc = j1[i-1]
                        z_ = last_iter['z'] - p_exc
                        c_ = last_iter['c'] + w_exc

                    # find the new critical item
                    j0_bound = -1
                    for k in range(len(j0)):
                        if j0[k][1] > c_:
                            j0_bound = k
                            break
                    # find possible solutions when i'th item is ignored
                    for k in reversed(range(j0_bound)):
                        temp_c = c_
                        temp_z = z_
                        add = []
                        for q in reversed(range(k+1)):
                            if temp_c >= j0[q][1]:
                                temp_z += j0[q][0]
                                temp_c -= j0[q][1]
                                add.append(q)
                                
                        #print("add {}:".format(k), add)

                        changes = {}
                        changes['z'] = temp_z
                        changes['c'] = temp_c
                        changes['remove'] = list(remove)
                        changes['add'] = list(add)
                        
                        #print(k)
                        #print(changes)
                        
                        approx.append(changes)

                if len(approx) > 0:
                    # find closest approximation
                    max_z = 0
                    max_app_ind = 0
                    for index in range(len(approx)):
                        if approx[index]['z'] > max_z:
                            max_z = approx[index]['z']
                            max_app_ind = index

                    max_c = approx[max_app_ind]['c']
                    max_remove = approx[max_app_ind]['remove']
                    max_add = approx[max_app_ind]['add']

                    if max_z >= iters[-1]['z']:
                        for index in max_remove:
                            remove_pack = list(last_iter['j1'][index])
                            remove_pack[2] = 0
                            last_iter['j0'].append(remove_pack)
                            del last_iter['j1'][index]

                        for index in max_add:
                            add_pack = list(last_iter['j0'][index])
                            add_pack[2] = 1
                            last_iter['j1'].append(add_pack)
                            del last_iter['j0'][index]

                        last_iter['z'] = max_z
                        last_iter['c'] = max_c
                        last_iter['j0'] = sorted(last_iter['j0'], key=itemgetter(1))
                        last_iter['j1'] = sorted(last_iter['j1'], key=itemgetter(1))
                    
                    # if there is no improvement in an iteration stop the algorithm
                    if last_iter['z'] <= iters[-1]['z']:
                        if dbg:
                            print("\nBreak with no improvement.\n")
                        break
                    else:
                        if dbg:
                            print("\nADDED TO ITERS\n")
                        iters.append(last_iter)

                else:
                    if dbg:
                        print("\nBreak with approx 0.\n")
                    break
                    
            
            results.append(dict(iters[-1]))
            j0_final = sorted(iters[-1]['j0'], key=itemgetter(1))
               
        for i in range(len(results)):
            
            if i is len(results)-1:
                j0_final = results[i]['j0']
                
            results_j1_final.append(results[i]['j1'])
            result_profit += results[i]['z']
            
        binary_lists = []
        for i in range(len(results_j1_final)):
            binary = []
            current_j1 = sorted(results_j1_final[i], key=itemgetter(3))
            
            q = 0
            for k in range(len(current_j1)):
                if current_j1[k][3] == q:
                    binary.append(1)
                    q += 1
                else:
                    while current_j1[k][3] != q:
                        binary.append(0)
                        q += 1
                    binary.append(1)
                    q += 1
            while len(binary) < n:
                binary.append(0)
                    
            binary_lists.append(binary)
            
        return result_profit, binary_lists



if len(sys.argv) < 2:
    print("\nError: Bad input\n\nExample run:\npython kp.py input.dat")
else:
    
    whole_start = time.clock()
    
    in_file = sys.argv[1]
    out_file = 'output-' + in_file
    
    start = time.clock()
    # algorithm here
    res = kp_cmdline(in_file)
    finish = time.clock()
    
    z = res[0]
    
    # if MKP use this output format
    if isinstance(res[1][0], list):
        binary_lists = res[1]
        with open(out_file, 'w') as out:
            out.write(str(z) + '\n')
            for i in range(len(binary_lists[0])):
                line = ""
                for l in binary_lists:
                    line += str(l[i]) + ' '
                line = line.strip() + '\n'
                out.write(line)
    # if KP use this output format
    else:
        binary = res[1]
        with open(out_file, 'w') as out:
            out.write(str(z) + '\n')
            for x in binary:
                line = str(x) + '\n'
                out.write(line)
                
    whole_finish = time.clock()
    exec_time = finish - start
    exec_whole = whole_finish - whole_start
    print('\nAlgorithm execution time:\t{:.6f}s'.format(exec_time))
    print('Total execution time:\t\t{:.6f}s'.format(exec_whole))


