import pytest
import mongoengine
from iec_lookup.utils import get_test_db, get_real_test_db_connection
from iec_lookup.models import ImporterExporterCodeDetails, Director, Branch, RegistrationDetails, RegistrationCumMembershipCertificateDetails, ImporterExporterCodeToBeRetrieved
from django.conf import settings
from bs4 import BeautifulSoup, NavigableString, Tag
import logging


@pytest.fixture(scope='class')#class, module, session, function
def mongo_test_db_setup(request):
	"""
	Fixture for setting mongo test db which can be included in test methods
	eliminates need to write setup and teardown methods for db
	"""
	logging.debug("Creating a test database and getting connection...")
	test_db = get_real_test_db_connection()
	yield test_db
	document_id = None
	logging.debug("Dropping a test database ...")
	test_db.drop_database(settings._MONGODB_NAME)
	logging.debug("Closing db connection ...")
	test_db.close()


@pytest.fixture(scope='function')#class, module, session, function
def importer_exporter_code_details_as_json():

	iec_json_data = {
	  # "id": "592800c1482d4273b3a51072",
	  "importer_exporter_code": "1198002743",
	  "importer_exporter_code_allotment_date": "27.10.1998",
	  "file_number": "11/04/130/00274/AM99/",
	  "file_date": "27.10.1998",
	  "party_name": "CAP & SEAL (INDORE) PVT.LTD.,",
	  "party_address": "PLOT NO.5, FLAT NO.302, 3RD FLOOR, SHREE BALAJI HEIGHTS, RAJGARH KOTHI, MANORAMAGANJ, INDORE, M.P., PIN-452001",
	  "phone_number": "0731-470346, 285400",
	  "email": "capandseal@capandseal.com",
	  "exporter_type": "2 Manufacturer Exporter",
	  "importer_exporter_code_status": "Valid IEC",
	  "date_of_establishment": "25.12.1986",
	  "bin_pan_extension": "AABCC4531E FT001",
	  "pan_issue_date": "",
	  "pan_issued_by": "CCIT, BHOPAL",
	  "nature_of_concern": "3  Private Limited",
	  "bank_name_and_location": "STATE BANK OF INDORE, PITHAMPUR BRANCH, PITHAMPUR, DIST.DHAR.",
	  "account_type": "1 CA",
	  "account_number": "CC 52",
	  "is_active": True,
	  "is_deleted": False,
	  "directors": [
	    {
	      "name": "SHRI NISHITH CHOUDAHARY",
	      "fathers_name": "SHRI SAMPAT SINGH CHOUDHARY",
	      "address": "H-1, RATLAM KOTHI, INDORE, M.P., PIN-0",
	      "phone_email": "519847"
	    },
	    {
	      "name": "SMT.NEETA CHOUDHARY",
	      "fathers_name": "W/O SHRI NISHITH CHOUDHARY",
	      "address": "H-1, RATLAM KOTHI, INDORE, M.P., PIN-0",
	      "phone_email": "519847"
	    }
	  ],
	  "branches": [
	    {
	      "branch_code": 1,
	      "address": "PLOT NO.184, ROAD NO.8, SECTOR-1, PITHAMPUR, DIST. DHAR, M.P., PIN-454775"
	    }
	  ],
	  "registration_details": [
	    {
	      "registration_type": 1,
	      "registration_number": "10/11/03502/PMT/SSI",
	      "issue_date": "12.03.1987",
	      "registered_with": "GM(DIC), DHAR"
	    }
	  ],
	  "rcmc_details": [
	    {
	      "rcmc_id": 0,
	      "rcmc_number": "FIEO/WR/A-2553/99-2000",
	      "issue_date": "01.04.2001",
	      "expiry": "31.03.2002",
	      "issued_by": "ASSTT.DIRECTOR(FIEO)"
	    }
	  ]
	}

	return iec_json_data

