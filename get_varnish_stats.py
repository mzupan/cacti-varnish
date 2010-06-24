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
        
        opts, args = getopt.getopt(argv, "h:p:", ["host=", "port="])
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
    stats = {}
    
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
    hit_percent = round(((float(hits) + float(hits_pass)) / (float(hits) + float(miss) + float(hits_pass))) * 100, 1)
    
    stats['requests'] = req
    stats['cache_hits'] = hits
    stats['cache_hits_pass'] = hits_pass
    stats['cache_miss'] = miss
    stats['cache_percentage'] = str(hit_percent)
    
    #
    # pulling out the cache size usage
    #
    bytes_free = re.search("\d+  bytes allocated", out).group(0).split()[0]
    bytes_used = re.search("\d+  bytes free", out).group(0).split()[0]
    bytes_total = int(bytes_free) + int(bytes_used)
    
    stats['bytes_free'] = bytes_free
    stats['bytes_used'] = bytes_used
    stats['bytes_total'] = str(bytes_total)
    
    
    #
    # pulling out the backend info
    #
    backend_conn = re.search("\d+  Backend conn. success", out).group(0).split()[0]
    backend_unhealthy = re.search("\d+  Backend conn. not attempted", out).group(0).split()[0]
    backend_busy = re.search("\d+  Backend conn. too many", out).group(0).split()[0]
    backend_fail = re.search("\d+  Backend conn. failures", out).group(0).split()[0]
    backend_reuse = re.search("\d+  Backend conn. reuses", out).group(0).split()[0]
    backend_recycle = re.search("\d+  Backend conn. recycles", out).group(0).split()[0]
    backend_unused = re.search("\d+  Backend conn. unused", out).group(0).split()[0]
    backend_req = int(backend_conn) + int(backend_unhealthy) + int(backend_busy) + int(backend_fail) + int(backend_reuse) + int(backend_recycle) + int(backend_unused) 
    
    stats['backend_conn'] = backend_conn
    stats['backend_unhealthy'] = backend_unhealthy
    stats['backend_busy'] = backend_busy
    stats['backend_fail'] = backend_fail
    stats['backend_reuse'] = backend_reuse
    stats['backend_recycle'] = backend_recycle
    stats['backend_unused'] = backend_unused
    stats['backend_req'] = backend_req
    
    
    #
    # pulling out all the thread information
    #
    threads_created = re.search("\d+  N worker threads created", out).group(0).split()[0]
    threads_running = re.search("\d+  N worker threads", out).group(0).split()[0]
    threads_not_created = re.search("\d+  N worker threads not created", out).group(0).split()[0]
    queued_requests = re.search("\d+  N queued work requests", out).group(0).split()[0]
    
    stats['threads_created'] = threads_created
    stats['threads_running'] = threads_running
    stats['threads_not_created'] = threads_not_created
    stats['queued_requests'] = queued_requests
    
    #
    # getting total bytes sent to client
    #
    sent_header = re.search("\d+  Total header bytes", out).group(0).split()[0]
    sent_body = re.search("\d+  Total body bytes", out).group(0).split()[0]
    sent_total = int(sent_header) + int(sent_body)
    
    stats['sent_header'] = sent_header
    stats['sent_body'] = sent_body
    stats['sent_total'] = str(sent_total)
    
    
    #
    # iterate through the dictionary
    #
    out = ""
    for k,v in stats.items():
        out = "%s:%s %s" % (k,v,out)

    print out
if __name__ == "__main__":
    main(sys.argv[1:])