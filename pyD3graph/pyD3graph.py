import os, webbrowser
from .network import netCreate
from .utils import isnumeric, transpose
from tempfile import mkdtemp
from statistics import mean, median
from copy import deepcopy

class pyD3graph:

  def __init__(self,
      nodes = None,
      links = None,
      nodeAttrNames = None,
      linkAttrNames = None,
      tree = None,
      name = None,
      label = None,
      labelSize = None,
      size = None,
      color = None,
      shape = None,
      legend = None,
      ntext = None,
      info = None,
      orderA = None,
      orderD = None,
      group = None,
      source = "Source",
      target = "Target",
      lwidth = None,
      lweight = None,
      lcolor = None,
      ltext = None,
      nodeFilter = None,
      linkFilter = None,
      degreeFilter = None,
      nodeBipolar = False,
      linkBipolar = False,
      defaultColor = "#1f77b4",
      repulsion = 25,
      distance = 10,
      zoom = 1,
      scenarios = None,
      main = None,
      note = None,
      help = None,
      helpOn = False,
      cex = 1,
      background = None,
      layout = None,
      limits = None,
      controls = [1,2,3,4,5],
      mode = ["network","heatmap"],
      showCoordinates = False,
      showArrows = False,
      showLegend = True,
      showAxes = False,
      axesLabels = None,
      language = 'en',
      image = None,
      imageNames = None,
      directory = None):
    '''Create pyD3graph object

    @keyword nodes: the attributes of the nodes as a dictionary.
    @keyword links: the attributes of the links as a dictionary.
    @keyword nodeAttrNames: list of node attributes.
    @keyword linkAttrNames: list of link attributes.
    @keyword tree: list where every list item is a pair of names describing
      relationships between nodes.
    @keyword name: name of the node attribute with names. By default, if
      I{language} is 'en', I{name} is 'name'.
    @keyword label: name of the node attribute with labels.
    @keyword labelSize: name of the node attribute with label sizes.
    @keyword size: name of the node attribute with sizes.
    @keyword color: name of the node attribute with colors.
    @keyword shape: name of the node attribute with shapes.
    @keyword legend: name of the node attribute to represent as a legend.
    @keyword ntext: name of the node attribute with html text.
    @keyword info: name of the node attribute with information to display in
      a panel.
    @keyword orderA: name of the node attribute with ascending order.
    @keyword orderD: name of the node attribute with descending order.
    @keyword group: name of the node attribute with groups.
    @keyword lwidth: name of the link attribute with line widths.
    @keyword lweight: name of the link attribute with weights.
    @keyword lcolor: name of the link attribute with line colors.
    @keyword ltext: name of the link attribute with texts.
    @keyword nodeFilter: boolean list to filter nodes.
    @keyword linkFilter: boolean list to filter links.
    @keyword degreeFilter: numeric value to filter the resulting network by
      degree.
    @keyword nodeBipolar: logical value that polarizes negative and positive
      node values in the graphical representation. C{False} by default.
    @keyword linkBipolar: logical value that polarizes negative and positive
      link values in the graphical representation. C{False} by default.
    @keyword defaultColor: string giving a valid html color.
    @keyword repulsion: percentage for repulsion between nodes.
    @keyword distance: percentage for distance of links.
    @keyword zoom: value between 0.1 and 10 to start displaying zoom.
    @keyword scenarios: a note showing number of scenarios.
    @keyword main: upper title of the graph.
    @keyword note: lower title of the graph.
    @keyword help: help text of the graph.
    @keyword helpOn: should the help be shown at the beginning?
    @keyword background: background color or image of the graph.
    @keyword layout: a matrix with two columns or an algorithm to elaborate the
      coordinates: 'auto', 'bipartite', 'circle', 'drl',
      'fruchterman_reingold', 'grid', 'kamada_kawai', 'lgl', 'mds', 'random',
      'reingold_tilford', 'star', 'sphere', 'sugiyama'.
    @keyword limits: list indicating size references to display layout, must be
      a numeric list of length 4: x1, y1, x2, y2.
    @keyword controls: a numeric list indicating which controls will be shown.
      1 = sidebar, 2 = selection buttons, 3 = tables, 4 = sliders & buttons,
      5 = export buttons. C{None} hide all controls, negative values deny each
      control and 0 deny all.
    @keyword mode: list of strings indicating the graph mode allowed: network,
      heatmap or both (both by default).
    @keyword showCoordinates: logical value C{True} if the coordinates are to
      be shown in tables. C{False} by default.
    @keyword showArrows: logical value C{True} if directional arrows are to be
      shown. C{False} by default.
    @keyword showLegend: logical value C{True} if the legend is to be shown.
      C{True} by default.
    @keyword showAxes: logical value C{True} if the axes are to be shown.
      C{False} by default.
    @keyword axesLabels: list of axes names.
    @keyword image: name of the node attribute with image files.
    @keyword imageNames: name of the node attribute with names for image
      files.
    @keyword directory: string representing the directory where the web files
      will be saved.
    '''

    if not name:
      name = getByLanguage(nameList,language)

    self.options = {'nodeName':name}
    
    def str2float(x):
      if type(x) is str:
        try:
          x = float(x)
          if(x.is_integer()):
            x = int(x)
        except ValueError:
          pass
      return x

    def checkItem(x,limit):
      x = list(map(str2float,x))
      if len(x) > limit:
        x = x[:limit]
      if len(x) < limit:
        if isnumeric(x):
          fill = 0
        else:
          fill = ''
        while len(x) < limit:
          x.append(fill)
      return x

    self.nodes = {}
    if nodes:
      if name not in nodes.keys():
        raise Exception('"' + name + '" must be in nodes')
      self.nodes[name] = list(map(str,nodes[name]))
      nnodes = len(nodes[name])
      for k in nodes.keys():
        if k!=name:
          self.nodes[k] = checkItem(nodes[k],nnodes)

    self.links = {}
    if links:
      if source not in links.keys():
        raise Exception('"' + source + '" must be in links')
      if target not in links.keys():
        raise Exception('"' + target + '" must be in links')
      self.options['linkSource'] = source
      self.options['linkTarget'] = target
      nlinks = len(links[source])
      if len(links[target]) != nlinks:
        raise Exception('"' + source + '" and "' + target + '" must have the same length')
      for k in links.keys():
        if k in [source,target]:
          if isnumeric(links[k]):
            if not nodes:
              self.links[k] = list(map(lambda x: 'node'+str(int(x)),links[k]))
            else:
              self.links[k] = list(map(lambda x: self.nodes[name][int(x)-1],links[k]))
          else:
            self.links[k] = list(map(str,links[k]))
        else:
          self.links[k] = checkItem(links[k],nlinks)
      if not nodes:
        self.nodes[name] = list(set(self.links[source]) | set(self.links[target]))

    if tree:
      tree = checkTree(tree,self.nodes[name])
      self.tree = tree

    # graph options
    self.options["cex"] = 1
    if isnumeric(cex):
      self.options["cex"] = cex
    else:
      print("cex: must be numeric")
    if isnumeric(repulsion) and repulsion>=0 and repulsion<=100:
      self.options["repulsion"] = repulsion
    else:
      print("repulsion: must be numeric between 0 and 100")
    if isnumeric(distance) and distance>=0 and distance<=100:
      self.options["distance"] = distance
    else:
      print("distance: must be numeric between 0 and 100")
    if isnumeric(zoom) and zoom>=0.1 and zoom<=10:
      self.options["zoom"] = zoom
    else:
      print("zoom: must be numeric between 0.1 and 10")
    if scenarios:
      if isnumeric(scenarios):
        self.options["scenarios"] = scenarios
      else:
        print("scenarios: must be numeric")
    if limits:
      if type(limits) is not list or len(limits) != 4:
        print("limits: must be a numeric list of length 4")
      else:
        self.options["limits"] = list(map(lambda x: float(x), limits))

    if main:
      self.options["main"] = main
    if note:
      self.options["note"] = note
    if help:
      self.options["help"] = help
    if background:
      self.options["background"] = background
    if language:
      self.options["language"] = language

    if nodeBipolar:
      self.options["nodeBipolar"] = True
    if linkBipolar:
      self.options["linkBipolar"] = True
    if helpOn:
      self.options["helpOn"] = True
    if defaultColor:
      self.options["defaultColor"] = defaultColor
    if controls:
      if type(controls) is not list:
        self.options["controls"] = int(controls)
      else:
        self.options["controls"] = [int(x) for x in controls]
    if mode:
      getFirst = lambda x: x[0:1].lower()
      if type(mode) is list:
        self.options["mode"] = list(map(getFirst, mode))
      else:
        self.options["mode"] = getFirst(mode)
    if axesLabels:
      if type(axesLabels) is not list:
        self.options["axesLabels"] = [str(axesLabels)]
      else:
        self.options["axesLabels"] = list(map(lambda x: str(x), axesLabels))

    if showCoordinates:
      self.options["showCoordinates"] = True
    if showArrows:
      self.options["showArrows"] = True
    if showLegend:
      self.options["showLegend"] = True
    if showAxes:
      self.options["showAxes"] = True

    # node options
    if label is None:
        self.options["nodeLabel"] = name
    elif label != "":
        self.options["nodeLabel"] = label
    if labelSize:
      self.options["nodeLabelSize"] = labelSize
    if group:
      self.options["nodeGroup"] = group
    if size:
      self.options["nodeSize"] = size
    if color:
      self.options["nodeColor"] = color
    if shape:
      self.options["nodeShape"] = shape
    if legend:
      self.options["nodeLegend"] = legend
    if ntext:
      self.options["nodeText"] = ntext
    if info:
      self.options["nodeInfo"] = info
    if orderA:
      self.options["nodeOrderA"] = orderA
    if orderD:
      self.options["nodeOrderD"] = orderD
    if image:
      self.options["imageItems"] = image
      if imageNames:
        self.options["imageNames"] = imageNames

    # link options
    if lwidth:
      self.options ["linkWidth"] = lwidth
    if lweight:
      self.options["linkWeight"] = lweight
    if lcolor:
      self.options["linkColor"] = lcolor
    if ltext:
      self.options["linkText"] = ltext

    # filters
    if nodeFilter and type(nodeFilter) is list and len(nodeFilter)==self.ncount():
      self.nodes['hidden'] = list(map(lambda x: not x, nodeFilter))

    if linkFilter and type(linkFilter) is list and len(linkFilter)==self.lcount():
      self.links['hidden'] = list(map(lambda x: not x, linkFilter))

    #if degreeFilter:
    #  self.options["degreeFilter"] = degreeFilter

    # layout
    if layout:
      if type(layout) is list:
        layout = transpose(layout)
        self.nodes["fx"] = layout[0]
        self.nodes["fy"] = layout[1]
      else:
        print("layout must be a matrix")

    # attribute names
    if nodeAttrNames:
      if name not in nodeAttrNames:
        nodeAttrNames = [name] + nodeAttrNames
      self.nodeAttrNames = nodeAttrNames

    if linkAttrNames:
      if (source not in linkAttrNames) or (target not in linkAttrNames):
        linkAttrNames = [source, target] + [x for x in linkAttrNames if x not in [source, target]]
      self.linkAttrNames = linkAttrNames

    if directory:
      netCreate(self,directory)

  def getNodeAttr(self):
    nodekeys = list(self.nodes.keys())
    if hasattr(self,'nodeAttrNames'):
      return [x for x in self.nodeAttrNames if x in nodekeys] + [x for x in nodekeys if x not in self.nodeAttrNames]
    else:
      return nodekeys

  def getLinkAttr(self):
    linkkeys = list(self.links.keys())
    if hasattr(self,'linkAttrNames'):
      return [x for x in self.linkAttrNames if x in linkkeys] + [x for x in linkkeys if x not in self.linkAttrNames]
    else:
      return linkkeys

  def ncount(self):
    return len(self.nodes[self.options['nodeName']])

  def lcount(self):
    if 'linkSource' in self.options:
      return len(self.links[self.options['linkSource']])
    else:
      return 0

  def getNet(self):
    '''Extract net from pyD3graph object'''
    net = {'options': deepcopy(self.options)}
    if hasattr(self,'tree'):
      net['tree'] = deepcopy(self.tree)
    net['nodeAttrNames'] = self.getNodeAttr()
    net['linkAttrNames'] = self.getLinkAttr()

    net['nodes'] = deepcopy(self.nodes)
    net['links'] = deepcopy(self.links)

    def getIndex(x):
      return net['nodes'][net['options']['nodeName']].index(x)

    if self.lcount():
      net['links'][net['options']['linkSource']] = list(map(getIndex,net['links'][net['options']['linkSource']]))
      net['links'][net['options']['linkTarget']] = list(map(getIndex,net['links'][net['options']['linkTarget']]))

    return net


  def __str__(self):
      """Returns a string representation of the graph."""
      output = []

      if 'main' in self.options:
        output.append("Title: " + self.options['main'])
        output.append("")

      columns = self.getNodeAttr()
      row_format ="{:>15}" * (len(columns))
      output.append(row_format.format(*columns))
      count = min(self.ncount(),6)
      for i in range(count):
        row = map(lambda x: str(self.nodes[x][i]),columns)
        output.append(row_format.format(*row))
      if self.ncount()>6:
        output.append("...")
      output.append("")

      columns = self.getLinkAttr()
      row_format ="{:>15}" * (len(columns))
      output.append(row_format.format(*columns))
      count = min(self.lcount(),6)
      for i in range(count):
        row = list(map(lambda x: str(self.links[x][i]),columns))
        output.append(row_format.format(*row))
      if self.lcount()>6:
        output.append("...")
      output.append("")

      if 'note' in self.options:
        output.append(self.options['note'])
        output.append("")

      return "\n".join(output)


  def summary(self):
      """Prints the summary of the graph."""
      output = []
      output.append(str(self.ncount())+" nodes and "+str(self.lcount())+" links.")

      stats = ["Min","Median","Mean","Max"]
      row_format ="{:>15}" * len(stats)
      freq = set(frequencyList) & set(self.nodes.keys())
      if len(freq)==1:
        freq = list(freq)[0]
        output.append(freq+' distribution of nodes:')
        freq = self.nodes[freq]
        freq = list(map(lambda x: str(round(x,2)),[min(freq),median(freq),mean(freq),max(freq)]))
        output.append(row_format.format(*stats))
        output.append(row_format.format(*freq))

      if 'linkWidth' in self.options:
        lwidth = self.options['linkWidth']
        output.append(lwidth+'\'s distribution:')
        lwidth = self.links[lwidth]
        lwidth = list(map(lambda x: str(round(x,2)),[min(lwidth),median(lwidth),mean(lwidth),max(lwidth)]))
        output.append(row_format.format(*stats))
        output.append(row_format.format(*lwidth))
      
      print("\n".join(output))


  def plot(self, directory = None):
      """Displays the graph in a web browser.

      @param directory: string representing the directory where the web files
      will be saved.
      """
      if not directory:
        directory = mkdtemp()
      netCreate(self,directory)
      webbrowser.open(os.path.join(directory,'index.html'))


  @classmethod
  def fromMatrix(klass, *args, **kwds):
        """Constructs a graph from a matrix representation.

        This representation assumes that the links of the graph are encoded
        in a matrix (list of tuples or lists). Each item in the list must have
        at least two elements, which specify the numeric index (one-based) of
        the source and the target nodes of the link. The remaining elements
        (if any) specify the link attributes of that link, where the names of
        the link attributes originate from the C{linkAttrNames} list.

        @param matrix: the data source for the links. This must be a list
          where each item is a tuple (or list) containing at least two
          items: the index (one-based) of the source and the target node.
        @return: the graph that was constructed
        """

        if 'matrix' in kwds:
          matrix = kwds['matrix']
        else:
          args = list(args)
          if len(args):
            matrix = args[0]

        # Check matrix
        lengths = set(map(lambda x: len(x),matrix))
        if len(lengths)==1:
          n = list(lengths)[0]
          if n < 2:
            raise Exception("'matrix' must have at least two items")
        else:
          raise Exception("all rows in 'matrix' must have the same length")

        # Check attribute names
        linkAttrNames = None
        if 'linkAttrNames' in kwds and type(kwds['linkAttrNames']) is list and len(kwds['linkAttrNames'])>=2:
          linkAttrNames = kwds['linkAttrNames']
          if len(linkAttrNames)>n:
            linkAttrNames = linkAttrNames[:n]
        if not linkAttrNames:
          linkAttrNames = list(map(lambda x: 'attr'+str(x-1),range(n)))
          linkAttrNames[:2] = ['Source','Target']
        kwds['source'], kwds['target'] = linkAttrNames[:2]
        kwds['linkAttrNames'] = linkAttrNames

        # Construct the links
        links = {}
        matrix = transpose(matrix)
        for index, item in enumerate(linkAttrNames):
          links[item] = matrix[index]

        kwds['links'] = links

        # Construct the graph
        return klass(**kwds)


languages = ['en','es','ca']

nameList = ['name','nombre','nom']
nameList = dict(zip(languages,nameList))

frequencyList = ["frequency","frecuencia","freq\u00FC\u00E8ncia","%"]

def getByLanguage(varlist,language):
  if language not in varlist:
    language = "en"
  return varlist[language]

def checkTree(links,names):
      if links:
        i = 0
        while i < len(links):
          if not ((links[i][0] in names) and (links[i][1] in names)):
            del links[i]
          else:
            i += 1
        if i==0:
          print("tree: any pair matches properly vertex names")
          return None
      return links

