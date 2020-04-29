list = []
frase = ""
with open("1_5e.txt") as f:
	for l in f:
		if l not in list and len(l) > 2:
			if not l.strip(): # se c'è un  acapo
				print(frase)
				with open("out.txt", "a") as o:
					o.write(frase + "\n")

				frase = ""

			else:
				frase+=l
				list.append(l)
				#print(frase)
