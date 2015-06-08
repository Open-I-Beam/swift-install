# --------------------------------------------------------------------------
# Copyright IBM Corp. 2015, 2015 All Rights Reserved
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# Limitations under the License.
# --------------------------------------------------------------------------
# Written By George Goldberg (georgeg@il.ibm.com)


def get_dict_path(d, path):
    l = d
    name = path
    for i in path.split('.'):
        l = l[i]
        name = i

    return (name, l)


def set_dict_path(d, path, v):
    l = d
    lst = path.split('.')
    spath = lst[:-1]
    entry = lst[-1]
    for i in spath:
        if i not in l:
            l[i] = {}
        l = l[i]

    l[entry] = v


def extractfromdict(d, l):
    r = []
    for f in l:
        r.append(get_dict_path(d, f)[1])
    return r

def extractfromlist(l, name):
    r = []
    for f in l:
        r.append(f[name])
    return r    


def dictrearrange(d, vals):
    o = {}
    for opath, dpath in vals.iteritems():
        [_, v] = get_dict_path(d, dpath)
        set_dict_path(o, opath, v)
    return o


def propagatevalue(d, listpath, dname, vals):
    r = []
    [_dname, lst] = get_dict_path(d, listpath)
    v = dictrearrange(d, vals)
    for f in lst:
        dd = {dname: f}
        dd.update(v)
        r.append(dd)
    return r


def addfield(l, p, v):
    r = []
    lst = p.split('.')
    path = lst[:-1]
    entry = lst[-1]
    for f in l:
        c = f.copy()
        cc = c
        for i in path:
            cc = cc[i]
        cc[entry] = v
        r.append(c)

    return r


def listflatten(l):
    r = []
    for f in l:
        r.extend(f)

    return r


class FilterModule(object):

    def filters(self):
        return {
            'extractfromdict': extractfromdict,
            'extractfromlist': extractfromlist,
            'propagatevalue': propagatevalue,
            'listflatten': listflatten,
            'addfield': addfield,
        }
