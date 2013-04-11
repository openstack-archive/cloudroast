"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class perf_parser(object):
    def __init__(self, from_log_name):
        self.f_log_name = from_log_name

    def parse_log(self):

        all_stats = ['approx.  95 percentile',
                     'total number of events',
                     'avg',
                     'read',
                     'write',
                     'other',
                     'transactions',
                     'deadlocks',
                     'total time',
                     'total',
                     'min',
                     'other operations',
                     'Number of threads',
                     'max', 'events (avg/stddev)',
                     'read/write requests',
                     'execution time (avg/stddev)']
        parse_per_sec = ['other operations',
                         'transactions',
                         'deadlocks',
                         'read/write requests']
        parse_avg_stddev = ['execution time (avg/stddev)',
                            'events (avg/stddev)']

        #csv = True
        f = open(self.f_log_name, 'r')
        d = {}
        stats_dict = {}
        for line in f:
            l = line.rstrip("\n")
            #l = line.split("run_command")
            # if len(l) > 1:
            #     l = l.pop(1)
            l = str(l)
            l = l.split(":")
            if len(l) == 2:
                d[l[0].strip()] = l[1].strip()
            #Iterate through all of the items
        for k, v in d.iteritems():
            if k in all_stats:
                v = v.rstrip('ms')
                #Iterate through the Per Second Data
                if k in parse_per_sec:
                    pri = self.get_pri_cnt(v)
                    per_sec = self.get_per_sec(v)
                    stats_dict[k] = pri
                    #to_log.log(k + "," + pri, csv = True)
                    stats_dict[k + " per sec"] = per_sec
                    #to_log.log(k + " per sec," + per_sec, csv)
                #Iterate through the Avg StdDev data
                if k in parse_avg_stddev:
                    avg = self.parse_avg_stddev(v, 'avg')
                    stddev = self.parse_avg_stddev(v, 'stddev')
                    title = self.parse_avg_stddev_name(k)
                    stats_dict[title.strip() + " avg"] = avg
                    #to_log.log(title.strip() + " avg," + avg, csv)
                    stats_dict[title.strip() + " stddev"] = stddev
                    #to_log.log(title.strip() + " stddev," + stddev, csv)
                #Handle anything that is left
                if (k not in parse_avg_stddev) and (k not in parse_per_sec):
                    stats_dict[k] = v
                    #to_log.log(k + "," + v, csv)
            #print stats_dict
        return stats_dict

    def get_per_sec(self, field):
        fl = field.split("(")
        fl = fl[1]
        fl = fl.split(" ")
        fl = fl[0]
        return fl

    def get_pri_cnt(self, field):
        fl = field.split("(")
        fl = fl[0].strip()
        return fl

    def parse_avg_stddev(self, field, type):
        #print field
        if type == 'avg':
            i = 0
        elif type == 'stddev':
            i = 1
        fl = field.split("/")
        return fl[i]

    def parse_avg_stddev_name(self, field):
        fl = field.split("(")
        return fl[0]
