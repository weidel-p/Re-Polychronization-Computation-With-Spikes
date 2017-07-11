import yaml
import sys
import os

def depth(d, level=0):
    if not isinstance(d, dict) or not d:
        return level
    return max(depth(d[k], level + 1) for k in d)

def escape(s):
    s = str(s).replace("_", "\_")
    s = s.replace("{", "\{")
    s = s.replace("}", "\}")
    return s

def begin_table():
    return """\\begin{table*}
              \\setlength{\\columnwidthleft}{0.2\\textwidth}
              \\setlength{\\columnwidthmiddle}{0.18\\textwidth}
              """

def add_section(title, label):
    return """\\begin{tabularx}{\\fullfigwidth}{|p{\\columnwidthleft}|X|}
              \\hline\\modelhdr{2}{"""+escape(label)+"""}{"""+escape(title)+"""}\\\\\\hline
              """

def add_line(key, value):
    return escape(key) + """ & """ + escape(value) + """ \\\\
           \\hline
           """ 

def end_section():
    return """\\end{tabularx}  \\\\
           """

def end_table(caption, label):
    return """\caption{
                """ + escape(caption) + """.
                \label{tab:nordlie-""" + escape(label).replace("\\_", "-") + """}
              }
              \end{table*}
              """
    
labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
folder="../NEST_model/experiments"
fns = os.listdir(folder)
for fn in fns:
    if fn.endswith("yaml"):
        
        with open(os.path.join(folder,fn), "r+") as f:
            cfg = yaml.load(f)


        sections = cfg.keys()
        
        table = begin_table()

        labelcounter = 0
        
        for i, sec in enumerate(sections):
        
            if depth(cfg[sec]) > 1:
                subsections = cfg[sec].keys()
                
                #table += add_section(sec, "")
        
                for j, subsec in enumerate(subsections):
                    if depth(cfg[sec][subsec]) > 1:
                        print "error: too deep config file"
                        exit()
                    else:
                        table += add_section(subsec, labels[labelcounter])
                        labelcounter += 1
                
                        for l in zip(cfg[sec][subsec].keys(), cfg[sec][subsec].values()):
                            table += add_line(l[0], l[1])
                
                        table += end_section()
            else:
                table += add_section(sec, labels[labelcounter])
                labelcounter += 1
        
                for l in zip(cfg[sec].keys(), cfg[sec].values()):
                    table += add_line(l[0], l[1])
        
                table += end_section()
        
        
        
        table += end_table("Parameter for experiment " + fn, fn)
        
        print table


