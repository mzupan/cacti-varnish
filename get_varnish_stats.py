#!/usr/bin/env python

#
# header should go here
#

import sys
import getopt
import telnetlib
import re

def main(argv):
    try:
        if len(argv) == 0:
            usage()
            sys.exit(2)
        
        opts, args = getopt.getopt(argv, "h:p:a:", ["host=", "port="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    #
    # defaults
    #
    host = "127.0.0.1"
    port = 6082

    for opt, arg in opts:
        if opt in ("-h", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = int(arg)

    get_stats(host, port)


def get_stats(host, port):
    telnet = telnetlib.Telnet()
    telnet.open(host, port)
    telnet.write('stats\r\n')

    out = telnet.read_until("N duplicate purges", 10)
    
    telnet.write('quit\r\n')
    telnet.close()
    
    #
    # pulling out the hit/miss stats
    #
    req = re.search("\d+  Client requests received", out).group(0).split()[0]
    hits = re.search("\d+  Cache hits", out).group(0).split()[0]
    hits_pass = re.search("\d+  Cache hits for pass", out).group(0).split()[0]
    miss = re.search("\d+  Cache misses", out).group(0).split()[0]
    hit_percent = round((float(hits) + float(hits_pass) / (float(hits) + float(miss) + float(hits_pass))) * 100, 1)
    
    
    
    print "requests:"+ req +" cache_hits:"+ hits +" cache_hits_pass:"+ hits_pass +" cache_miss:"+ miss

if __name__ == "__main__":
    main(sys.argv[1:])