@pytest.fixture(scope='function')#class, module, session, function
def basic_iec_details_as_object():
	iec_json_data = importer_exporter_code_details_as_json()

	basic_importer_exporter_code_details = ImporterExporterCodeDetails(importer_exporter_code = iec_json_data['importer_exporter_code'],
			importer_exporter_code_allotment_date = iec_json_data['importer_exporter_code_allotment_date'],
			file_number = iec_json_data['file_number'],
			file_date = iec_json_data['file_date'], 
			party_name = iec_json_data['party_name'],
			party_address = iec_json_data['party_address'],
			phone_number = iec_json_data['phone_number'], 
			email = iec_json_data['email'],
			exporter_type = iec_json_data['exporter_type'], 
			importer_exporter_code_status = iec_json_data['importer_exporter_code_status'],
			date_of_establishment = iec_json_data['date_of_establishment'], 
			bin_pan_extension = iec_json_data['bin_pan_extension'],
			pan_issue_date = iec_json_data['pan_issue_date'], 
			pan_issued_by = iec_json_data['pan_issued_by'],
			nature_of_concern = iec_json_data['nature_of_concern'], 
			bank_name_and_location = iec_json_data['bank_name_and_location'],
			account_type = iec_json_data['account_type'],
			account_number = iec_json_data['account_number'],
			is_active= iec_json_data['is_active'],
			is_deleted= iec_json_data['is_deleted']
			)
	return basic_importer_exporter_code_details

@pytest.fixture(scope='function')#class, module, session, function
def importer_exporter_code_details_as_object():
	iec_json_data = importer_exporter_code_details_as_json()
	importer_exporter_code_details = basic_iec_details_as_object()

	directors_list = []
	branches_list = []
	registration_details_list = []
	rcmc_details_list = []

	for each_director in iec_json_data["directors"]:
		new_director = Director(name= each_director['name'], fathers_name= each_director['fathers_name'],
				address = each_director['address'],
				phone_email = each_director['phone_email'])

		directors_list.append(new_director) 

	for each_branch_data in iec_json_data["branches"]:
		new_branch = Branch(branch_code= each_branch_data['branch_code'], address = each_branch_data['address'])

		branches_list.append(new_branch)

	for each_registration_detail_data in iec_json_data["registration_details"]:
		new_registration_details = RegistrationDetails(registration_type= each_registration_detail_data['registration_type'],
				registration_number = each_registration_detail_data['registration_number'], 
				issue_date = each_registration_detail_data['issue_date'], 
				registered_with = each_registration_detail_data['registered_with'])

		registration_details_list.append(new_registration_details)

	for each_rcmc_detail_data in iec_json_data["rcmc_details"]:
		new_rcmc_details = RegistrationCumMembershipCertificateDetails(rcmc_id= each_rcmc_detail_data['rcmc_id'], rcmc_number = each_rcmc_detail_data['rcmc_number'], 
				issue_date = each_rcmc_detail_data['issue_date'] , expiry = each_rcmc_detail_data['expiry'],
				issued_by = each_rcmc_detail_data['issued_by'])

		rcmc_details_list.append(new_rcmc_details)

	importer_exporter_code_details.directors= directors_list
	importer_exporter_code_details.branches= branches_list
	importer_exporter_code_details.registration_details= registration_details_list
	importer_exporter_code_details.rcmc_details= rcmc_details_list
	return importer_exporter_code_details


@pytest.fixture(scope='function')#class, module, session, function
def dgft_error_response_html_string():
	dgft_error_response = """
		<html><head>
		<title>IEC</title></head>

		<body>
		The name Given By you does not match with the data OR you have entered less than three letters 

		</body>
		</html>
		"""
	return dgft_error_response

