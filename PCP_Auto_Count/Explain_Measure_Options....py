# Menu Option to show the input options help file in a web browser.
# Should only be run directly, nothing should happen if imported.
if __name__ == "__main__" or __name__ == "__builtin__":
	import webbrowser
	from java.lang.System import getProperty

	url = 'file:///' + str(getProperty('fiji.dir')).replace('\\', '/') + '/lib/pcp_auto_count/help/index.html'
	url = url.replace(' ','%20')

	webbrowser.open(url,new=2)
