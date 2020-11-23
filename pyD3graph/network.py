import os, re
from shutil import copyfile
from .utils import createHTML, getLanguageScript, transpose

def networkJSON(net):
  #prepare json
  links = net['links']
  nodes = net['nodes']
  options = net['options']

  nodes[options['nodeName']] = list(map(str,nodes[options['nodeName']]))

  tree = None
  if 'tree' in net:
    tree = net['tree']
    nlinks = len(tree)
    name = nodes[options['nodeName']]

    tree = transpose(tree)
    for i in range(nlinks):
      for j in range(2):
        tree[j][i] = name.index(str(tree[j][i]))

    checkdup = tree[1]
    if len(tree)>2:
      checkdup = list(map(lambda x: str(x[1])+str(x[2]),tree))

    if len(set(checkdup))!=len(checkdup):
      tree = None
      print("tree: there must be only one parent per node")

  def getNames(items,itemnames):
    allnames = list(items.keys())
    if itemnames in net:
      names = net[itemnames]
      for i in allnames:
        if i not in names:
          names.append(i)
    else:
      names = allnames
    return names
    
  nodenames = net['nodeAttrNames']
  nodes = list(map(lambda x: nodes[x],nodenames))
  data = {'nodes': nodes, 'nodenames': nodenames}
  if links is not None:
    linknames = net['linkAttrNames']
    links = list(map(lambda x: links[x],linknames))
    data['links'] = links
    data['linknames'] = linknames

  if tree is not None:
    data['tree'] = tree
  data['options'] = options
  
  return data


def getRawName(filepath):
  filename = os.path.basename(filepath).split(".")
  ext = filename[-1]
  filename = ".".join(filename[:-1])
  return filename.encode("utf-8").hex() + "." + ext


def netWrapper(net,directory):
  if type(net).__name__=="pyD3graph":
    net = net.getNet()

  #copy images to net
  imgDir = os.path.join(directory,"images")
  if 'imageItems' in net['options']:
    if not os.path.exists(imgDir):
      os.mkdir(imgDir)
    if type(net['options']['imageItems']) is not list:
      net['options']['imageItems'] = [net['options']['imageItems']]
    if 'imageNames' not in net['options']:
      net['options']['imageNames'] = net['options']['imageItems']
      net['options']['imageItems'] = list(map(lambda x: x+"_url",net['options']['imageItems']))
      if 'nodeAttrNames' in net:
        for i in net['options']['imageItems']:
          net['nodeAttrNames'].append(i)
      regex = re.compile(r"\.[a-zA-Z0-9]+$")
      for i in range(len(net['options']['imageItems'])):
        net['nodes'][net['options']['imageItems'][i]] = net['nodes'][net['options']['imageNames'][i]]
        net['nodes'][net['options']['imageNames'][i]] = list(map(lambda x: re.sub(regex,"",os.path.basename(x)), net['nodes'][net['options']['imageNames'][i]]))

    def copyImage(filepath):
      rawname = getRawName(filepath)
      copyfile(filepath, os.path.join(imgDir,rawname))
      return os.path.join("images",rawname)

    for img in net['options']['imageItems']:
      net['nodes'][img] = list(map(copyImage,net['nodes'][img]))

  if 'background' in net['options']:
    if os.path.isfile(net['options']['background']):
      filepath = net['options']['background']
      rawname = getRawName(filepath)
      if not os.path.exists(imgDir):
        os.mkdir(imgDir)
      copyfile(filepath, os.path.join(imgDir,rawname))
      net['options']['background'] = 'url("'+os.path.join("images",rawname)+'")'

  return networkJSON(net)


def netCreate(graph, directory):
  #create html wrapper for network graph
  language = getLanguageScript(graph)
  if not language:
    language = "en.js"

  createHTML(directory, ["reset.css","styles.css","d3.min.js","jspdf.min.js","jszip.min.js","iro.min.js","functions.js",language,"colorScales.js","network.js"],lambda: netWrapper(graph,directory))