@pytest.fixture(scope='function')#class, module, session, function
def dgft_succes_response_html_string():

	dgft_success_response = """
		<html><head>
	<title>IEC</title></head>

	<body>
	<FORM ACTION=""METHOD=GET>
	<H2 ALIGN="CENTER" >Importer Exporter Code</H2>

	</FORM> 
	<TABLE BORDER=0>
	<TR><TH VALIGN= TOP ALIGN=LEFT COLSPAN=50></TH><TH VALIGN= TOP ALIGN=LEFT COLSPAN=3></TH><TH VALIGN= TOP ALIGN=LEFT COLSPAN=50></TH></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>IEC</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>1198002743</TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>IEC Allotment Date</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>27.10.1998</TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>File Number</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>11/04/130/00274/AM99/    </TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>File Date</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>27.10.1998</TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>IEC</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>1198002743</TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>Party Name and Address</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>CAP & SEAL (INDORE) PVT.LTD.,                     <BR>PLOT NO.5, FLAT NO.302, 3RD FLOOR, <BR>SHREE BALAJI HEIGHTS, RAJGARH KOTHI<BR>MANORAMAGANJ, INDORE, M.P.         <BR>PIN-452001<BR></TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>Phone No</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>0731-470346, 285400                                                   </TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>e_mail</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>capandseal@capandseal.com                                             </TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>Exporter Type</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>2 Manufacturer Exporter                                        </TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>IEC Status</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50><b>Valid IEC</b></TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>Date of Establishment</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>25.12.1986</TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>BIN (PAN+Extension)</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>AABCC4531E FT001</TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>PAN ISSUE DATE</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50></TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>PAN ISSUED BY</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>CCIT, BHOPAL        </TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>Nature Of Concern</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>3  Private Limited                                              </TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>Banker Detail</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=3>:</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>STATE BANK OF INDORE, PITHAMPUR BRANCH, PITHAMPUR, DIST.DHAR.         <BR>A/C Type:1 CA                  <BR>A/C No  :CC 52               <BR></TD></TR>


	</TABLE> 
	<BR> 
	<BR> 
	<B>Directors:</B> 
	<BR> 
	<TABLE BORDER=1>
	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>1.</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=100>SHRI NISHITH CHOUDAHARY                           <BR>SHRI SAMPAT SINGH CHOUDHARY                       <BR>H-1, RATLAM KOTHI,                 <BR>                                   <BR>INDORE, M.P.                       <BR>PIN-0<BR>Phone/Email:519847                             </TD></TR>

	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>2.</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=100>SMT.NEETA CHOUDHARY                               <BR>W/O SHRI NISHITH CHOUDHARY                        <BR>H-1, RATLAM KOTHI,                 <BR>                                   <BR>INDORE, M.P.                       <BR>PIN-0<BR>Phone/Email:519847                             </TD></TR>


	</TABLE> 
	<BR> 
	<BR> 
	<B>Branches:</B> 
	<BR> 
	<TABLE BORDER=1>
	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>1.</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=100>Branch Code:1<BR>PLOT NO.184, ROAD NO.8,            <BR>SECTOR-1, PITHAMPUR,               <BR>DIST. DHAR, M.P.                   <BR>PIN-454775</TD></TR>


	</TABLE> 
	<BR> 
	<BR> 
	<B>Registration Details:</B> 
	<BR> 
	<TABLE BORDER=1>
	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>1.</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=100>Registration Type:1<BR>No:10/11/03502/PMT/SSI <BR>Date:12.03.1987<BR>Registered WithGM(DIC), DHAR       </TD></TR>


	</TABLE> 
	<BR> 
	<BR> 
	<B>RCMC Details:</B> 
	<BR> 
	<TABLE BORDER=1>
	<TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>1.</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=100>0<BR>FIEO/WR/A-2553/99-2000             <BR>Issue Dt:01.04.2001<BR>Expiry:31.03.2002<BR>Issued By:ASSTT.DIRECTOR(FIEO)               </TD></TR>


	</TABLE> 
	<BR> 
	<BR> 
	<BR> 
	<PRE><B>Place:                                     (Name and Signature with Seal)</B></PRE> 
	<BR> 
	Date: 

	</body>
	</html>

	"""

	return dgft_success_response

@pytest.fixture(scope='function')#class, module, session, function
def iec_table_section_list():

	dgft_success_response_html_string = dgft_succes_response_html_string()

	dgft_site_response_soup = BeautifulSoup(dgft_success_response_html_string, "html.parser")
	iec_tables = dgft_site_response_soup.find_all("table")
	return iec_tables

@pytest.fixture(scope='function')#class, module, session, function
def dgft_error_message():

	dgft_error_html_string = dgft_error_response_html_string()

	dgft_site_error_response_soup = BeautifulSoup(dgft_error_html_string, "html.parser")
	dgft_site_error_message = str(dgft_site_error_response_soup.find("body").text)
	return dgft_site_error_message






