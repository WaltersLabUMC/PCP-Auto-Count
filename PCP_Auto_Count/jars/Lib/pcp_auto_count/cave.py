# Represents a (possible) cave within a chunk.
from pcp_auto_count.entity import Entity
class Cave(Entity):

	@staticmethod
	def getEntityType():
		return "cave"
		
# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
