import sys
from datetime import datetime, timedelta
from TSHRevDefs import enterpriseSelection, getResourceIds, getUtcOffsetTimes, addResourceBlock, showMenu

credentials = enterpriseSelection()

showMenu(credentials)

sys.exit(0)
