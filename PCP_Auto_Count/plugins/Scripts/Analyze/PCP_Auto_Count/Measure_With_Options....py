# Menu Option to show the Input Options dialog, then run PCP Auto Count.
# Should only be run directly, nothing should happen if imported.
if __name__ == "__main__" or __name__ == "__builtin__":
	from pcp_auto_count import measure	
	measure.main(False)
