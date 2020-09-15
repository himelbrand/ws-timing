import os
import sys
import datetime
import pause
import argparse

def time_query(q):
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    # os.system('sudo systemd-resolve --flush-caches')
    cmd = 'googler --np {}'.format(q) 
    try:
        split = os.popen(cmd).read().split('\n')
        google_time = split[1]
        fetch_time = split[0]
    except: #timed out 3 times
        google_time = -1
        fetch_time = -1
    return '{}\t{}\t{}\t{}\n'.format(q,google_time,fetch_time,dt_string)
    

def main(start,end,part,filename,samples):
    f = open(filename)
    lines = f.readlines()
    f.close()
    i = 1
    lines = [line.strip() for line in lines[start:end]]
    now = datetime.datetime.now()
    with open('{}.queries{}.times'.format(now.strftime('%Y%h%d_%H:%M'),part), 'w') as f:
        for query in lines:
            for _ in range(samples):
                line = time_query(query)
                f.write(line)
                i += 1
                if i%100 == 0:
                    f.flush()

def parse_args():
    parser = argparse.ArgumentParser(prog='ws-timing.py',description='Collects query resolving times from google, by a list of queries.')
    parser.add_argument('max_vm',  type=int,help='a positive integer for the max number of vms.')
    parser.add_argument('vm', type=int,help='an integer for the vm number.')
    parser.add_argument('iters', type=int, help='number of iterations to run the script over the segment of urls.')
    parser.add_argument('-input', dest='input', default='aol_queries',help='path to input file containing queries to time (default: "aol_queries").')
    parser.add_argument('-dd',dest='days', metavar='D',default=1, type=int, help='an integer for the iteration delay in days (default: 1).')
    parser.add_argument('-hd',dest='hours', metavar='H',default=1, type=int, help='an integer for the iteration delay in hours (default: 1).')
    parser.add_argument('-s',dest='samples',default=3,type=int, help='an integer defining how many time smpales for each query (default: 3)')
    args = parser.parse_args()
    if args.max_vm <= 0:
        raise argparse.ArgumentTypeError(f'{args.max_vm} is an invalid positive integer.')
    if not (1 <= args.vm <= args.max_vm):
        raise argparse.ArgumentTypeError(f'{args.vm} is an invalid vm number, must be an integer between 1 and {args.max_vm}.')
    if args.max_vm <= 0:
        raise argparse.ArgumentTypeError(f'{args.iters} is an invalid positive integer.')
    return args

def get_queries_count(filename):
    f = open(filename)
    lines = f.readlines()
    f.close()
    return len(lines)

if __name__ == '__main__':
    args = parse_args()
    q_count = get_queries_count(args.input)
    partition_size = int(q_count//args.max_vm)
    start = (args.vm-1)*partition_size
    end = start + partition_size if args.vm < args.max_vm else int(q_count+1)
    i = 0
    while i < args.iters:
        start_time = datetime.datetime.now()
        main(start,end,args.vm,args.input,args.samples)
        start_time += datetime.timedelta(days=args.days,hours=args.hours)
        pause.until(start_time)
        i+=1
