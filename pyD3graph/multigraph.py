import os, webbrowser
from shutil import copytree
from .utils import createHTML, getLanguageScript
from .network import netWrapper, netCreate
from .pyD3graph import pyD3graph

# create json for multigraph
def multigraphJSON(graphs,names,directory):
  #prepare json
  json = []
  types = []
  items = []
  for i,item in enumerate(names):
    graph = graphs[i]
    gClass = type(graph).__name__
    jsongraph = {}
    if gClass == 'pyD3graph':
      jsongraph = netWrapper(graph,directory)
    elif gClass == 'str' and os.path.isfile(os.path.join(graph,'index.html')):
      gClass = 'iFrame'
      graphName = os.path.basename(graph)
      copytree(graph,os.path.join(directory,'data',graphName))
      jsongraph = 'data/'+graphName
    else:
      print("Object of class '"+gClass+"' not supported")
      continue
    json.append(jsongraph)
    types.append(gClass)
    items.append(item)

  return {'items':items,'types':types,'data':json}

def multiGraph(graphs,names,directory):
  language = set(map(getLanguageScript, graphs))
  language.discard(None)
  if len(language)!=1:
    language = "en.js"
  else:
    language = list(language)[0]

  createHTML(directory, ["reset.css","styles.css","d3.min.js","jspdf.min.js","jszip.min.js","iro.min.js","functions.js",language,"colorScales.js","multigraph.js","network.js","barplot.js","timeline.js"], lambda: multigraphJSON(graphs,names,directory))

def polyGraph(graphs,names,directory):
  createHTML(directory, ["polygraph.js"], None)
  multiGraph(graphs,names,os.path.join(directory,"multiGraph"))

def frameGraph(graphs,names,directory):
  classes = set(map(lambda x: type(x).__name__, graphs))
  if len(classes)!=1 or 'pyD3graph' not in classes:
    raise Exception("All graphs must be 'pyD3graph' objects")

  name = graphs[0].options['nodeName']
  source = graphs[0].options['linkSource']
  target = graphs[0].options['linkTarget']

  def compareLists(a,b):
    aa = set(a)
    bb = set(b)
    if len(aa.difference(bb))==0 and len(bb.difference(aa))==0:
      return True
    return False

  nodenames = graphs[0].getNodeAttr()
  linknames = graphs[0].getLinkAttr()
  multi = []
  for g in graphs:
    if g.lcount()==0:
      raise Exception("links: all graphs must have links")
    if not compareLists(nodenames,g.getNodeAttr()):
      raise Exception("nodes: all graphs must have the same node columns")
    if not compareLists(linknames,g.getLinkAttr()):
      raise Exception("links: all graphs must have the same link columns")
    if name!=g.options['nodeName']:
      raise Exception("name: all graphs must have the same name")
    if source!=g.options['linkSource']:
      raise Exception("source: all graphs must have the same source")
    if target!=g.options['linkTarget']:
      raise Exception("target: all graphs must have the same target")
    multi.append(g.getNet())

  linknames.append("_frame_")
  links = {}
  for k in linknames:
    links[k] = []
  for i in range(len(names)):
    nlinks = len(multi[i]['links'][source])
    for k in linknames:
      if k in [source,target]:
        links[k].extend(list(map(lambda x: multi[i]['nodes'][name][x], multi[i]['links'][k])))
      elif k=="_frame_":
        links[k].extend([i]*nlinks)
      else:
        links[k].extend(multi[i]['links'][k])

  nodes = {}
  nodes[name] = list(set([item for sublist in map(lambda x: x['nodes'][name],multi) for item in sublist]))
  for n in nodenames:
    if n!=name:
      nodes[n] = [None]*len(nodes[name])
      for x,nam in enumerate(nodes[name]):
        def getValues(f):
          try:
            return multi[f]['nodes'][n][multi[f]['nodes'][name].index(nam)]
          except:
            return None
        values = list(map(getValues, range(len(names))))
        aux = set(values)
        aux.discard(None)
        if len(aux)<2:
          if len(aux)==1:
            nodes[n][x] = list(aux)[0]
          continue
        for i,val in enumerate(values):
          if val:
            values[i] = str(val)
          else:
            values[i] = ''
        nodes[n][x] = '|'.join(values)

  for k in [source,target]:
    links[k] = list(map(lambda x: nodes[name].index(x), links[k]))

  options = multi[0]['options']

  def getAll(item):
    items = []
    for x in multi:
      if item in x['options']:
        items.append(x['options'][item])
      else:
        items.append(None)
    if len(set(items))!=1:
      options[item] = items

  for item in ["main","note","repulsion","distance","zoom"]:
    getAll(item)
  options['frames'] = names
  net = {'links':links,'nodes':nodes,'nodeAttrNames':nodenames,'linkAttrNames':linknames,'options':options}

  tree = []
  for i in range(len(names)):
    if 'tree' in multi[i]:
      for j in multi[i]['tree']:
        tree.append(j+[i])
  if len(tree)!=0:
    net['tree'] = tree

  netCreate(net,directory)


#create html wrapper for multigraph
def multigraphCreate(graphs, names = None,  mode = ["default","parallel","frame"], directory = "MultiGraph", show = True):
  if not graphs or type(graphs) is not list:
    raise Exception("graphs: must be a non-empty list")

  if names and len(names)!=len(graphs):
    print("names: length must match with 'graphs' length")
    names = None    
  if not names:
    print("Graph names will be generated automatically")
    names = list(map(lambda x: "graph"+str(x+1),range(len(graphs))))

  if type(mode) is list:
    mode = mode[0]
  mode = mode[0]

  if mode=="f" and len(graphs)==1:
    mode = "d"
    print("Cannot make a dynamic graph with only one graph")

  if mode=="p":
    polyGraph(graphs,names,directory)
  elif mode=="f":
    frameGraph(graphs,names,directory)
  else:
    multiGraph(graphs,names,directory)
  
  if show:
    webbrowser.open(os.path.join(directory,'index.html'))

