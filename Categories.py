def addCategories(uD: dict[str,any]):
	
	def all(uDef: dict[str,any]):
		return True

	def mobile(uDef: dict[str,any]):
		return (uDef.get('speed') or 0) > 0

	def notmobile(uDef: dict[str,any]):
		return not mobile(uDef)

	def weapon(uDef: dict[str,any]):
		return uDef.get('weapondefs') is not None

	def noweapon(uDef: dict[str,any]):
		return uDef.get('weapondefs') is None

	def vtol(uDef: dict[str,any]):
		return uDef.get('canfly') is True

	def notair(uDef: dict[str,any]):
		return not vtol(uDef)

	hoverList = ['HOVER2','HOVER3','HHOVER4','AHOVER2']
	def hover(uDef: dict[str,any]):
		movementclass = uDef.get('movementclass') or ''
		maxwaterdepth = uDef.get('maxwaterdepth')
		return movementclass in hoverList and (maxwaterdepth is None or maxwaterdepth < 1)

	def nothover(uDef: dict[str,any]):
		return not hover(uDef)

	shipList = ['BOAT3','BOAT4','BOAT5','BOAT9','EPICSHIP']
	def ship(uDef: dict[str,any]):
		movementclass = uDef.get('movementclass') or ''
		maxwaterdepth = uDef.get('maxwaterdepth')
		return movementclass in shipList or (movementclass in hoverList and maxwaterdepth is not None and maxwaterdepth >= 1)

	def notship(uDef: dict[str,any]):
		return not ship(uDef)

	subList = ['UBOAT4','EPICSUBMARINE']
	def notsub(uDef: dict[str,any]):
		movementclass = uDef.get('movementclass') or ''
		return not movementclass in subList

	#can be underwater
	amphibList = ['VBOT6','COMMANDERBOT','SCAVCOMMANDERBOT','ATANK3','ABOT3','HABOT5','ABOTBOMB2','EPICBOT','EPICALLTERRAIN']
	def canbeuw(uDef: dict[str,any]):
		movementclass = uDef.get('movementclass') or ''
		cansubmerge = uDef.get('cansubmerge')
		return movementclass in amphibList or cansubmerge is True

	def underwater(uDef: dict[str,any]):
		minwaterdepth = uDef.get('minwaterdepth')
		waterline = uDef.get('waterline')
		speed = uDef.get('speed')
		return minwaterdepth is not None and ((waterline is None) or (waterline > minwaterdepth and speed is not None and speed > 0))

	def surface(uDef: dict[str,any]):
		return not (underwater(uDef) and mobile(uDef)) and not vtol(uDef)

	def mine(uDef: dict[str,any]):
		weapondefs = uDef.get('weapondefs') or {}
		minerange = weapondefs.get('minerange')
		return minerange is not None

	commanderList = ['COMMANDERBOT','SCAVCOMMANDERBOT']
	def commander(uDef: dict[str,any]):
		movementclass = uDef.get('movementclass') or ''
		return movementclass in commanderList

	def empable(uDef: dict[str,any]):
		customparams = uDef.get('customparams') or {}
		paralyzemultiplier = customparams.get('paralyzemultiplier') or 0
		return surface(uDef) and paralyzemultiplier != 0

	categories = {
		'ALL': all,
		'MOBILE': mobile,
		'NOTMOBILE': notmobile,
		'WEAPON': weapon,
		'NOWEAPON': noweapon,
		'VTOL': vtol,
		'NOTAIR': notair,
		'HOVER': hover,
		'NOTHOVER': nothover,
		'SHIP': ship,
		'NOTSHIP': notship,
		'NOTSUB': notsub,
		'CANBEUW': canbeuw,
		'UNDERWATER': underwater,
		'SURFACE': surface,
		'MINE': mine,
		'COMMANDER': commander,
		'EMPABLE': empable,
	}

	category = uD.get('category') or ""
	if category.find("OBJECT") == -1:
		exemptcategory = uD.get('exemptcategory')
		for categoryName, condition in categories.items():
			if exemptcategory is None or exemptcategory.find(categoryName):
				if condition(uD):
					category += f" {categoryName}"
	uD['category'] = category