#parsing fpga_netlist to eqn
#file created 31st March 2016
#file updated 13th April 2016

import re
from itertools import cycle

file = raw_input("Enter file name: ")
if (len(file) < 1): file = 'Multiplier16Bits.vo'
outfile = file.split('.')[0]+'.e'
file_handle = open(file,'r')
f_h = open(outfile,'w')

#extracting equations in readable form

for line in file_handle:
 if line.startswith('// Equation(s):'):
   strtemp = next(file_handle)
   string = ""
   while (strtemp.startswith("//")):
    strtemp = strtemp.lstrip("\/")
    string = string + strtemp.rstrip("\n")
    strtemp = next(file_handle)
   string = string+"\n" 
   if "\~QUARTUS_CREATED_GND~I_combout" not in string:
    string=string.lstrip("\/")
    string=string.replace("\\","")
    strlist = string.split('=')
    strlist[0]=re.sub('[~|_]combout',"",strlist[0])
    strlist[0]=strlist[0].strip()
    strlist[1]=re.sub('~input\S+',"",strlist[1])
    strlist[1]=re.sub('[~|_]combout',"",strlist[1])
    strlist[1]=strlist[1].replace(" ","")
    expr = strlist[0]+'='+strlist[1]
    f_h.write(expr)
    #f_ha.write(string)
f_h.close()
file_handle.close()
#f_ha.close()

file_handle = open(outfile,'r')
eqnfile = file.split('.')[0]+'.eqn'
f_h = open(eqnfile,'w')
 
#parsing
f_eqs = list()
loeq = list()
for line in file_handle:
 print line.split("=")
 eq = line.split("=")[1]
 equation = list()
 final_eq = list()
 operand=""

 eqlist = list(eq) #getting list of characters
 iter_eq = iter(list(eq))
 for letter in iter_eq:
  #print letter
  if letter in ['(','$','#','!','&',')']:
    if len(operand) > 0:
     equation.append(operand)
     operand = ""
    equation.append(letter)
  else:
    operand = operand+letter
    try:
     nextelem = iter_eq.next()
    except:
     nextelem = '\n'
    #print "nextelem ="+nextelem
    if nextelem in ['(','$','#','!','&',')','\n']:
      equation.append(operand)
      if nextelem in ['(','$','#','!','&',')']:
       equation.append(nextelem)
      #print "operand="+operand
      operand=""
    else:
      operand = operand + nextelem
 print equation
 equation.remove('\n')
 loeq.append(equation)
 for i in equation:
  if i == ')':
   templist = list()
   templist.append(i)
   flag=True
   while (flag):
    if (len(final_eq) != 0):
     elem = final_eq.pop()
    else:
     break   
    if elem == '!':
     notelem = templist.pop()
     notelem = "(1 - "+notelem +")"
     templist.append(notelem)
    else: 
     templist.append(elem)
    if elem == '(':
     flag=False
   templist.reverse()
   #crosscheck size of templist should be 3 or 5
   if (len(templist) == 3):
    exp = templist[0]+templist[1]+templist[2]
    final_eq.append(exp)
   elif (len(templist) == 5):
    if templist[2] == '&':
     exp = templist[0]+templist[1]+" * "+templist[3]+templist[4]
     final_eq.append(exp)
    elif templist[2] == '$':
     exp = templist[0]+templist[1]+" + "+templist[3]+" - 2 * "+templist[1]+" * "+templist[3]+templist[4]
     final_eq.append(exp)
    elif templist[2] == '#':
     exp = templist[0]+templist[1]+" + "+templist[3]+" - "+templist[1]+" * "+templist[3]+templist[4]
     final_eq.append(exp)
  else:    
   final_eq.append(i)
 while (len(final_eq) > 1): #parsing till the first element of list
  #get 3 elements and parse
  templist = list()
  while (len(templist) < 3):
   if (len(final_eq) != 0):
    elem = final_eq.pop()
   else:
    break
   if elem == '!':
    notelem = templist.pop()
    notelem = "(1 - "+notelem +")"
    templist.append(notelem)
   else: 
    templist.append(elem)
  templist.reverse()
  if templist[1] == '&':
   exp = "("+templist[0]+" * "+templist[2]+")"
   final_eq.append(exp)
  elif templist[1] == '$':
   exp = "("+templist[0]+" + "+templist[2]+" - 2 * "+templist[0]+" * "+templist[2]+")"
   final_eq.append(exp)
  elif templist[1] == '#':
   exp = "("+templist[0]+" + "+templist[2]+" - "+templist[0]+" * "+templist[2]+")"
   final_eq.append(exp)
 f_eqs.append(line.split("=")[0]+" = "+final_eq[0]+"\n") 
f_eqs.reverse()
for ele in f_eqs:
 f_h.write(ele)
f_h.write("#output\n")
#f_h.write(output)
#f_h.close()
file_handle.close()

# getting primary outputs

file_handle = open(outfile,'r')
left_var = list()
primary_outputs = list()
for line in file_handle:
 left_var.append(line.split("=")[0])
 
for var in left_var:
 flag = 0
 for eq in loeq:
  if (var in eq):
   flag = 1
   break
 if flag == 0:
  primary_outputs.append(var) 
output = primary_outputs[0]+"*2^0"
iter_PO = iter(primary_outputs)
next(iter_PO)
i = 1
for PO in iter_PO:
 output = output + " + " + PO + "*2^" + str(i)
 i = i+1

f_h.write(output+"\n")
file_handle.close()
f_h.close()
