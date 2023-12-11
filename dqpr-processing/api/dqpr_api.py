import requests
import json
from datetime import date
from datetime import datetime

class DQPR_API:
	"""DQPR API Wrapper Class"""
	non_rejected_status_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
	all_status_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,9999]
	open_waiting_in_prog_status_list = [1,2,4,8,9,10,11,12,13,14,15]
	def __init__(self, settings):
		self.BASE_URL = settings["BASE_URL"]
		self.USER = settings["USER"]

	def make_request(self, rel_url, method="GET", data=None):
		url = "{}{}".format(self.BASE_URL, rel_url)
		print("CALLING: {}".format(url))
		if method == "GET":
			r = requests.get(url)
			return r.json()
		if method == "POST":
			data["userName"] = self.USER
			print(json.dumps(data))
			r = requests.post(url, json=data)
			return r.json()

	def get_last_year_for_list(self, key, resource, critera_name, status_list=None, url_override=None):
		items_url = url_override or "dq/{}/list".format(resource)
		items = self.make_request(items_url)
		item_set = set([item[key] for item in items])
		results = {}
		print("Fetching result set for {} {}s".format(len(items), resource))
		criteria = {}
		for set_item in item_set:
			criteria[critera_name] = set_item
			result_set = self.get_last_year(extra_criteria = criteria, status_list = status_list)
			results[set_item] = result_set
		return results

	def get_last_year_and_open_for_site_list(self):
		results = self.get_last_year_for_list("siteCode", "site", "site", status_list=self.open_waiting_in_prog_status_list)
		return results

	def get_last_year_and_open_for_instrument_list(self):
		results = self.get_last_year_for_list("instrumentClass", "instrument", "instrument", status_list=self.open_waiting_in_prog_status_list)
		return results

	def get_last_year_for_site_list(self):
		results = self.get_last_year_for_list("siteCode", "site", "site")
		return results

	def get_last_year_for_instrument_list(self):
		results = self.get_last_year_for_list("instrumentClass", "instrument", "instrument")
		return results

	def get_last_year_group_by_submitter(self):
		results = self.get_last_year_for_list("personId", "person", "person_ids", status_list=self.all_status_list, url_override="dq/dqpr/authors")
		return results

	def get_last_year_for_submitter(self, submitter):
		criteria = {
			"person_id": submitter
		}
		results = self.get_last_year(extra_criteria=criteria)
		return results

	def get_last_year(self, extra_criteria=None, status_list=None):
		status_list = status_list or self.non_rejected_status_list
		first_of_current_year = date(date.today().year, 1, 1)
		first_of_current_year_as_epoch = self.convert_datetime_time_from_epoch(datetime.combine(first_of_current_year, datetime.min.time()))
		criteria = {
				"start_date": first_of_current_year_as_epoch,
				"status": ",".join(["{}".format(status) for status in status_list])
			}
		if extra_criteria:
			criteria.update(extra_criteria)
		results = self.search_dqprs(criteria)
		return results

	def search_dqprs(self, criteria):
		print(criteria)
		criteria_list = ["{}={}".format(name, value) for (name, value) in criteria.items()]
		url = "dq/dqpr/search?{}".format("&".join(criteria_list))
		print(url)
		results = self.make_request(url)
		return results

	def create_new_dqpr(self, person_id, dqpr_qa_reason, dqpr_status, instrument, prob_desc, qa_code, dqpr_start_date=None, dqpr_end_date=None):
		request_data = {
			"personId": person_id,
			"dqprQaReason": ",".join(["{}".format(reason) for reason in dqpr_qa_reason]),
			"dqprStatus": dqpr_status,
			"instrument": ":".join(["{}".format(loc_part) for loc_part in instrument]),
			"probDesc": prob_desc,
			"qaCode": qa_code,
		}
		if dqpr_start_date:
			request_data["dqprStartDate"] = dqpr_start_date
		if dqpr_end_date:
			request_data["dqprEndDate"] = dqpr_end_date
		return self.make_request("dq/dqpr/create", method="POST", data=request_data)

	def get_audit_history(self, dqpr_no):
		return self.make_request("dq/comment/audit/{}".format(dqpr_no))

	def get_maint_history(self, dqpr_no):
		return self.make_request("dq/comment/maint/{}".format(dqpr_no))

	def get_comment_history(self, dqpr_no):
		return self.make_request("dq/comment/user/{}".format(dqpr_no))

	def convert_datetime_time_from_epoch(self, d):
		epoch = datetime.utcfromtimestamp(0)
		return ('%f' % ((d - epoch).total_seconds() * 1000)).split(".")[0]
