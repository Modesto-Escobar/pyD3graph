import os, shutil, re, json

www = os.path.join(os.path.dirname(__file__), 'www')

def createHTML(directory, dependencies, data):
  if os.path.exists(directory):
    shutil.rmtree(directory)
  os.makedirs(directory)
  html = open(os.path.join(www, 'template.html')).read()
  name = directory.split(os.sep)[-1]
  html = html.replace('titulo', name)
  dep = ''
  for depend in dependencies:
    dirName = ''
    if re.search(".css$",depend):
      dep = dep + "\n" + '<link rel="stylesheet" type="text/css" href="styles/' + depend + '"></link>'
      dirName = os.path.join(directory,'styles')
      if depend=="styles.css":
        for font in ("Roboto-Regular-latin.woff2","Roboto-Regular-latin-ext.woff2"):
          shutil.copy(os.path.join(www,font), dirName)
    else:
      dep = dep + "\n" + '<script type="text/javascript" src="scripts/' + depend + '"></script>'
      dirName = os.path.join(directory,'scripts')
    if not os.path.exists(dirName):
      os.mkdir(dirName)
    shutil.copy(os.path.join(www,depend), dirName)

  html = html.replace('<!--scripts-->', dep)

  if data:
    if callable(data):
      data = data()
    html = html.replace('<!--json-->','<script type="application/json" id="data">' + json.dumps(data) + '</script>')
  index_path = os.path.join(directory, "index.html")
  con = open(index_path,"w")
  con.write(html)
  con.close()
  print("The graph has been generated in the '%s' folder." % directory)

def isnumeric(x):
  if type(x) is list:
    return all(map(lambda z : isnumeric(z),x))
  else:
    return isinstance(x, (int, float, complex)) and not isinstance(x, bool)

def getLanguageScript(obj):
  if hasattr(obj,'net'):
    obj = obj.net
  if type(obj) is dict and 'options' in obj:
    language = "en"
    if "language" in obj['options'] and obj['options']['language'] in ("es","ca"):
      language = obj['options']['language']
    return language + ".js"
  return None

def transpose(m):
  return [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]

