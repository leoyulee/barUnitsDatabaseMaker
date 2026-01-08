import argparse
import pathlib
import shutil
import json
import subprocess
import sqlite3 as sql
import Categories
import fileinput
import sys

parser = argparse.ArgumentParser("simple_example")
parser.add_argument("barFolderPath", help="The path of your BAR development repo", type=pathlib.Path)
parser.add_argument("-r","--resetDB", help="If the tables within the database should be reset", default=False, action='store_true')

fileDir = pathlib.Path(__file__).parent

def getFiles(dir: pathlib.Path, output: dict[str,str]):
	if dir.is_dir():
		for child in dir.iterdir():
			getFiles(child, output)
	elif dir.is_file():
		# for line in fileinput.input(dir, inplace=True):
			# The 'inplace=True' argument redirects standard output back to the file itself.
			# The comma at the end of the print statement is often used to suppress extra newlines
			# as the 'line' variable already contains one.
			# sys.stdout.write(line.replace('Spring.GetModOptions().assistdronesbuildpowermultiplier', '1'))

		readModule = (fileDir/'luaToJsonOutput/readModule.lua').absolute()
		fileName = (dir.name).replace(".lua","")
		relPath = dir.relative_to(readModule, walk_up=True)
		luaPath = (str(relPath)).replace("..\\","").replace(".lua","")
		result = (subprocess.check_output(['lua', str(readModule), str(luaPath)]).decode("utf-8")).replace("\r\n","")
		if result != "None":
			try:
				newJson = json.loads(result)
				output[fileName] = newJson
			except Exception as e:
				print("Error",e,"\relPath:",relPath,"\nResult:",result)
				output[fileName] = {}
			#print(fileName, result)
			#print(dir)

FACTION_TABLE = 'Faction'
FACTION_MAPPINGS = [
	["arm","Armada"],
	["cor","Cortex"],
	["leg","Legion"],
	["raptor","Raptor"],
	["scav","Scavengers"],
	[None,"Other"]
]
def verifyFactionTable(sqlCon: sql.Connection, reset: bool):
	if reset:
		sqlCon.execute("DROP TABLE IF EXISTS Faction")
		sqlCon.commit()
	
	existCheck = sqlCon.execute(f"SELECT * FROM sqlite_master WHERE name = '{FACTION_TABLE}'")
	if existCheck.fetchone() is None:
		sqlCon.execute(f"CREATE TABLE {FACTION_TABLE} (factionID PRIMARY KEY,name)")
		sqlCon.commit()
	
	sqlCon.execute(f"DELETE FROM {FACTION_TABLE}")
	sqlCon.commit()
	sqlCon.executemany(f"INSERT INTO {FACTION_TABLE} (factionID,name) VALUES (?,?)", FACTION_MAPPINGS)
	sqlCon.commit()

UNIT_TABLE = 'Units'
def verifyUnitTable(sqlCon: sql.Connection, reset: bool):
	if reset:
		sqlCon.execute(f"DROP TABLE IF EXISTS {UNIT_TABLE}")
		sqlCon.commit()
	
	existCheck = sqlCon.execute(f"SELECT * FROM sqlite_master WHERE name = '{UNIT_TABLE}'")
	if existCheck.fetchone() is None:
		sqlCon.execute(f"CREATE TABLE {UNIT_TABLE} (unitID PRIMARY KEY,factionID,name,description,contents,energycost,energymake,energystorage,health,metalcost,metalmake,metalstorage,movementclass,radardistance,sightdistance,sonardistance,speed,turnrate,workertime)")
		sqlCon.commit()

BUILD_TABLE = 'UnitBuildOptions'
def verifyBuildTable(sqlCon: sql.Connection, reset: bool):
	if reset:
		sqlCon.execute(f"DROP TABLE IF EXISTS {BUILD_TABLE}")
		sqlCon.commit()
	
	existCheck = sqlCon.execute(f"SELECT * FROM sqlite_master WHERE name = '{BUILD_TABLE}'")
	if existCheck.fetchone() is None:
		sqlCon.execute(f"CREATE TABLE {BUILD_TABLE} (builderUnitID,optionUnitID)")
		sqlCon.commit()

CATEGORY_TABLE = 'UnitCategories'
def verifyCategoryTable(sqlCon: sql.Connection, reset: bool):
	if reset:
		sqlCon.execute(f"DROP TABLE IF EXISTS {CATEGORY_TABLE}")
		sqlCon.commit()
	
	existCheck = sqlCon.execute(f"SELECT * FROM sqlite_master WHERE name = '{CATEGORY_TABLE}'")
	if existCheck.fetchone() is None:
		sqlCon.execute(f"CREATE TABLE {CATEGORY_TABLE} (unitID,category)")
		sqlCon.commit()
	
def verifyDB(sqlCon: sql.Connection, reset: bool):
	verifyFactionTable(sqlCon,reset)
	verifyUnitTable(sqlCon,reset)
	verifyBuildTable(sqlCon,reset)
	verifyCategoryTable(sqlCon,reset)

