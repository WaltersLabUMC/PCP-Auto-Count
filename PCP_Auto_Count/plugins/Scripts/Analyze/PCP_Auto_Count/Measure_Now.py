# Menu Options to immediately run PCP Auto Count using the most recently used (or otherwise default) settings.
# Should only be run directly, nothing should happen if imported.
if __name__ == "__main__" or __name__ == "__builtin__":
        from pcp_auto_count import measure
	measure.main(True)
