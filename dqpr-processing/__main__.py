from api.dqpr_api import DQPR_API
from config.settings import SETTINGS

def main():
   '''Example program to utilize the DQPR API
   Author: Ben Newland
   '''
	dqpr_api = DQPR_API(SETTINGS)
	result_set = dqpr_api.get_last_year()
	print(result_set)
	result = dqpr_api.create_new_dqpr(18944, [5000], 1, ["sgp","f1","ccn-air"], "test", 1)
	print(result)
	history = dqpr_api.get_audit_history(7872)
	print(history)
	comments = dqpr_api.get_comment_history(7872)
	print(comments)
	maint = dqpr_api.get_maint_history(7872)
	print(maint)

if __name__ == "__main__":
    main()