def main():
	args = parser.parse_args()

	barFolderPath: pathlib.Path = args.barFolderPath

	enUnitsLocale = barFolderPath/'language/en/units.json'
	unitsJson:dict[str,dict[str,dict[str,str]]] = json.load(enUnitsLocale.open())
	names = unitsJson['units']['names']
	descriptions = unitsJson['units']['descriptions']

	origUnitFolder = barFolderPath/'units'

	cachePath = fileDir/'luaToJsonOutput/units'
	cacheUnitFolder = cachePath
	if cacheUnitFolder.exists():
		shutil.rmtree(cacheUnitFolder)
	cacheUnitFolder = origUnitFolder.copy(cachePath)
	
	contents: dict[str, dict[any,any]] = {}
	print("Copying units.lua")
	getFiles(cacheUnitFolder, contents)
	print(len(contents))

	print("Setting up sqlite unit table")
	with sql.connect('barUnits.sqlite3', isolation_level=None) as sqlCon:
		verifyDB(sqlCon, args.resetDB or False)

		insCount,upCount = 0,0
		for unitID,content in (contents.items()):
			name=names.get(unitID)
			desc=descriptions.get(unitID)

			existingUnitData = (sqlCon.execute(f"SELECT COUNT(*) FROM {UNIT_TABLE} WHERE unitID = ?",(unitID,))).fetchone() or (0,)
			if existingUnitData[0] == 0:
				insCount+=1
				sqlCon.execute(f"INSERT INTO {UNIT_TABLE} (unitID,name,description,contents) VALUES (?,?,?,?)",(unitID,name,desc,str(content),))
			else:
				upCount+=1
				sqlCon.execute(f"UPDATE {UNIT_TABLE} SET name=?,description=?,contents=? WHERE unitID = ?",(name,desc,str(content),unitID,))
				
			sqlCon.commit()

			#Add Other Properties to Unit
			sqlCon.execute(f"""
				UPDATE {UNIT_TABLE} SET
					energycost=?,
					energymake=?,
					energystorage=?,
					health=?,
					metalcost=?,
					metalmake=?,
					metalstorage=?,
					movementclass=?,
					radardistance=?,
					sightdistance=?,
					sonardistance=?,
					speed=?,
					turnrate=?,
					workertime=?
				WHERE unitID = ?
			""",(
				content.get('energycost',0),
				content.get('energymake',0),
				content.get('energystorage',0),
				content.get('health',0),
				content.get('metalcost',0),
				content.get('metalmake',0),
				content.get('metalstorage',0),
				content.get('movementclass'),
				content.get('radardistance',0),
				content.get('sightdistance',0),
				content.get('sonardistance',0),
				content.get('speed',0),
				content.get('turnrate',0),
				content.get('workertime',0),
				unitID,
			))
			sqlCon.commit()
			
			#Add factionIDs to UNIT_TABLE
			factionIDs = (sqlCon.execute(f"SELECT factionID FROM {FACTION_TABLE}")).fetchall() or []
			for factionRes in factionIDs:
				factionID = factionRes[0]
				if factionID is not None and unitID.startswith(factionID):
					sqlCon.execute(f"UPDATE {UNIT_TABLE} SET factionID=? WHERE unitID = ?",(factionID,unitID,))
					sqlCon.commit()
					break
			
			#Add unitIDs to BUILD_TABLE
			buildoptions = content.get("buildoptions") or []
			for optionUnitID in buildoptions:
				existingBuildOptionData = sqlCon.execute(f"SELECT COUNT(*) FROM {BUILD_TABLE} WHERE builderUnitID = ? AND optionUnitID = ?", (unitID, optionUnitID,)).fetchone() or (0,)
				if existingBuildOptionData[0] == 0:
					sqlCon.execute(f"INSERT INTO {BUILD_TABLE} (builderUnitID, optionUnitID) VALUES (?,?)", (unitID, optionUnitID,))
					sqlCon.commit()
			
			#Assign automatic categories from game logic "\Beyond-All-Reason\gamedata\alldefs_post.lua"
			Categories.addCategories(content)
			categories = content.get("category").split()
			for category in categories:
				existingCategoryData = sqlCon.execute(f"SELECT COUNT(*) FROM {CATEGORY_TABLE} WHERE unitID = ? AND category = ?", (unitID, category,)).fetchone() or (0,)
				if existingCategoryData[0] == 0:
					sqlCon.execute(f"INSERT INTO {CATEGORY_TABLE} (unitID, category) VALUES (?,?)", (unitID, category,))
					sqlCon.commit()
		
		print(f"insCount: {insCount}\nupCount: {upCount}")
		print(sqlCon.execute(f"SELECT COALESCE(f.name, 'Other'), COUNT(*) FROM {UNIT_TABLE} u LEFT JOIN Faction f ON f.factionID = u.factionID GROUP BY u.factionID").fetchall())


if __name__=="__main__":
	main()